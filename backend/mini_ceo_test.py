import sys
import logging
from dotenv import load_dotenv

from app.database import get_all_companies, get_supabase_client

load_dotenv(override=True)
logging.basicConfig(level=logging.WARNING)
# Force UTF-8 output so special chars don't crash on Windows console
sys.stdout.reconfigure(encoding='utf-8')

TARGETS = ["OpenAI", "Anthropic"]

def run():
    client = get_supabase_client()
    companies = get_all_companies()
    target_comps = [c for c in companies if c["name"] in TARGETS]

    for c in target_comps:
        name = c["name"]
        cid  = c["id"]

        res = (
            client.table("hypotheses")
            .select("*")
            .eq("company_id", cid)
            .eq("status", "ACTIVE")
            .order("created_at", desc=True)
            .limit(5)
            .execute()
        )
        hyps = res.data or []

        print(f"\n{'='*72}")
        print(f"  MINI CEO TEST: {name}  ({len(hyps)} active hypotheses)")
        print(f"{'='*72}")

        for i, h in enumerate(hyps, 1):
            desc = h.get("description", "")

            # Parse sections out of the markdown description
            def extract_section(label, text):
                import re
                pattern = rf"\*\*{re.escape(label)}\*\*:\n(.*?)(?=\n\n\*\*|\Z)"
                m = re.search(pattern, text, re.DOTALL)
                return m.group(1).strip() if m else "(not found)"

            observation  = extract_section("Observation",        desc)
            tradeoff     = extract_section("Strategic Trade-off", desc)
            prediction   = extract_section("Prediction",         desc)
            counter      = extract_section("Counter-evidence",   desc)
            support      = extract_section("Supporting Evidence",desc)
            confidence   = h.get("confidence", "?")
            created_at   = h.get("created_at", "")[:10]

            print(f"\nHypothesis {i}  [confidence={confidence}  created={created_at}]")
            print(f"Title: {h.get('title', '')}\n")
            if observation != "(not found)":
                print(f"Observation:\n{observation}\n")
            print(f"Interpretation / Trade-off:\n{tradeoff}\n")
            print(f"Prediction:\n{prediction}\n")
            print(f"Supporting Evidence:\n{support}\n")
            print(f"Counter Evidence:\n{counter}\n")
            print("-" * 72)

if __name__ == "__main__":
    run()
