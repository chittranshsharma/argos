import json
import logging
from dotenv import load_dotenv

from app.database import get_supabase_client

load_dotenv(override=True)
logging.basicConfig(level=logging.WARNING)

def run():
    client = get_supabase_client()
    
    res = client.table("analytics_snapshots").select("*").eq("metric_type", "rejected_hypothesis_create").order("timestamp", desc=True).limit(20).execute()
    
    snapshots = res.data
    
    if not snapshots:
        print("No rejected CREATE actions found.")
        return
        
    print(f"Found {len(snapshots)} recent rejected CREATE actions.\n")
    
    for snap in snapshots:
        data = snap.get("payload_json", {})
        action = data.get("action", {})
        scores = data.get("scores", {})
        
        belief = action.get("belief", "Unknown")
        gen_score = scores.get("genericity_score", "N/A")
        fals_score = scores.get("falsifiability_score", "N/A")
        ceo_score = scores.get("ceo_score", "N/A")
        opp_score = scores.get("opposite_score", "N/A")
        
        reason = data.get("reason", "Unknown")
        
        supporting = action.get("supporting_signals", [])
        counter = action.get("counter_evidence", [])
        
        print("=" * 50)
        print("Candidate")
        print("=========\n")
        print("Text:")
        print(f"{belief}\n")
        print("Scores:")
        print(f"* Genericity: {gen_score}")
        print(f"* Falsifiability: {fals_score}")
        print(f"* CEO Test: {ceo_score}")
        
        try:
            overall = (gen_score + fals_score + ceo_score + opp_score) / 4.0
            print(f"* Overall: {overall:.2f}")
        except Exception:
            pass
            
        print("\nRejected because:")
        # split reasoning by newlines or sentences if it's long, or just print
        print(f"{reason}\n")
        
        print("Supporting evidence:")
        for ev in supporting:
            print(f"* {ev}")
            
        print("\nCounter evidence:")
        for ev in counter:
            print(f"* {ev}")
            
        print("\n" + "=" * 50 + "\n")

if __name__ == "__main__":
    run()
