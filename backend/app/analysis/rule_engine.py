import logging
from app.database import get_supabase_client

logger = logging.getLogger(__name__)

class RuleEngine:
    def get_rules_for_company(self, company_id: str) -> list[dict]:
        try:
            client = get_supabase_client()
            result = client.table("alert_rules")\
                .select("*")\
                .eq("company_id", company_id)\
                .eq("is_active", True)\
                .execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get rules: {e}")
            return []
    
    def evaluate_rules(
        self, 
        company_id: str,
        new_signals: list[dict]
    ) -> list[dict]:
        """
        Evaluate all active rules against new signals.
        Returns list of triggered alerts.
        """
        rules = self.get_rules_for_company(company_id)
        triggered = []
        
        for rule in rules:
            for signal in new_signals:
                if self._matches_rule(rule, signal):
                    triggered.append({
                        "rule_id": rule["id"],
                        "rule_name": rule["rule_name"],
                        "company_id": company_id,
                        "company_name": rule["company_name"],
                        "signal": signal,
                        "alert_type": "custom_rule",
                        "message": f"🎯 Rule '{rule['rule_name']}' triggered: {signal.get('title', '')}"
                    })
                    # Update trigger count
                    try:
                        from datetime import datetime, timezone
                        client = get_supabase_client()
                        client.table("alert_rules").update({
                            "last_triggered": datetime.now(timezone.utc).isoformat(),
                            "trigger_count": rule.get("trigger_count", 0) + 1
                        }).eq("id", rule["id"]).execute()
                    except Exception:
                        pass
                    break  # One alert per rule per cycle
        
        return triggered
    
    def _matches_rule(self, rule: dict, signal: dict) -> bool:
        """Check if a signal matches a rule"""
        # Source filter
        if rule.get("source") and rule["source"] != "any":
            if signal.get("source") != rule["source"]:
                return False
        
        # Keyword match (case insensitive)
        keyword = rule.get("keyword", "").lower()
        text = (
            (signal.get("title") or "") + " " + 
            (signal.get("content") or "")
        ).lower()
        
        if keyword and keyword not in text:
            return False
        
        # Importance threshold
        threshold = rule.get("importance_threshold", "any")
        if threshold != "any":
            importance_rank = {"low": 1, "medium": 2, "high": 3}
            signal_rank = importance_rank.get(
                signal.get("importance", "medium"), 2
            )
            threshold_rank = importance_rank.get(threshold, 1)
            if signal_rank < threshold_rank:
                return False
        
        return True