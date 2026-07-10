"""
P0 Backfill: Parse prediction fields out of hypothesis description markdown
and write them back to the structured columns.

This is a one-time migration for all existing hypotheses created before
the P0 fix to hypothesis_engine.py. After running this, run
verify_p0_finding1.py again to confirm field population.

Run from backend/ directory:
    .venv\Scripts\python.exe backfill_prediction_fields.py

The script is safe to re-run — it skips rows that already have
prediction_event set.
"""
import sys, os, re, json, logging
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
os.chdir(script_dir)
from dotenv import load_dotenv
load_dotenv()

from app.database import get_supabase_client
from app.llm import get_groq_llm, llm_invoke

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

client = get_supabase_client()

print("\n" + "="*70)
print("  P0 BACKFILL: Structured prediction fields")
print("="*70)

# Fetch all hypotheses missing prediction_event
res = client.table("hypotheses").select(
    "id, title, description, prediction_event, prediction_deadline_days, status"
).is_("prediction_event", "null").execute()

rows = res.data or []
already_have = client.table("hypotheses").select("id").not_.is_("prediction_event", "null").execute()
print(f"\nTotal hypotheses without prediction_event: {len(rows)}")
print(f"Already have prediction_event:             {len(already_have.data or [])}")

if not rows:
    print("\nNothing to backfill. All hypotheses already have prediction_event set.")
    sys.exit(0)

# Use LLM to extract prediction fields from the description markdown
llm = get_groq_llm(max_tokens=400)

def extract_prediction_fields(title: str, description: str) -> dict:
    """Ask the LLM to extract structured prediction fields from description markdown."""
    prompt = f"""You are parsing an existing strategic hypothesis record to extract structured prediction fields.

HYPOTHESIS TITLE (this is the strategic interpretation/belief):
{title}

HYPOTHESIS DESCRIPTION (contains embedded prediction in markdown):
{description[:1500]}

Extract the following fields from the description. The description contains a section called "**Prediction**:" with Event, Target, Deadline, and Measurement.

Return ONLY valid JSON:
{{
  "prediction_event": "<the action verb and subject, e.g. 'launch', 'acquire', 'announce'> OR empty string if not found",
  "prediction_target": "<the specific product, entity, or metric> OR empty string if not found",
  "prediction_deadline_days": <integer number of days, e.g. 90> OR null if not found,
  "prediction_measurement": "<the specific observable condition> OR empty string if not found"
}}

If the description says 'N/A' for deadline, output null. If no prediction section exists, output empty strings and null."""
    try:
        response = llm_invoke(llm, prompt)
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        logger.error(f"LLM extraction failed: {e}")
    return {
        "prediction_event": "",
        "prediction_target": "",
        "prediction_deadline_days": None,
        "prediction_measurement": ""
    }

updated = 0
skipped = 0
failed = 0

for row in rows:
    hyp_id = row["id"]
    title = row.get("title", "")[:80]
    description = row.get("description", "") or ""

    if not description.strip():
        logger.info(f"Skip {hyp_id[:8]} — no description to parse")
        skipped += 1
        continue

    logger.info(f"Extracting fields for {hyp_id[:8]} ({title[:50]})")
    fields = extract_prediction_fields(title, description)

    # Validate — don't write garbage
    pred_event = str(fields.get("prediction_event") or "").strip()
    pred_target = str(fields.get("prediction_target") or "").strip()
    pred_days = fields.get("prediction_deadline_days")
    pred_measure = str(fields.get("prediction_measurement") or "").strip()

    # Coerce deadline to int if possible
    try:
        pred_days = int(pred_days) if pred_days is not None else None
    except (ValueError, TypeError):
        pred_days = None

    update_payload = {}
    if pred_event:
        update_payload["prediction_event"] = pred_event
    if pred_target:
        update_payload["prediction_target"] = pred_target
    if pred_days is not None:
        update_payload["prediction_deadline_days"] = pred_days
    if pred_measure:
        update_payload["prediction_measurement"] = pred_measure

    if not update_payload:
        logger.warning(f"  No extractable prediction fields in {hyp_id[:8]} — marking as unstructured")
        update_payload["prediction_event"] = ""  # explicit empty so we know it was attempted
        skipped += 1
        continue

    try:
        client.table("hypotheses").update(update_payload).eq("id", hyp_id).execute()
        logger.info(f"  Updated {hyp_id[:8]}: event='{pred_event[:40]}' deadline={pred_days}")
        updated += 1
    except Exception as e:
        logger.error(f"  DB update failed for {hyp_id[:8]}: {e}")
        failed += 1

    import time
    time.sleep(1.0)  # rate limit

print("\n" + "-"*70)
print(f"Backfill complete.")
print(f"  Updated: {updated}")
print(f"  Skipped (no parseable prediction): {skipped}")
print(f"  Errors:  {failed}")
print()
print("Run verify_p0_finding1.py to confirm population rates.")
print("="*70 + "\n")
