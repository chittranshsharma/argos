"""
Argos — Hypothesis Audit (Human Review Pack)
Pulls active hypotheses and their evaluations to generate a markdown review pack.
This is used to manually grade Precision, Novelty, Actionability, and Stability.
"""

import os
import json
import logging
from datetime import datetime, timezone
from app.database import get_supabase_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_review_pack():
    client = get_supabase_client()
    logger.info("Fetching active hypotheses...")
    
    # Get active hypotheses
    res = client.table("hypotheses").select("*, companies(name)").eq("status", "ACTIVE").limit(25).execute()
    hypotheses = res.data or []
    
    if not hypotheses:
        logger.info("No active hypotheses found to review.")
        return
    
    pack_lines = ["# Hypothesis Human Review Pack\n"]
    pack_lines.append(f"Generated at: {datetime.now(timezone.utc).isoformat()}\n")
    pack_lines.append("## Grading Criteria:")
    pack_lines.append("- **Precision:** Is the narrative mathematically supported by the evidence?")
    pack_lines.append("- **Novelty:** Does it tell us something beyond just re-stating the signals?")
    pack_lines.append("- **Actionability:** Is it specific enough to base a business decision on?")
    pack_lines.append("- **Stability:** Does the confidence evolve logically or bounce randomly?\n")
    pack_lines.append("---\n")
    
    for h in hypotheses:
        c_name = h.get("companies", {}).get("name", "Unknown")
        hid = h["id"]
        
        # Get evaluations
        evals_res = client.table("hypothesis_evaluations").select("*, signals(title)").eq("hypothesis_id", hid).order("created_at", desc=True).execute()
        evals = evals_res.data or []
        
        # Get snapshots for stability
        snaps_res = client.table("hypothesis_snapshots").select("*").eq("hypothesis_id", hid).order("captured_at", desc=False).execute()
        snaps = snaps_res.data or []
        
        pack_lines.append(f"### Company: {c_name}")
        pack_lines.append(f"**Hypothesis:** {h['title']}")
        pack_lines.append(f"**Type:** {h['type']}")
        pack_lines.append(f"**Current Confidence:** {h['confidence']}")
        
        # Drift status
        last_ev_str = h.get("last_evidence_at")
        if last_ev_str:
            days_old = (datetime.now(timezone.utc) - datetime.fromisoformat(last_ev_str)).days
            if days_old > 45:
                pack_lines.append(f"**Drift Status:** STALE ({days_old} days without evidence)")
            elif days_old > 21:
                pack_lines.append(f"**Drift Status:** AGING ({days_old} days without evidence)")
            else:
                pack_lines.append(f"**Drift Status:** ACTIVE")
        else:
            pack_lines.append(f"**Drift Status:** NO EVIDENCE YET")
        
        # Snapshot trajectory
        if snaps:
            traj = " → ".join([str(s["confidence"]) for s in snaps])
            pack_lines.append(f"\n**Stability Trajectory:**\n{traj}")
        else:
            pack_lines.append("\n**Stability Trajectory:** None (New)")
            
        # Evidence Trail
        pack_lines.append("\n**Evidence Trail:**")
        if evals:
            for ev in evals:
                impact_str = f"+{ev['impact']}" if ev['impact'] > 0 else str(ev['impact'])
                sig_title = ev.get("signals", {}).get("title", "Unknown Signal") if ev.get("signals") else "Unknown Signal"
                pack_lines.append(f"- {impact_str} {sig_title}")
                pack_lines.append(f"  *Reasoning: {ev['reasoning']}*")
        else:
            pack_lines.append("- No evaluations yet.")
            
        pack_lines.append("\n---\n")
        
    out_file = "hypothesis_review_pack.md"
    with open(out_file, "w") as f:
        f.write("\n".join(pack_lines))
        
    logger.info(f"Review pack generated: {out_file}")

if __name__ == "__main__":
    generate_review_pack()
