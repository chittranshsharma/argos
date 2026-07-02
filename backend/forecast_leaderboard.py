"""
Argos — Forecast Leaderboard Utility
Queries and displays historical resolved predictions from the database
to measure hit rates and track forecasting quality by horizon.
"""

import os
import sys
from datetime import datetime

# Insert backend folder to path
sys.path.insert(0, os.path.join(os.getcwd(), "backend"))

from app.database import get_supabase_client

def calculate_horizon_days(created_at_str: str, deadline_days: int) -> str:
    """Classify the horizon based on deadline days."""
    try:
        days = int(deadline_days)
    except (ValueError, TypeError):
        return "Unknown"
        
    if days <= 7:
        return "7d"
    elif days <= 30:
        return "30d"
    elif days <= 90:
        return "90d"
    else:
        return f"{days}d"

def run_leaderboard():
    print("Connecting to Supabase...")
    client = get_supabase_client()
    
    # Query prediction outcomes joined with hypotheses
    # prediction_outcomes has foreign key to hypotheses (hypothesis_id or stored in hypotheses)
    print("Querying resolved prediction outcomes...")
    res = client.table("prediction_outcomes").select("id, status, confidence, resolved_at, hypotheses(*)").execute()
    rows = res.data or []
    
    if not rows:
        print("No prediction outcomes found in database.")
        return
        
    # We filter for resolved prediction outcomes
    # Terminal states: CONFIRMED, INCORRECT, EXPIRED
    resolved_outcomes = []
    active_outcomes = []
    
    for r in rows:
        status = r.get("status")
        hyp = r.get("hypotheses") or {}
        if not hyp:
            continue
            
        created_at = hyp.get("created_at", "")
        deadline_days = hyp.get("prediction_deadline_days", 30)
        horizon = calculate_horizon_days(created_at, deadline_days)
        
        item = {
            "forecast_id": r["id"],
            "company": hyp.get("title", "Unknown")[:25],
            "company_name": hyp.get("company_name", "Unknown"),
            "status": status,
            "confidence": r.get("confidence", 0.0),
            "horizon": horizon,
            "created_at": created_at[:10] if created_at else "N/A"
        }
        
        if status in ["CONFIRMED", "INCORRECT", "EXPIRED"]:
            resolved_outcomes.append(item)
        else:
            active_outcomes.append(item)
            
    print("\n" + "="*80)
    print("                      ARGOS FORECAST LEADERBOARD")
    print("="*80)
    
    # Print active summary
    print(f"Active Forecasts:   {len(active_outcomes)}")
    print(f"Resolved Forecasts: {len(resolved_outcomes)}")
    print("-"*80)
    
    # Print resolved table
    if resolved_outcomes:
        print(f"{'Forecast ID':<38} | {'Company':<15} | {'Horizon':<7} | {'Outcome':<12} | {'Conf':<5}")
        print("-"*80)
        
        counts = {"CONFIRMED": 0, "INCORRECT": 0, "EXPIRED": 0}
        horizon_stats = {}
        
        for item in resolved_outcomes:
            status = item["status"]
            horizon = item["horizon"]
            
            # Print row safely
            print(f"{item['forecast_id']:<38} | {item['company_name']:<15} | {horizon:<7} | {status:<12} | {item['confidence']:.2f}")
            
            # Stats tracking
            if status in counts:
                counts[status] += 1
                
            if horizon not in horizon_stats:
                horizon_stats[horizon] = {"confirmed": 0, "total": 0}
            if status in ["CONFIRMED", "INCORRECT"]:
                horizon_stats[horizon]["total"] += 1
                if status == "CONFIRMED":
                    horizon_stats[horizon]["confirmed"] += 1
                    
        print("-"*80)
        total_decisive = counts["CONFIRMED"] + counts["INCORRECT"]
        hit_rate = (counts["CONFIRMED"] / total_decisive * 100) if total_decisive > 0 else 0.0
        
        print("SUMMARY STATISTICS:")
        print(f"  - CONFIRMED:    {counts['CONFIRMED']}")
        print(f"  - INCORRECT:    {counts['INCORRECT']}")
        print(f"  - EXPIRED:      {counts['EXPIRED']}")
        print(f"  - Decisive Hit Rate: {hit_rate:.1f}% ({counts['CONFIRMED']}/{total_decisive})")
        print("-"*80)
        print("ACCURACY BY HORIZON:")
        for hor, stats in sorted(horizon_stats.items()):
            h_rate = (stats["confirmed"] / stats["total"] * 100) if stats["total"] > 0 else 0.0
            print(f"  - {hor:<5}: {h_rate:>5.1f}% ({stats['confirmed']}/{stats['total']} resolved)")
    else:
        print("No resolved outcomes found yet to compute statistics.")
        
    print("="*80 + "\n")

if __name__ == "__main__":
    run_leaderboard()
