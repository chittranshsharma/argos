import json
import logging
from app.llm import get_groq_llm, llm_invoke

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def analyze_batch_sentiment(
        self, 
        signals: list[dict]
    ) -> list[dict]:
        """
        Analyze sentiment for a batch of signals.
        Returns signals with sentiment_score (-1 to 1) added.
        """
        if not signals:
            return []
        
        results = []
        for signal in signals:
            text = f"{signal.get('title','')} {signal.get('content','')[:300]}"
            score = self._score_sentiment(text)
            results.append({
                **signal,
                "sentiment_score": score
            })
        return results
    
    def _score_sentiment(self, text: str) -> float:
        """
        Simple keyword-based sentiment scoring.
        Returns float between -1 (negative) and 1 (positive).
        """
        text = text.lower()
        
        positive_words = [
            "great", "excellent", "amazing", "best", "love",
            "fantastic", "outstanding", "impressive", "reliable",
            "fast", "innovative", "growth", "success", "winning",
            "profitable", "expanding", "hire", "launch", "milestone"
        ]
        negative_words = [
            "bad", "terrible", "awful", "worst", "hate",
            "broken", "slow", "down", "outage", "scam", "fraud",
            "layoff", "fired", "bankrupt", "lawsuit", "breach",
            "hack", "fail", "loss", "decline", "leaving"
        ]
        
        pos = sum(1 for w in positive_words if w in text)
        neg = sum(1 for w in negative_words if w in text)
        total = pos + neg
        
        if total == 0:
            return 0.0
        return round((pos - neg) / total, 2)
    
    def get_weekly_sentiment(
        self,
        signals: list[dict],
        weeks: int = 12
    ) -> list[dict]:
        """
        Aggregate sentiment by week for the last N weeks.
        Returns list of {week, avg_sentiment, signal_count}
        """
        from datetime import datetime, timedelta, timezone
        from collections import defaultdict
        
        now = datetime.now(timezone.utc)
        weekly_data = defaultdict(list)
        
        for signal in signals:
            try:
                collected = datetime.fromisoformat(
                    signal["collected_at"].replace("Z", "+00:00")
                )
                days_ago = (now - collected).days
                week_num = days_ago // 7
                if week_num < weeks:
                    score = signal.get("sentiment_score", 0)
                    weekly_data[week_num].append(score)
            except Exception:
                continue
        
        result = []
        for week in range(weeks - 1, -1, -1):
            scores = weekly_data.get(week, [])
            week_start = now - timedelta(days=(week + 1) * 7)
            result.append({
                "week": week_start.strftime("%b %d"),
                "avg_sentiment": round(
                    sum(scores) / len(scores), 2
                ) if scores else 0,
                "signal_count": len(scores)
            })
        
        return result