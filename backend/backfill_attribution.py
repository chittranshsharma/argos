"""
Argos — Signal Attribution Backfill Migration Script
Re-evaluates all historical signals using the new Deterministic Attribution Engine rules.
"""

import os
import sys
import logging
import statistics
from tqdm import tqdm

# Insert current working directory to path to allow importing app modules
sys.path.insert(0, os.getcwd())

from app.database import get_supabase_client, get_all_companies
from app.signals.attribution_engine import AttributionEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def map_confidence_to_type(conf: float) -> str:
    """Helper to map a raw confidence value (0.0 - 1.0) to type categories for baseline."""
    if conf is None or conf == "":
        return "NOISE"
    try:
        conf = float(conf)
    except ValueError:
        return "NOISE"
        
    if conf >= 0.80:
        return "DIRECT"
    elif conf >= 0.50:
        return "PARTNER"
    elif conf >= 0.20:
        return "INDUSTRY"
    else:
        return "NOISE"

def run_backfill():
    client = get_supabase_client()
    
    print("Fetching active companies for domain routing...")
    companies = get_all_companies()
    company_map = {c["id"]: c for c in companies if c.get("id")}
    company_names = [c["name"] for c in companies if c.get("name")]
    
    print("Initializing Deterministic Attribution Engine...")
    engine = AttributionEngine(portfolio_companies=company_names)
    
    print("Fetching all historical signals from Supabase...")
    # Fetch all signals in batches if too large, but up to 2000 is fine
    response = client.table("signals").select("*").limit(3000).execute()
    signals = response.data or []
    
    if not signals:
        print("No signals found in the database to backfill.")
        return
        
    print(f"Retrieved {len(signals)} signals. Preparing statistics...")
    
    # 1. Compute BEFORE Stats
    before_confidences = []
    before_categories = {"DIRECT": 0, "PARTNER": 0, "INDUSTRY": 0, "NOISE": 0}
    
    for s in signals:
        raw = s.get("raw_data", {})
        # Check existing attribution confidence or fallback to signal's general confidence
        conf = raw.get("attribution_confidence") or s.get("confidence")
        if conf is not None and conf != "":
            try:
                before_confidences.append(float(conf))
            except ValueError:
                pass
        else:
            before_confidences.append(0.0)
            
        attr_type = raw.get("attribution_type") or map_confidence_to_type(conf)
        before_categories[attr_type] = before_categories.get(attr_type, 0) + 1
        
    before_avg = sum(before_confidences) / len(before_confidences) if before_confidences else 0.0
    before_med = statistics.median(before_confidences) if before_confidences else 0.0
    
    # 2. Process and Update Signals (AFTER)
    after_confidences = []
    after_categories = {"DIRECT": 0, "PARTNER": 0, "INDUSTRY": 0, "NOISE": 0}
    
    print("Processing attribution re-scoring for all signals...")
    updated_count = 0
    
    for s in tqdm(signals):
        co_id = s.get("company_id")
        co_info = company_map.get(co_id, {})
        website = co_info.get("website")
        co_name = s.get("company_name") or co_info.get("name") or "Unknown"
        
        # Calculate new attribution
        attr_meta = engine.calculate_attribution(
            title=s.get("title", ""),
            description=s.get("description", ""),
            url=s.get("url", ""),
            company_name=co_name,
            website=website
        )
        
        # Update raw_data
        raw_data = s.get("raw_data", {}) or {}
        # Merge new attribution values
        raw_data.update(attr_meta)
        
        # Collect AFTER statistics
        conf = attr_meta["attribution_confidence"]
        after_confidences.append(conf)
        after_categories[attr_meta["attribution_type"]] += 1
        
        # Update database record
        try:
            client.table("signals").update({"raw_data": raw_data}).eq("id", s["id"]).execute()
            updated_count += 1
        except Exception as e:
            logger.error(f"Failed to update signal ID {s['id']}: {e}")
            
    after_avg = sum(after_confidences) / len(after_confidences) if after_confidences else 0.0
    after_med = statistics.median(after_confidences) if after_confidences else 0.0
    
    # 3. Print Comparison Report
    print("\n" + "="*50)
    print("        ARGOS ATTRIBUTION MIGRATION REPORT")
    print("="*50)
    print(f"Total Signals Processed: {len(signals)}")
    print(f"Successfully Updated:    {updated_count}")
    print("-"*50)
    print("DISTRIBUTION COMPARISON:")
    print(f"{'Category':<15} | {'BEFORE % (Count)':<20} | {'AFTER % (Count)':<20}")
    print("-"*50)
    for cat in ["DIRECT", "PARTNER", "INDUSTRY", "NOISE"]:
        b_count = before_categories.get(cat, 0)
        b_pct = (b_count / len(signals)) * 100
        
        a_count = after_categories.get(cat, 0)
        a_pct = (a_count / len(signals)) * 100
        
        print(f"{cat:<15} | {b_pct:>5.1f}% ({b_count:<5d})       | {a_pct:>5.1f}% ({a_count:<5d})")
    print("-"*50)
    print("CONFIDENCE STATS:")
    print(f"  - Average Confidence: {before_avg:.2f} (Before) -> {after_avg:.2f} (After)")
    print(f"  - Median Confidence:  {before_med:.2f} (Before) -> {after_med:.2f} (After)")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_backfill()
