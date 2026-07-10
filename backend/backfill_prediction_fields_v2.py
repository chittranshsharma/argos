"""
P0 Backfill v2: Parse prediction fields from description markdown via regex.
No LLM needed — the structured prediction block is already present in the descriptions.

Run from backend/ directory:
    .venv\Scripts\python.exe backfill_prediction_fields_v2.py
"""
import sys, os, re, logging
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
os.chdir(script_dir)
from dotenv import load_dotenv
load_dotenv()

from app.database import get_supabase_client

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

client = get_supabase_client()

print("\n" + "="*70)
print("  P0 BACKFILL v2: Regex extraction from description markdown")
print("="*70)

# Fetch all hypotheses missing prediction_event
res = client.table("hypotheses").select(
    "id, title, description, prediction_event"
).is_("prediction_event", "null").execute()
rows = res.data or []

print(f"\nHypotheses missing prediction_event: {len(rows)}")
if not rows:
    print("Nothing to backfill.")
    sys.exit(0)


def extract_from_markdown(description: str) -> dict:
    """
    Parse the structured prediction block embedded in the description markdown.
    The format written by hypothesis_engine.py is:
        Event: <text>
        Target: <text>
        Deadline: <N> days
        Measurement: <text>
    """
    if not description:
        return {}

    result = {}

    # prediction_event — line starting with "Event:"
    m = re.search(r"(?:^|\n)\s*Event:\s*(.+)", description, re.IGNORECASE)
    if m:
        result["prediction_event"] = m.group(1).strip()

    # prediction_target — line starting with "Target:"
    m = re.search(r"(?:^|\n)\s*Target:\s*(.+)", description, re.IGNORECASE)
    if m:
        result["prediction_target"] = m.group(1).strip()

    # prediction_deadline_days — "Deadline: <N> days" or "Deadline: <N>"
    m = re.search(r"(?:^|\n)\s*Deadline:\s*(\d+)", description, re.IGNORECASE)
    if m:
        try:
            result["prediction_deadline_days"] = int(m.group(1))
        except ValueError:
            pass

    # prediction_measurement — line starting with "Measurement:"
    # May span to the next blank line or section header
    m = re.search(
        r"(?:^|\n)\s*Measurement:\s*(.+?)(?:\n\n|\n\*\*|\Z)",
        description, re.IGNORECASE | re.DOTALL
    )
    if m:
        result["prediction_measurement"] = m.group(1).strip()

    return result


updated = 0
skipped_no_data = 0
skipped_partial = 0
errors = 0

for row in rows:
    hyp_id = row["id"]
    title = row.get("title", "")[:60]
    description = row.get("description", "") or ""

    fields = extract_from_markdown(description)

    if not fields:
        logger.warning(f"  No prediction block found in {hyp_id[:8]} — ({title})")
        skipped_no_data += 1
        continue

    # Only update fields we actually extracted — don't overwrite with empty strings
    update_payload = {}
    if fields.get("prediction_event"):
        update_payload["prediction_event"] = fields["prediction_event"]
    if fields.get("prediction_target"):
        update_payload["prediction_target"] = fields["prediction_target"]
    if fields.get("prediction_deadline_days") is not None:
        update_payload["prediction_deadline_days"] = fields["prediction_deadline_days"]
    if fields.get("prediction_measurement"):
        update_payload["prediction_measurement"] = fields["prediction_measurement"]

    if not update_payload:
        logger.info(f"  Partial extraction for {hyp_id[:8]} — skipping")
        skipped_partial += 1
        continue

    try:
        client.table("hypotheses").update(update_payload).eq("id", hyp_id).execute()
        logger.info(
            f"  Updated {hyp_id[:8]}: "
            f"event='{str(fields.get('prediction_event', ''))[:40]}' "
            f"deadline={fields.get('prediction_deadline_days')} "
            f"({title})"
        )
        updated += 1
    except Exception as e:
        logger.error(f"  DB update failed for {hyp_id[:8]}: {e}")
        errors += 1

print("\n" + "-"*70)
print(f"Backfill v2 complete.")
print(f"  Updated:               {updated}")
print(f"  Skipped (no block):    {skipped_no_data}")
print(f"  Skipped (partial):     {skipped_partial}")
print(f"  DB errors:             {errors}")
print()
print("Run verify_p0_finding1.py to confirm population rates.")
print("="*70 + "\n")
