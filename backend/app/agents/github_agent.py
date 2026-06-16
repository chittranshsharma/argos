"""
Argos — GitHub Agent
100% Deterministic Engineering Velocity Engine.
Collects API metrics, computes velocity, and derives signals through strict mathematical thresholds.
"""

import logging
from datetime import datetime, timezone, timedelta
import requests

from app.signals.registry import SignalType, SignalSubtype
from app.database import get_latest_github_snapshot, save_github_snapshot, update_company

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
HEADERS = {"Accept": "application/vnd.github.v3+json"}

class GitHubAgent:
    """Derives engineering velocity signals using pure deterministic rules."""

    def collect(self, github_org: str, company_name: str, company_id: str) -> list[dict]:
        if not github_org:
            return []

        signals = []

        try:
            # 1. Fetch current absolute metrics
            repos = self._get_org_repos(github_org)
            if not repos:
                return []

            current_metrics = {
                "stars": sum(r.get("stargazers_count", 0) for r in repos),
                "forks": sum(r.get("forks_count", 0) for r in repos),
                "repo_count": len(repos),
                "contributors_30d": 0,
                "commits_30d": 0,
                "releases_30d": 0,
                "new_repos_30d": 0
            }

            cutoff_30d = datetime.now(timezone.utc) - timedelta(days=30)
            
            # For unique contributors
            contributors_set = set()

            # Iterate over top repos (limit 10 for API limits)
            for repo in repos[:10]:
                full_name = repo.get("full_name")
                
                # Check creation
                created_at = repo.get("created_at")
                if created_at:
                    try:
                        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        if dt > cutoff_30d: 
                            current_metrics["new_repos_30d"] += 1
                    except: pass
                
                # Count commits & contributors in last 30 days
                commits = self._get_commits(full_name, days_ago=30)
                current_metrics["commits_30d"] += len(commits)
                for c in commits:
                    author = c.get("author")
                    if author and author.get("login"):
                        contributors_set.add(author["login"])
                
                # Count releases in last 30 days
                current_metrics["releases_30d"] += len(self._get_releases(full_name, days_ago=30))

            current_metrics["contributors_30d"] = len(contributors_set)

            # 2. Fetch previous snapshot to compute deltas
            prev_snapshot = get_latest_github_snapshot(company_id)
            
            stars_delta = 0
            forks_delta = 0
            stars_growth_pct = 0.0
            
            if prev_snapshot:
                prev_stars = prev_snapshot.get("stars", 0)
                prev_forks = prev_snapshot.get("forks", 0)
                
                stars_delta = current_metrics["stars"] - prev_stars
                forks_delta = current_metrics["forks"] - prev_forks
                
                if prev_stars > 0:
                    stars_growth_pct = stars_delta / prev_stars
                    
            current_metrics["stars_delta"] = stars_delta
            current_metrics["stars_growth_pct"] = stars_growth_pct
            current_metrics["forks_delta"] = forks_delta
            
            prev_commits_30d = prev_snapshot.get("commits_30d", 0) if prev_snapshot else 0
            prev_contribs_30d = prev_snapshot.get("contributors_30d", 0) if prev_snapshot else 0
            prev_releases_30d = prev_snapshot.get("releases_30d", 0) if prev_snapshot else 0

            # 3. Calculate Engineering Velocity Score (0-100)
            score_commits = min(30, (current_metrics["commits_30d"] / 100.0) * 30)
            score_contribs = min(30, (current_metrics["contributors_30d"] / 20.0) * 30)
            score_releases = min(20, (current_metrics["releases_30d"] / 4.0) * 20)
            score_stars = min(20, (max(0, stars_delta) / 50.0) * 20)
            
            velocity_score = int(score_commits + score_contribs + score_releases + score_stars)

            # Update the company's velocity score
            update_company(company_id, {"engineering_velocity_score": velocity_score})

            # 4. Generate Deterministic Signals
            # Must strictly follow the relative growth rules
            
            # Rule 1: RELEASE_ACCELERATION
            if current_metrics["releases_30d"] >= 3 and current_metrics["releases_30d"] > prev_releases_30d:
                signals.append(self._build_signal(
                    company_id, company_name, github_org,
                    subtype="RELEASE_ACCELERATION",
                    title="Release Velocity Acceleration",
                    content=f"Company shipped {current_metrics['releases_30d']} releases in 30 days (up from {prev_releases_30d}).",
                    evidence={
                        "releases_before": prev_releases_30d,
                        "releases_after": current_metrics["releases_30d"]
                    }
                ))

            # Rule 2: ENGINEERING_EXPANSION
            if current_metrics["contributors_30d"] > (prev_contribs_30d * 1.5) and prev_contribs_30d > 0:
                signals.append(self._build_signal(
                    company_id, company_name, github_org,
                    subtype="ENGINEERING_EXPANSION",
                    title="Engineering Contributor Expansion",
                    content=f"Active contributors grew by over 50% to {current_metrics['contributors_30d']} in the last 30 days.",
                    evidence={
                        "contributors_before": prev_contribs_30d,
                        "contributors_after": current_metrics["contributors_30d"]
                    }
                ))

            # Rule 3: OPEN_SOURCE_MOMENTUM
            if stars_growth_pct > 0.20 and stars_delta > 0:
                signals.append(self._build_signal(
                    company_id, company_name, github_org,
                    subtype="OPEN_SOURCE_MOMENTUM",
                    title="Open Source Momentum Surge",
                    content=f"Repository stars grew by {int(stars_growth_pct*100)}% (+{stars_delta} stars) recently.",
                    evidence={
                        "stars_before": prev_snapshot.get("stars", 0),
                        "stars_after": current_metrics["stars"],
                        "growth_pct": round(stars_growth_pct, 3)
                    }
                ))

            # Rule 4: NEW_PRODUCT_INITIATIVE
            if current_metrics["new_repos_30d"] > 0:
                signals.append(self._build_signal(
                    company_id, company_name, github_org,
                    subtype="NEW_PRODUCT_INITIATIVE",
                    title="New Open Source Repository",
                    content=f"Company launched {current_metrics['new_repos_30d']} new repository(ies) in the last 30 days.",
                    evidence={
                        "new_repos_30d": current_metrics["new_repos_30d"]
                    }
                ))

            # 5. Save the snapshot for the next run
            snapshot = {
                "company_id": company_id,
                "stars": current_metrics["stars"],
                "forks": current_metrics["forks"],
                "repo_count": current_metrics["repo_count"],
                "contributors_30d": current_metrics["contributors_30d"],
                "commits_30d": current_metrics["commits_30d"],
                "releases_30d": current_metrics["releases_30d"]
            }
            save_github_snapshot(snapshot)

        except Exception as e:
            logger.error(f"GitHubAgent error for {github_org}: {e}")

        logger.info(f"GitHubAgent collected {len(signals)} structured signals for {company_name}")
        return signals

    def _build_signal(self, company_id: str, company_name: str, github_org: str, subtype: str, title: str, content: str, evidence: dict) -> dict:
        """Helper to construct deterministic signals."""
        return {
            "company_id": company_id,
            "company_name": company_name,
            "signal_type": SignalType.GITHUB,
            "subtype": subtype,
            "title": title,
            "content": content,
            "url": f"https://github.com/{github_org}",
            "payload": {
                "evidence": evidence,
                "confidence": 0.95,
                "review_status": "auto_approved",
                "confidence_reasoning": {
                    "source": "github_api",
                    "metric_based": True
                }
            },
            "agent": "GitHubAgent",
            "extraction_model": "deterministic"
        }

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

    def _get_commits(self, full_name: str, days_ago: int = 30) -> list:
        try:
            since = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()
            url = f"{GITHUB_API}/repos/{full_name}/commits"
            params = {"since": since, "per_page": 100}
            resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
            if resp.status_code == 200:
                return resp.json()
            return []
        except: return []

    def _get_releases(self, full_name: str, days_ago: int = 30) -> list:
        try:
            url = f"{GITHUB_API}/repos/{full_name}/releases"
            params = {"per_page": 20}
            resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
            if resp.status_code == 200:
                releases = resp.json()
                cutoff = datetime.now(timezone.utc) - timedelta(days=days_ago)
                recent = []
                for r in releases:
                    try:
                        pub = datetime.fromisoformat(r["published_at"].replace("Z", "+00:00"))
                        if pub > cutoff: recent.append(r)
                    except: recent.append(r)
                return recent
            return []
        except: return []