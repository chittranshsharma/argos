import time
import inspect
import sys
import logging
from collections import defaultdict
import uuid

import app.llm
from app.database import get_supabase_client

logging.basicConfig(level=logging.WARNING)

LLM_AUDIT_STATS = defaultdict(lambda: {"calls": 0, "total_time": 0.0, "retries": 0, "rate_limits": 0})

original_llm_invoke = app.llm.llm_invoke

def patched_llm_invoke(llm, prompt: str) -> str:
    component = "Unknown"
    is_relevance_check = False
    
    for frame_info in inspect.stack():
        filename = frame_info.filename
        func_name = frame_info.function
        
        if "_check_relevance" in func_name:
            is_relevance_check = True
            
        if "funding_agent.py" in filename:
            component = "FundingAgent"
        elif "executive_agent.py" in filename:
            component = "ExecutiveAgent"
        elif "partnership_agent.py" in filename:
            component = "PartnershipsAgent"
        elif "hypothesis_engine.py" in filename:
            component = "HypothesisEngine"
        elif "discoverer.py" in filename or "auto_discoverer" in filename.lower():
            component = "AutoDiscoverer"
        elif "competitor_mapper.py" in filename:
            component = "CompetitorMapper"
        
        if component != "Unknown":
            break
            
    if is_relevance_check:
        component = "Relevance Guardrails"

    calls_before = app.llm.LLM_STATS["calls"]
    retries_before = app.llm.LLM_STATS["retries"]
    rl_before = app.llm.LLM_STATS["rate_limits"]
    
    t0 = time.time()
    try:
        response = original_llm_invoke(llm, prompt)
    finally:
        t1 = time.time()
        calls_diff = app.llm.LLM_STATS["calls"] - calls_before
        retries_diff = app.llm.LLM_STATS["retries"] - retries_before
        rl_diff = app.llm.LLM_STATS["rate_limits"] - rl_before
        time_diff = t1 - t0
        
        LLM_AUDIT_STATS[component]["calls"] += 1
        LLM_AUDIT_STATS[component]["retries"] += retries_diff
        LLM_AUDIT_STATS[component]["rate_limits"] += rl_diff
        LLM_AUDIT_STATS[component]["total_time"] += time_diff

    return response

app.llm.llm_invoke = patched_llm_invoke

def run_audit():
    client = get_supabase_client()
    
    companies = ["Nvidia", "Stripe", "Figma", "Anthropic"]
    print(f"Running LLM Call Audit for {len(companies)} companies...\n")
    
    from app.discovery.auto_discover import AutoDiscoverer
    from app.discovery.competitor_mapper import CompetitorMapper
    from app.pipeline.graph import monitoring_graph
    
    for c in companies:
        print(f"--- Onboarding {c} ---")
        
        existing = client.table("companies").select("*").eq("name", c).execute()
        if existing.data:
            client.table("companies").delete().eq("name", c).execute()
            
        company_id = str(uuid.uuid4())
        company_data = {
            "id": company_id,
            "name": c,
            "website": f"https://www.{c.lower()}.com",
            # "status": "DISCOVERED" -> checking schema if status exists
        }
        
        # We'll just pass basic data
        try:
            client.table("companies").insert(company_data).execute()
        except Exception as e:
            print(f"Failed to insert mock company: {e}")
        
        try:
            discoverer = AutoDiscoverer()
            sources = discoverer.discover(company_data["name"], company_data.get("website", ""))
            company_data.update(sources)
        except Exception as e:
            print(f"AutoDiscoverer failed: {e}")
            
        try:
            mapper = CompetitorMapper()
            competitors = mapper.discover_competitors(company_data["name"], company_data.get("website", ""))
        except Exception as e:
            print(f"CompetitorMapper failed: {e}")
            
        initial_state = {
            "company_id": company_id,
            "company_name": company_data["name"],
            "company_data": company_data,
            "raw_signals": [],
            "new_signals": [],
            "analysis": {},
            "key_findings": [],
            "hiring_trends": [],
            "tech_signals": [],
            "report": "",
            "alerts": [],
            "entities": [],
            "relationships": [],
        }
        
        try:
            monitoring_graph.invoke(initial_state)
        except Exception as e:
            print(f"Graph pipeline failed: {e}")
            
        print(f"Finished {c}\n")
        
    print("\n=== SPRINT X.2: LLM CALL AUDIT RESULTS ===")
    print(f"{'Component':<25} | {'Calls':<6} | {'Retries':<8} | {'429s':<5} | {'Total Time (s)':<15} | {'Avg Time (s)':<12}")
    print("-" * 80)
    
    sorted_stats = sorted(LLM_AUDIT_STATS.items(), key=lambda x: x[1]["total_time"], reverse=True)
    
    for comp, stats in sorted_stats:
        calls = stats["calls"]
        retries = stats["retries"]
        rl = stats["rate_limits"]
        tt = stats["total_time"]
        avg = tt / calls if calls > 0 else 0
        
        print(f"{comp:<25} | {calls:<6} | {retries:<8} | {rl:<5} | {tt:<15.2f} | {avg:<12.2f}")
        
    with open("audit_llm_results.txt", "w") as f:
        f.write("=== SPRINT X.2: LLM CALL AUDIT RESULTS ===\n")
        f.write(f"{'Component':<25} | {'Calls':<6} | {'Retries':<8} | {'429s':<5} | {'Total Time (s)':<15} | {'Avg Time (s)':<12}\n")
        f.write("-" * 80 + "\n")
        for comp, stats in sorted_stats:
            calls = stats["calls"]
            retries = stats["retries"]
            rl = stats["rate_limits"]
            tt = stats["total_time"]
            avg = tt / calls if calls > 0 else 0
            f.write(f"{comp:<25} | {calls:<6} | {retries:<8} | {rl:<5} | {tt:<15.2f} | {avg:<12.2f}\n")

if __name__ == "__main__":
    run_audit()
