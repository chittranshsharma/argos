"""
Argos — Pipeline Graph
LangGraph StateGraph wiring all monitoring pipeline nodes.
"""

from langgraph.graph import StateGraph, END

from app.pipeline.state import AgentState
from app.pipeline.nodes import (
    collect_signals_node,
    filter_new_signals_node,
    correlate_signals_node,
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
    workflow = StateGraph(AgentState)

    # ── Add nodes ───────────────────────────────────────────
    workflow.add_node("collect_signals", collect_signals_node)
    workflow.add_node("filter_new", filter_new_signals_node)
    workflow.add_node("correlate", correlate_signals_node)
    workflow.add_node("analyze", analyze_signals_node)
    workflow.add_node("compute_analytics", compute_analytics_node)
    workflow.add_node("store_graph", store_graph_node)
    workflow.add_node("generate_report", generate_report_node)
    workflow.add_node("generate_alerts", generate_alerts_node)

    # ── Define edges ────────────────────────────────────────
    workflow.set_entry_point("collect_signals")
    workflow.add_edge("collect_signals", "filter_new")
    workflow.add_edge("filter_new", "correlate")
    workflow.add_edge("correlate", "analyze")
    workflow.add_edge("analyze", "compute_analytics")
    workflow.add_edge("compute_analytics", "store_graph")
    workflow.add_edge("store_graph", "generate_report")
    workflow.add_edge("generate_report", "generate_alerts")
    workflow.add_edge("generate_alerts", END)

    return workflow.compile()


# Export compiled graph
monitoring_graph = build_monitoring_graph()