"""
Argos — Auto Discovery
Uses Groq LLM to intelligently find all company sources given a name/website.
"""

import json
import logging

import requests

from app.llm import get_groq_llm, llm_invoke

logger = logging.getLogger(__name__)


class AutoDiscoverer:
    """LLM-powered company source discovery."""

    def discover(self, company_name: str, website: str = None) -> dict:
        """
        Use Groq LLM to find all relevant sources for a company.
        Returns a dict with discovered fields.
        """
        website_info = f"\n  Website: {website}" if website else ""

        prompt = f"""You are a research assistant. Given a company name, return a JSON object with these fields (null if unknown):
{{
    "github_org": "org name on github.com",
    "careers_url": "direct URL to careers/jobs page",
    "producthunt_slug": "slug on producthunt.com",
    "linkedin_url": "full linkedin.com/company/... URL",
    "changelog_url": "URL to changelog or blog",
    "news_keywords": ["keyword1", "keyword2", "keyword3"]
}}

CRITICAL KEYWORD RULES:
- DO NOT use generic terms (e.g. "AI", "Artificial Intelligence", "Machine Learning", "Deep Learning", "Generative AI", "LLM").
- ONLY include highly specific branded terms (e.g. the company name itself, major product names, or founder names).

Company: {company_name}{website_info}

Return ONLY valid JSON, no explanation. Be accurate — only include sources you are confident exist."""

        result = {
            "github_org": None,
            "careers_url": None,
            "reddit_sub": None, # Kept for schema compatibility, set to None
            "producthunt_slug": None,
            "linkedin_url": None,
            "changelog_url": None,
            "news_keywords": [company_name],
        }

        try:
            llm = get_groq_llm()
            response = llm_invoke(llm, prompt)

            # Parse JSON response
            parsed = self._parse_json(response)
            if parsed:
                # Merge parsed values (keep defaults for None)
                for key in result:
                    if key in parsed and parsed[key] is not None:
                        result[key] = parsed[key]

                # Filter out generic keywords and ensure company name is present
                keywords = result.get("news_keywords") or []
                
                BANNED_KEYWORDS = {
                    "ai", "artificial intelligence", "machine learning",
                    "deep learning", "generative ai", "llm",
                    "large language model", "neural network"
                }
                
                filtered_keywords = []
                for k in keywords:
                    if k.strip().lower() not in BANNED_KEYWORDS:
                        filtered_keywords.append(k)
                    else:
                        logger.info(f"AutoDiscoverer: Rejected generic keyword '{k}' for {company_name}")
                        
                if company_name not in filtered_keywords:
                    filtered_keywords.insert(0, company_name)
                    
                result["news_keywords"] = filtered_keywords

            logger.info(f"Discovered sources for {company_name}: {result}")

        except Exception as e:
            logger.error(f"Auto-discovery failed for {company_name}: {e}")

        # ── Validate GitHub org ─────────────────────────────
        if result.get("github_org"):
            result["github_org"] = self._validate_github_org(result["github_org"])

        return result

    def _validate_github_org(self, org: str) -> str | None:
        """Verify GitHub org exists with a HEAD request."""
        if not org:
            return None

        try:
            url = f"https://api.github.com/orgs/{org}"
            resp = requests.head(url, timeout=10)
            if resp.status_code == 200:
                return org

            # Try as user
            url = f"https://api.github.com/users/{org}"
            resp = requests.head(url, timeout=10)
            if resp.status_code == 200:
                return org

            logger.warning(f"GitHub org/user '{org}' not found — setting to null")
            return None
        except requests.RequestException:
            return org  # Network error, keep the value

    def _parse_json(self, text: str) -> dict | None:
        """Extract JSON from LLM response."""
        # Direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Find JSON in code block
        import re
        match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # Find JSON object
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        return None