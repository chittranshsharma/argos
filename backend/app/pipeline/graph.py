"""
Argos — Pipeline Graph
LangGraph StateGraph wiring all monitoring pipeline nodes.
"""

from langgraph.graph import StateGraph, END

from app.pipeline.state import AgentState
from app.pipeline.nodes import (
    collect_signals_node,
    filter_new_signals_node,
    analyze_signals_node,
    compute_analytics_node,
    store_graph_node,
    generate_report_node,
    generate_alerts_node,
)


def build_monitoring_graph() -> StateGraph:
    """
    Build the LangGraph monitoring pipeline:
    collect → filter → analyze → store_graph → report → alerts
    """
    return None