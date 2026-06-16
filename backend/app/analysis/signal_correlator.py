"""
Argos — Signal Correlator
[DORMANT]: This module is an experimental subsystem under observation for 30 days.
It currently produces 0% of the hypotheses and serves only to collect metrics 
comparing its rule-based output against the HypothesisEngine's direct LLM synthesis.
"""

import logging
import json
from datetime import datetime, timezone, timedelta
from app.llm import get_groq_llm, llm_invoke
from app.signals.registry import SignalType

logger = logging.getLogger(__name__)

class SignalCorrelator:
    def __init__(self):
        pass

    def evaluate_correlations(self, company_id: str, company_name: str, signals: list[dict]) -> list[dict]:
        """
        Evaluate 60 days of signals against hard deterministic rules.
        Returns a list of CORRELATION super-signals.
        """
        if not signals:
            return []

        # Filter out existing correlations to avoid feedback loops
        base_signals = [s for s in signals if str(s.get("signal_type")).upper() != "CORRELATION"]

        # Group signals by source / subtype
        funding_signals = [s for s in base_signals if s.get("source") == "funding" or str(s.get("signal_type")).upper() == "FUNDING"]
        exec_signals = [s for s in base_signals if s.get("source") == "executive" or str(s.get("signal_type")).upper() == "EXECUTIVE"]
        hiring_signals = [s for s in base_signals if s.get("source") == "jobs" or str(s.get("signal_type")).upper() == "HIRING"]
        news_signals = [s for s in base_signals if s.get("source") in ("news", "hackernews")]
        launch_signals = [s for s in base_signals if s.get("source") in ("producthunt", "changelog", "launch")]

        correlations = []

        # -------------------------------------------------------------
        # Rule 1: STRATEGIC_EXPANSION
        # Funding + Hiring Surge (AI/Engineering/GTM) + Executive Appointed
        # -------------------------------------------------------------
        has_funding = len(funding_signals) > 0
        has_hiring_surge = any(
            s.get("subtype") in ["AI_EXPANSION", "ENGINEERING_SURGE", "GTM_PUSH", "REGIONAL_EXPANSION"]
            for s in hiring_signals
        )
        appointed_execs = [s for s in exec_signals if s.get("payload", {}).get("movement_type", "").lower() in ["appointed", "joined", "hired"]]
        
        if has_funding and has_hiring_surge and appointed_execs:
            evidence = funding_signals[:1] + [s for s in hiring_signals if s.get("subtype") in ["AI_EXPANSION", "ENGINEERING_SURGE", "GTM_PUSH", "REGIONAL_EXPANSION"]][:1] + appointed_execs[:1]
            correlations.append(self._build_correlation(
                company_id, company_name, "STRATEGIC_EXPANSION", "Strategic Expansion", evidence, "EXPANSION_RULE_V1"
            ))

        # -------------------------------------------------------------
        # Rule 2: COMPETITIVE_ACCELERATION
        # Funding + Engineering Surge + Product Launch
        # -------------------------------------------------------------
        has_eng_surge = any(s.get("subtype") in ["ENGINEERING_SURGE", "AI_EXPANSION"] for s in hiring_signals)
        has_launch = len(launch_signals) > 0

        if has_funding and has_eng_surge and has_launch:
            evidence = funding_signals[:1] + [s for s in hiring_signals if s.get("subtype") in ["ENGINEERING_SURGE", "AI_EXPANSION"]][:1] + launch_signals[:1]
            correlations.append(self._build_correlation(
                company_id, company_name, "COMPETITIVE_ACCELERATION", "Competitive Acceleration", evidence, "ACCELERATION_RULE_V1"
            ))

        # -------------------------------------------------------------
        # Rule 3: ORGANIZATIONAL_RISK
        # Executive Departure + Negative Sentiment / Layoffs
        # -------------------------------------------------------------
        departed_execs = [s for s in exec_signals if s.get("payload", {}).get("movement_type", "").lower() in ["departed", "resigned", "stepped_down", "board_departed"]]
        has_negative_news = any(
            any(kw in str(s.get("title", "") + " " + s.get("content", "")).lower() for kw in ["layoff", "restructuring", "cut", "missed", "struggle", "decline"])
            for s in news_signals
        )
        
        if departed_execs and has_negative_news:
            evidence = departed_execs[:1] + [s for s in news_signals if any(kw in str(s.get("title", "") + " " + s.get("content", "")).lower() for kw in ["layoff", "restructuring", "cut", "missed", "struggle", "decline"])][:1]
            correlations.append(self._build_correlation(
                company_id, company_name, "ORGANIZATIONAL_RISK", "Organizational Risk", evidence, "RISK_RULE_V1"
            ))

        # -------------------------------------------------------------
        # Rule 4: MARKET_CONSOLIDATION
        # Acquisition + Hiring Reduction (Layoffs/Restructuring)
        # -------------------------------------------------------------
        has_acquisition = any(s.get("subtype", "").upper() == "ACQUISITION" for s in funding_signals)
        if has_acquisition and has_negative_news:
            acq_evidence = [s for s in funding_signals if s.get("subtype", "").upper() == "ACQUISITION"][:1]
            neg_evidence = [s for s in news_signals if any(kw in str(s.get("title", "") + " " + s.get("content", "")).lower() for kw in ["layoff", "restructuring", "cut"])][:1]
            if neg_evidence:
                correlations.append(self._build_correlation(
                    company_id, company_name, "MARKET_CONSOLIDATION", "Market Consolidation", acq_evidence + neg_evidence, "CONSOLIDATION_RULE_V1"
                ))

        # -------------------------------------------------------------
        # Rule 5: LEADERSHIP_REORGANIZATION
        # Multiple executive changes (>=3) in 60 days
        # -------------------------------------------------------------
        if len(exec_signals) >= 3:
            evidence = exec_signals[:3]
            correlations.append(self._build_correlation(
                company_id, company_name, "LEADERSHIP_REORGANIZATION", "Leadership Reorganization", evidence, "REORG_RULE_V1"
            ))

        # -------------------------------------------------------------
        # Rule 6: GEOGRAPHIC_EXPANSION
        # Regional Hiring + (News of office OR Partnership)
        # -------------------------------------------------------------
        has_regional_hiring = any(s.get("subtype") == "REGIONAL_EXPANSION" for s in hiring_signals)
        has_office_news = any(
            any(kw in str(s.get("title", "") + " " + s.get("content", "")).lower() for kw in ["new office", "expansion", "headquarters", "global", "partnership", "partnered"])
            for s in news_signals
        )
        
        if has_regional_hiring and has_office_news:
            evidence = [s for s in hiring_signals if s.get("subtype") == "REGIONAL_EXPANSION"][:1] + [s for s in news_signals if any(kw in str(s.get("title", "") + " " + s.get("content", "")).lower() for kw in ["new office", "expansion", "headquarters", "global", "partnership", "partnered"])][:1]
            correlations.append(self._build_correlation(
                company_id, company_name, "GEOGRAPHIC_EXPANSION", "Geographic Expansion", evidence, "GEO_EXPANSION_RULE_V1"
            ))

        # Deduplicate correlations by subtype to avoid emitting multiples of the same macro event
        unique_correlations = { c["subtype"]: c for c in correlations }
        return list(unique_correlations.values())


    def _build_correlation(self, company_id: str, company_name: str, subtype: str, title_prefix: str, evidence: list[dict], rule_name: str) -> dict:
        """
        Takes matched evidence and uses the LLM to generate a professional narrative.
        """
        evidence_text = "\n".join([f"- {s.get('title')}: {s.get('content')}" for s in evidence])
        
        prompt = f"""You are a competitive intelligence analyst. I have detected a "{title_prefix}" event for {company_name} based on the following verified signals:

EVIDENCE:
{evidence_text}

Write a professional, 2-3 sentence narrative summarizing this correlated event. Focus on what this means strategically. Do not invent any facts not present in the evidence.

Return ONLY the narrative string. No markdown formatting, no JSON, no quotes."""

        try:
            llm = get_groq_llm()
            narrative = llm_invoke(llm, prompt).strip(' "')
        except Exception as e:
            logger.error(f"Failed to generate narrative for {subtype}: {e}")
            narrative = f"{title_prefix} detected based on multiple concurrent signals."

        # Calculate dynamic confidence
        confidences = []
        for s in evidence:
            conf = s.get("confidence") or s.get("payload", {}).get("confidence") or s.get("raw_data", {}).get("confidence")
            if conf:
                try:
                    confidences.append(float(conf))
                except:
                    pass
                    
        if confidences:
            avg_evidence_confidence = sum(confidences) / len(confidences)
            correlation_confidence = min(avg_evidence_confidence * 1.15, 0.99)
        else:
            correlation_confidence = 0.85
            
        correlation_confidence = round(correlation_confidence, 2)
        
        # Determine review status for macro event
        needs_review = correlation_confidence < 0.70
        review_status = "pending" if needs_review else "auto_approved"

        return {
            "company_id": company_id,
            "company_name": company_name,
            "signal_type": "CORRELATION",
            "subtype": subtype,
            "title": f"Macro Event: {title_prefix}",
            "content": narrative,
            "url": evidence[0].get("url", ""),
            "payload": {
                "evidence_ids": [s.get("id") for s in evidence if s.get("id")],
                "supporting_signals": [
                    {
                        "id": s.get("id"),
                        "title": s.get("title"),
                        "signal_type": s.get("signal_type"),
                        "subtype": s.get("subtype"),
                        "url": s.get("url"),
                        "content": s.get("content")
                    } for s in evidence
                ],
                "created_by_rule": rule_name,
                "confidence": correlation_confidence,
                "confidence_reasoning": {
                    "avg_evidence_confidence": round(avg_evidence_confidence if confidences else 0.85, 2),
                    "correlation_boost": 1.15,
                    "review_status": review_status
                }
            },
            "agent": "SignalCorrelator",
            "extraction_model": "deterministic_rules",
            "review_status": review_status
        }
