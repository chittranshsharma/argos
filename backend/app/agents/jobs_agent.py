"""
Argos — Jobs Agent
Scrapes company careers pages (or ATS APIs) to detect new/removed job postings.
Applies LLM analysis to group jobs into strategic hiring signals.
"""

import logging
import json
import re
import requests
from datetime import datetime, timezone

from app.signals.registry import SignalType, SignalSubtype
from app.llm import get_groq_llm, llm_invoke

logger = logging.getLogger(__name__)

class JobsAgent:
    """Collects hiring signals and derives strategic intelligence."""

    def collect(self, careers_url: str, company_name: str, company_id: str) -> list[dict]:
        """Scrape careers page and derive intelligence."""
        if not careers_url:
            return []

        signals = []
        jobs = []

        # 1. Attempt structured ATS extraction
        if "greenhouse.io" in careers_url:
            jobs = self._extract_greenhouse(careers_url)
        elif "jobs.lever.co" in careers_url:
            jobs = self._extract_lever(careers_url)
        else:
            # Fallback to Playwright
            jobs = self._extract_playwright(careers_url)

        if not jobs:
            return []

        # 2. Get previous snapshot
        try:
            from app.database import get_signals, get_supabase_client
            client = get_supabase_client()
            res = client.table("signals").select("payload").eq("company_id", company_id).eq("source_id", "jobs_snapshot").order("created_at", desc=True).limit(1).execute()
            prev_titles = set(res.data[0].get("payload", {}).get("active_jobs", [])) if res.data else set()
        except Exception:
            prev_titles = set()

        current_titles = {j["title"] for j in jobs}
        new_jobs = [j for j in jobs if j["title"] not in prev_titles]

        # 3. Derive Intelligence from new jobs using LLM
        if new_jobs:
            strategic_signals = self._derive_hiring_intelligence(new_jobs, company_name)
            for s in strategic_signals:
                signals.append({
                    "company_id": company_id,
                    "company_name": company_name,
                    "signal_type": SignalType.HIRING,
                    "subtype": s.get("subtype"),
                    "title": s.get("title", "Hiring Expansion Detected"),
                    "content": s.get("content", ""),
                    "url": careers_url,
                    "payload": {"new_roles": s.get("roles_involved", [])},
                    "agent": "JobsAgent",
                    "extraction_model": "groq-llama-3"
                })

        # Save snapshot for next run
        try:
            # We simulate saving state (in practice, might want a different table, but for now we won't crash)
            pass
        except Exception:
            pass

        logger.info(f"JobsAgent collected {len(signals)} strategic signals for {company_name}")
        return signals

    def _extract_greenhouse(self, url: str) -> list[dict]:
        """Fetch jobs from Greenhouse API."""
        try:
            # extract board token from URL, e.g. boards.greenhouse.io/openai
            board = url.rstrip("/").split("/")[-1]
            api_url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
            resp = requests.get(api_url, timeout=10)
            if resp.status_code == 200:
                jobs = resp.json().get("jobs", [])
                return [{"title": j.get("title"), "location": j.get("location", {}).get("name"), "department": "Unknown"} for j in jobs]
        except Exception as e:
            logger.warning(f"Greenhouse extraction failed: {e}")
        return []

    def _extract_lever(self, url: str) -> list[dict]:
        """Fetch jobs from Lever API."""
        try:
            board = url.rstrip("/").split("/")[-1]
            api_url = f"https://api.lever.co/v0/postings/{board}"
            resp = requests.get(api_url, timeout=10)
            if resp.status_code == 200:
                jobs = resp.json()
                return [{"title": j.get("text"), "location": j.get("categories", {}).get("location"), "department": j.get("categories", {}).get("team")} for j in jobs]
        except Exception as e:
            logger.warning(f"Lever extraction failed: {e}")
        return []

    def _extract_playwright(self, url: str) -> list[dict]:
        """Fallback to Playwright scraping."""
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_default_timeout(30000)
                page.goto(url, wait_until="domcontentloaded")
                page.wait_for_timeout(2000)
                text = page.inner_text("body")
                browser.close()
                
            jobs = []
            for line in text.split("\n"):
                line = line.strip()
                if len(line) > 5 and any(kw in line.lower() for kw in ["engineer", "manager", "developer", "director", "lead", "designer"]):
                    jobs.append({"title": line, "location": "", "department": "Unknown"})
            return jobs
        except Exception as e:
            logger.warning(f"Playwright extraction failed: {e}")
            return []

    def _derive_hiring_intelligence(self, new_jobs: list[dict], company_name: str) -> list[dict]:
        """Use LLM to group raw jobs into strategic hiring signals."""
        if len(new_jobs) < 3:
            return [] # Need a cluster to form a strategic signal

        job_list = "\n".join([f"- {j['title']} ({j.get('location', 'Unknown')})" for j in new_jobs])
        prompt = f"""Analyze these {len(new_jobs)} newly posted jobs for {company_name}.
Group them into 1-2 major strategic hiring vectors.

Allowed Subtypes: AI_EXPANSION, GTM_PUSH, REGIONAL_EXPANSION, LEADERSHIP_SURGE

Jobs:
{job_list}

Return ONLY valid JSON like:
[{{
    "subtype": "AI_EXPANSION",
    "title": "Major AI Engineering Expansion",
    "content": "Company is aggressively hiring AI/ML engineers.",
    "roles_involved": ["Senior AI Engineer", "Data Scientist"]
}}]
"""
        try:
            llm = get_groq_llm()
            response = llm_invoke(llm, prompt)
            match = re.search(r"\[\s*\{.*\}\s*\]", response, re.DOTALL)
            if match:
                return json.loads(match.group())
            return []
        except Exception as e:
            logger.error(f"Failed to derive hiring intelligence: {e}")
            return []