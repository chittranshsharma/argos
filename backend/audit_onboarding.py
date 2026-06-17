"""
Sprint X: Search Any Company Audit
Measures onboarding latency and reliability for new companies.
"""

import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.database import get_supabase_client
from app.discovery.auto_discover import AutoDiscoverer
from app.agents.github_agent import GitHubAgent
from app.agents.news_agent import NewsAgent
from app.agents.hackernews_agent import HackerNewsAgent
from app.agents.jobs_agent import JobsAgent
from app.agents.executive_agent import ExecutiveAgent
from app.agents.funding_agent import FundingAgent
from app.agents.launch_agent import LaunchAgent
from app.agents.partnership_agent import PartnershipsAgent
from app.agents.linkedin_agent import LinkedInAgent
from app.analysis.hypothesis_engine import HypothesisEngine

logging.basicConfig(level=logging.WARNING)

TEST_COMPANIES = [
    {"name": "Nvidia", "website": "https://www.nvidia.com"},
    {"name": "Figma", "website": "https://www.figma.com"},
    {"name": "Stripe", "website": "https://stripe.com"},
    {"name": "Anthropic", "website": "https://www.anthropic.com"},
    {"name": "Perplexity", "website": "https://www.perplexity.ai"},
    {"name": "Lovable", "website": "https://lovable.dev"} # Small startup
]

def run_audit():
    print(f"{'='*60}")
    print("  ONBOARDING PIPELINE AUDIT")
    print(f"{'='*60}")

    # For testing, we mock the DB id
    mock_company_id = "00000000-0000-0000-0000-000000000000"

    total_results = []

    for co in TEST_COMPANIES:
        name = co["name"]
        website = co["website"]
        
        print(f"\n--- Searching: {name} ---")
        metrics = {
            "company": name,
            "discovery_time": 0,
            "collection_time": 0,
            "hypothesis_time": 0,
            "total_time": 0,
            "agent_times": {},
            "total_signals": 0,
            "total_hypotheses": 0,
            "llm_stats": {},
            "failures": []
        }
        
        # Reset LLM Stats
        from app.llm import LLM_STATS
        LLM_STATS["calls"] = 0
        LLM_STATS["total_time"] = 0.0
        LLM_STATS["retries"] = 0
        LLM_STATS["rate_limits"] = 0
        
        t0 = time.time()
        
        # 1. Discovery
        print("  Running AutoDiscoverer...")
        t_disc_start = time.time()
        discoverer = AutoDiscoverer()
        try:
            sources = discoverer.discover(name, website)
        except Exception as e:
            sources = {}
            metrics["failures"].append(f"Discovery Failed: {e}")
        metrics["discovery_time"] = time.time() - t_disc_start
        
        print(f"    Discovered: {sources}")

        # 2. Collection
        print("  Running Agents (max_workers=8)...")
        tasks = []
        if sources.get("github_org"):
            tasks.append(("github", GitHubAgent().collect, {"github_org": sources["github_org"], "company_name": name, "company_id": mock_company_id}))
        if sources.get("news_keywords"):
            tasks.append(("news", NewsAgent().collect, {"keywords": sources["news_keywords"], "company_name": name, "company_id": mock_company_id}))
        tasks.append(("hackernews", HackerNewsAgent().collect, {"company_name": name, "company_id": mock_company_id}))
        if sources.get("careers_url"):
            tasks.append(("jobs", JobsAgent().collect, {"careers_url": sources["careers_url"], "company_name": name, "company_id": mock_company_id}))
        tasks.append(("executive", ExecutiveAgent().collect, {"company_name": name, "company_id": mock_company_id}))
        tasks.append(("funding", FundingAgent().collect, {"company_name": name, "company_id": mock_company_id}))
        tasks.append(("launch", LaunchAgent().collect, {"company_name": name, "company_id": mock_company_id, "producthunt_slug": sources.get("producthunt_slug")}))
        tasks.append(("partnerships", PartnershipsAgent().collect, {"company_name": name, "company_id": mock_company_id}))
        if sources.get("linkedin_url"):
            tasks.append(("linkedin", LinkedInAgent().collect, {"linkedin_url": sources["linkedin_url"], "company_name": name, "company_id": mock_company_id}))

        t_col_start = time.time()
        all_signals = []
        
        # Track futures instead of sequential execution
        with ThreadPoolExecutor(max_workers=8) as executor:
            future_to_name = {}
            for task_name, func, kwargs in tasks:
                future_to_name[executor.submit(func, **kwargs)] = task_name
                
            for future in as_completed(future_to_name):
                task_name = future_to_name[future]
                # We can't measure individual block time easily without a wrapper, so we'll just track completion.
                try:
                    res = future.result()
                    if res:
                        all_signals.extend(res)
                    metrics["agent_times"][task_name] = time.time() - t_col_start
                    print(f"    - {task_name} finished.")
                except Exception as e:
                    metrics["failures"].append(f"Agent {task_name} failed: {e}")
                    print(f"    - {task_name} FAILED: {e}")
                
        metrics["collection_time"] = time.time() - t_col_start
        metrics["total_signals"] = len(all_signals)

        # 3. Hypothesis Generation
        print("  Running Hypothesis Engine...")
        t_hyp_start = time.time()
        engine = HypothesisEngine()
        try:
            if all_signals:
                hypotheses = engine.generate_hypotheses(mock_company_id, name, all_signals, "Search Company Audit")
                metrics["total_hypotheses"] = len(hypotheses) if hypotheses else 0
            else:
                metrics["total_hypotheses"] = 0
        except Exception as e:
            metrics["failures"].append(f"Hypothesis Engine Failed: {e}")
        metrics["hypothesis_time"] = time.time() - t_hyp_start
        
        # Capture LLM Stats
        metrics["llm_stats"] = dict(LLM_STATS)

        metrics["total_time"] = time.time() - t0
        total_results.append(metrics)
        
        print(f"  Result: {metrics['total_signals']} signals -> {metrics['total_hypotheses']} hypotheses in {metrics['total_time']:.1f}s")
        if metrics["failures"]:
            print(f"  Failures: {metrics['failures']}")

    # Final Report
    print(f"\n\n{'='*60}")
    print("  ONBOARDING LATENCY REPORT")
    print(f"{'='*60}")
    
    for r in total_results:
        print(f"\n{r['company'].upper()} ({r['total_time']:.1f}s total)")
        print(f"  Discovery:   {r['discovery_time']:.1f}s")
        print(f"  Collection:  {r['collection_time']:.1f}s  [{r['total_signals']} signals]")
        
        # Sort agents by longest time
        sorted_agents = sorted(r['agent_times'].items(), key=lambda x: x[1], reverse=True)
        for aname, atime in sorted_agents[:3]:
            print(f"    - {aname}: {atime:.1f}s")
            
        print(f"  Hypothesis:  {r['hypothesis_time']:.1f}s  [{r['total_hypotheses']} hypotheses]")
        print(f"  LLM Bottleneck:")
        print(f"    - Calls: {r['llm_stats']['calls']}")
        print(f"    - Time:  {r['llm_stats']['total_time']:.1f}s")
        print(f"    - Rate limits: {r['llm_stats']['rate_limits']}")
        print(f"    - Retries: {r['llm_stats']['retries']}")
        if r['failures']:
            print(f"  Failures:")
            for f in r['failures']:
                print(f"    ! {f}")

if __name__ == "__main__":
    run_audit()
