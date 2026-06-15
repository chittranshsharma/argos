"""
Argos — Pipeline State
TypedDict defining the state that flows through the LangGraph pipeline.
"""

from typing import TypedDict


class AgentState(TypedDict):
    """State flowing through the monitoring pipeline."""

    # ── Company Info ────────────────────────────────────────
    company_id: str
    company_name: str
    company_data: dict

    # ── Signals ─────────────────────────────────────────────
    raw_signals: list[dict]
    new_signals: list[dict]

    # ── Analysis ────────────────────────────────────────────
    analysis: dict
    key_findings: list[str]
    hiring_trends: list[dict]
    tech_signals: list[dict]

    # ── Report ──────────────────────────────────────────────
    report: str

    # ── Alerts ──────────────────────────────────────────────
    alerts: list[dict]

    # ── Knowledge Graph ─────────────────────────────────────
    entities: list[dict]
    relationships: list[dict]