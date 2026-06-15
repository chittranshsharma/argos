"""
Argos — LinkedIn Agent
Scrapes public LinkedIn company pages for recent posts.
Uses Playwright — gracefully handles login walls.
"""

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class LinkedInAgent:
    """Scrapes public LinkedIn company pages for recent posts and announcements."""

    def collect(self, linkedin_url: str, company_name: str, company_id: str) -> list[dict]:
        """
        Attempt to scrape a public LinkedIn company page for posts.
        If the page requires login, returns empty list gracefully.
        """
        if not linkedin_url:
            return []

        signals = []

        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                page.set_default_timeout(20000)

                try:
                    # Navigate to company page posts
                    posts_url = linkedin_url.rstrip("/") + "/posts/"
                    page.goto(posts_url, wait_until="domcontentloaded")
                    page.wait_for_timeout(3000)

                    # Check if we're redirected to login
                    current_url = page.url
                    if "login" in current_url or "authwall" in current_url:
                        logger.info(f"LinkedIn requires login for {linkedin_url} — skipping")
                        browser.close()
                        return []

                    # Try to extract post content
                    content = page.content()

                    # Look for post containers
                    posts = page.query_selector_all("[data-urn]")
                    if not posts:
                        posts = page.query_selector_all(".feed-shared-update-v2")
                    if not posts:
                        posts = page.query_selector_all("article")

                    for i, post_el in enumerate(posts[:10]):
                        try:
                            text = post_el.inner_text()
                            if not text or len(text.strip()) < 20:
                                continue

                            # Clean text
                            lines = [l.strip() for l in text.split("\n") if l.strip()]
                            title = lines[0][:200] if lines else "LinkedIn Post"
                            post_content = " ".join(lines[:5])[:500]

                            # Determine if it's an announcement
                            announcement_keywords = [
                                "announce", "launch", "introducing", "excited",
                                "proud", "milestone", "partnership", "joining"
                            ]
                            is_announcement = any(kw in post_content.lower() for kw in announcement_keywords)

                            signals.append({
                                "company_id": company_id,
                                "company_name": company_name,
                                "source": "linkedin",
                                "signal_type": "announcement" if is_announcement else "post",
                                "title": title,
                                "content": post_content,
                                "url": linkedin_url,
                                "raw_data": {
                                    "post_index": i,
                                    "is_announcement": is_announcement,
                                },
                                "importance": "high" if is_announcement else "medium",
                            })
                        except Exception as e:
                            logger.debug(f"Error extracting LinkedIn post: {e}")
                            continue

                except Exception as e:
                    logger.warning(f"LinkedIn page load error for {linkedin_url}: {e}")

                browser.close()

        except ImportError:
            logger.error("Playwright not installed — skipping LinkedInAgent")
        except Exception as e:
            logger.error(f"LinkedInAgent error for {linkedin_url}: {e}")

        logger.info(f"LinkedInAgent collected {len(signals)} signals for {company_name}")
        return signals