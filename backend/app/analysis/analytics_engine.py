"""
Argos — Analytics Engine V1
Computes the Intelligence Score and component breakdowns based on real data.
"""

import logging
from datetime import datetime, timedelta, timezone

from app.database import get_supabase_client, save_analytics_snapshot
from app.memory.graph_db import GraphDB

logger = logging.getLogger(__name__)

class AnalyticsEngine:
    def __init__(self):
        self.client = get_supabase_client()

    def compute_analytics(self, company_id: str, company_name: str) -> dict:
        """
        Compute Analytics V1 score and breakdown from real data.
        Returns the payload and saves it to snapshots.
        """
        now = datetime.now(timezone.utc)
        thirty_days_ago = (now - timedelta(days=30)).isoformat()
        seven_days_ago = (now - timedelta(days=7)).isoformat()

        # 1. Signal Volume (Max 25 points)
        # Assuming 50 signals in 30 days = max points
        try:
            res = self.client.table("signals").select("id", count="exact").eq("company_id", company_id).gte("collected_at", thirty_days_ago).execute()
            signal_count = res.count or 0
            signal_volume_score = min(25, (signal_count / 50.0) * 25)
        except Exception:
            signal_volume_score = 0

        # 2. Hiring Velocity (Max 18 points)
        try:
            res = self.client.table("signals").select("id", count="exact").eq("company_id", company_id).eq("source", "jobs").gte("collected_at", thirty_days_ago).execute()
            jobs_count = res.count or 0
            hiring_velocity_score = min(18, (jobs_count / 10.0) * 18)
        except Exception:
            hiring_velocity_score = 0

        # 3. Funding Activity (Max 20 points)
        try:
            res = self.client.table("signals").select("title, content").eq("company_id", company_id).eq("source", "funding").gte("collected_at", thirty_days_ago).execute()
            funding_count = res.count or 0
            if funding_count == 0:
                # Fallback to news text search
                res = self.client.table("signals").select("title, content").eq("company_id", company_id).eq("source", "news").gte("collected_at", thirty_days_ago).execute()
                funding_keywords = ["funding", "raised", "series", "seed", "investment", "capital"]
                for sig in (res.data or []):
                    text = (sig.get("title", "") + " " + sig.get("content", "")).lower()
                    if any(k in text for k in funding_keywords):
                        funding_count += 1
            funding_activity_score = min(20, (funding_count / 2.0) * 20)
        except Exception:
            funding_activity_score = 0

        # 4. Sentiment (Max 15 points)
        try:
            res = self.client.table("signals").select("title, content").eq("company_id", company_id).gte("collected_at", thirty_days_ago).execute()
            
            base_score = 7.5
            adjustment = 0.0
            
            positive_kws = ["record", "expansion", "raised", "success", "growth", "launch", "hiring", "profitable", "partnership", "award"]
            negative_kws = ["layoff", "departure", "breach", "lawsuit", "decline", "missed", "resigned", "down", "struggle", "loss"]
            
            for sig in (res.data or []):
                text = (sig.get("title", "") + " " + (sig.get("content") or "")).lower()
                
                if any(kw in text for kw in positive_kws):
                    adjustment += 0.2
                
                if any(kw in text for kw in negative_kws):
                    adjustment -= 0.3
                    
            clamped_adjustment = max(-5.5, min(5.5, adjustment))
            sentiment_score = base_score + clamped_adjustment
            
        except Exception as e:
            logger.error(f"Failed to compute sentiment: {e}")
            sentiment_score = 7.5

        # 5. Executive Events (Max 8 points)
        try:
            res = self.client.table("signals").select("id", count="exact").eq("company_id", company_id).eq("source", "executive").gte("collected_at", thirty_days_ago).execute()
            exec_count = res.count or 0
            executive_events_score = min(8, (exec_count / 1.0) * 8)
        except Exception:
            executive_events_score = 0

        # 6. Report Activity (Max 5 points)
        try:
            res = self.client.table("reports").select("id", count="exact").eq("company_id", company_id).gte("generated_at", thirty_days_ago).execute()
            report_count = res.count or 0
            report_activity_score = min(5, (report_count / 4.0) * 5)
        except Exception:
            report_activity_score = 0

        total_score = round(
            signal_volume_score + hiring_velocity_score + funding_activity_score +
            sentiment_score + executive_events_score + report_activity_score, 1
        )

        payload = {
            "signal_volume": round(signal_volume_score, 1),
            "hiring_velocity": round(hiring_velocity_score, 1),
            "funding_activity": round(funding_activity_score, 1),
            "sentiment": round(sentiment_score, 1),
            "executive_events": round(executive_events_score, 1),
            "report_activity": round(report_activity_score, 1),
            "total": total_score
        }

        # 1. Save Snapshot
        save_analytics_snapshot(
            metric_type=f"intelligence_score:{company_id}",
            payload=payload
        )

        # Fetch previous score to calculate change
        try:
            comp_res = self.client.table("companies").select("intelligence_score").eq("id", company_id).execute()
            prev_score = 0
            if comp_res.data and comp_res.data[0].get("intelligence_score"):
                prev_score = float(comp_res.data[0]["intelligence_score"])
            score_change = round(total_score - prev_score, 1)
        except Exception:
            score_change = 0.0

        # Save History
        history_payload = {
            "company_id": company_id,
            "timestamp": now.strftime("%Y-%m-%d"),
            "score": total_score
        }
        save_analytics_snapshot(
            metric_type=f"score_history:{company_id}",
            payload=history_payload
        )

        # Update company row for fast sorting and rich rankings
        try:
            self.client.table("companies").update({
                "intelligence_score": total_score,
                "score_change": score_change,
                "signals_count": signal_count
            }).eq("id", company_id).execute()
        except Exception as e:
            logger.error(f"Failed to update company analytics fields: {e}")

        # 3. Update Knowledge Graph
        try:
            from app.config import NEO4J_DATABASE
            graph_db = GraphDB()
            driver = graph_db._get_driver()
            if driver:
                with driver.session(database=NEO4J_DATABASE) as session:
                    # Update Node Weight
                    query_node = "MATCH (c:Company {name: $name}) SET c.intelligence_score = $score"
                    session.run(query_node, name=company_name, score=total_score)
                    
                    # Update Edge Strength for new signals (simulated as raising relation weights)
                    query_edge = """
                    MATCH (c:Company {name: $name})-[r]->(t)
                    SET r.strength = coalesce(r.strength, 1.0) + ($score / 100.0)
                    """
                    session.run(query_edge, name=company_name, score=total_score)
        except Exception as e:
            logger.error(f"Failed to update KG with analytics: {e}")

        # --- V2 Extension Hooks ---
        # Future integrations can attach data here:
        # payload["github_activity"] = self._compute_github_v2()
        # payload["linkedin_hiring"] = self._compute_linkedin_v2()
        # payload["crunchbase_funding"] = self._compute_crunchbase_v2()
        # payload["sec_filings"] = self._compute_sec_v2()
        # payload["producthunt_launches"] = self._compute_ph_v2()
        # payload["reddit_mentions"] = self._compute_reddit_v2()
        # payload["x_mentions"] = self._compute_x_v2()

        return payload