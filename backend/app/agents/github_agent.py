"""
Argos — GitHub Agent
Collects repository metrics and derives engineering velocity intelligence.
"""

import logging
from datetime import datetime, timezone, timedelta
import requests
import json
import re

from app.signals.registry import SignalType, SignalSubtype
from app.llm import get_groq_llm, llm_invoke

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
HEADERS = {"Accept": "application/vnd.github.v3+json"}

class GitHubAgent:
    """Derives engineering velocity signals from GitHub."""

    def collect(self, github_org: str, company_name: str, company_id: str) -> list[dict]:
        """Fetch metrics and compute velocity signals."""
        if not github_org:
            return []

        signals = []

        try:
            repos = self._get_org_repos(github_org)
            if not repos:
                return []

            metrics = {
                "total_repos": len(repos),
                "total_stars": sum(r.get("stargazers_count", 0) for r in repos),
                "total_forks": sum(r.get("forks_count", 0) for r in repos),
                "new_repos_30d": 0,
                "recent_releases": 0,
                "recent_commits": 0,
            }

            cutoff_30d = datetime.now(timezone.utc) - timedelta(days=30)
            cutoff_7d = datetime.now(timezone.utc) - timedelta(days=7)

            for repo in repos[:10]:
                full_name = repo.get("full_name")
                
                # Check creation
                created_at = repo.get("created_at")
                if created_at:
                    try:
                        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        if dt > cutoff_30d: metrics["new_repos_30d"] += 1
                    except: pass
                
                # Count commits in last 7 days
                metrics["recent_commits"] += len(self._get_recent_commits(full_name))
                
                # Count releases in last 30 days
                metrics["recent_releases"] += len(self._get_releases(full_name))

            # Derive Intelligence
            strategic_signals = self._derive_github_intelligence(metrics, company_name)
            
            for s in strategic_signals:
                signals.append({
                    "company_id": company_id,
                    "company_name": company_name,
                    "signal_type": SignalType.GITHUB,
                    "subtype": s.get("subtype"),
                    "title": s.get("title", "GitHub Velocity Shift"),
                    "content": s.get("content", ""),
                    "url": f"https://github.com/{github_org}",
                    "payload": metrics,
                    "agent": "GitHubAgent",
                    "extraction_model": "groq-llama-3"
                })

        except Exception as e:
            logger.error(f"GitHubAgent error for {github_org}: {e}")

        logger.info(f"GitHubAgent collected {len(signals)} structured signals for {company_name}")
        return signals

    def _derive_github_intelligence(self, metrics: dict, company_name: str) -> list[dict]:
        """Use LLM to determine if these metrics represent a strategic velocity signal."""
        
        # Heuristic gate to save LLM calls
        if metrics["recent_commits"] == 0 and metrics["recent_releases"] == 0 and metrics["new_repos_30d"] == 0:
            # Maybe emit MAINTENANCE_DECLINE if we tracked historicals, but for now we skip
            pass
            
        prompt = f"""Analyze the following GitHub engineering metrics for {company_name}.
Determine if this constitutes a major engineering velocity event.

Metrics (Last 30 Days):
- Total Repos: {metrics['total_repos']}
- Total Stars: {metrics['total_stars']}
- Total Forks: {metrics['total_forks']}
- New Repos created: {metrics['new_repos_30d']}
- Recent Releases: {metrics['recent_releases']}
- Commits (last 7 days top repos): {metrics['recent_commits']}

Allowed Subtypes: ENGINEERING_SURGE, RELEASE_ACCELERATION, OPEN_SOURCE_EXPANSION, MAINTENANCE_DECLINE

If the activity is extremely high, select a subtype. If it's normal business as usual, return [].

Return ONLY valid JSON like:
[{{
    "subtype": "ENGINEERING_SURGE",
    "title": "High Engineering Velocity",
    "content": "Company generated 45 commits and 3 releases this week."
}}]
"""
        try:
            llm = get_groq_llm()
            response = llm_invoke(llm, prompt)
            match = re.search(r"\[\s*\{.*\}\s*\]", response, re.DOTALL)
            if match:
                return json.loads(match.group())
            return []
        except Exception:
            return []

    def _get_org_repos(self, org: str) -> list:
        try:
            url = f"{GITHUB_API}/orgs/{org}/repos"
            params = {"sort": "stars", "direction": "desc", "per_page": 20}
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code == 404:
                url = f"{GITHUB_API}/users/{org}/repos"
                resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
            if resp.status_code == 200:
                return resp.json()
            return []
        except: return []

    def _get_recent_commits(self, full_name: str) -> list:
        try:
            since = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
            url = f"{GITHUB_API}/repos/{full_name}/commits"
            params = {"since": since, "per_page": 100}
            resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
            if resp.status_code == 200:
                return resp.json()
            return []
        except: return []

    def _get_releases(self, full_name: str) -> list:
        try:
            url = f"{GITHUB_API}/repos/{full_name}/releases"
            params = {"per_page": 10}
            resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
            if resp.status_code == 200:
                releases = resp.json()
                cutoff = datetime.now(timezone.utc) - timedelta(days=30)
                recent = []
                for r in releases:
                    try:
                        pub = datetime.fromisoformat(r["published_at"].replace("Z", "+00:00"))
                        if pub > cutoff: recent.append(r)
                    except: recent.append(r)
                return recent
            return []
        except: return []