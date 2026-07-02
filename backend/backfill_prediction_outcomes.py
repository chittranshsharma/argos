"""
Sprint 5A: Backfill prediction_outcomes for all existing hypotheses.

Finds every hypothesis with no corresponding prediction_outcomes row
and creates an UNRESOLVED registry entry for it.
Run once after the Sprint 5A migration.
"""
import sys, os
sys.path.insert(0, os.getcwd())
os.chdir("backend")
from dotenv import load_dotenv
load_dotenv()

from app.database import get_supabase_client, create_prediction_outcome

client = get_supabase_client()

# 1. Get all hypothesis IDs
all_hyp = client.table("hypotheses").select("id, title, status").execute().data or []
print(f"Total hypotheses in DB: {len(all_hyp)}")

# 2. Get all hypothesis_ids that already have a registry row
existing = client.table("prediction_outcomes").select("hypothesis_id").execute().data or []
existing_ids = {r["hypothesis_id"] for r in existing}
print(f"Already have registry rows: {len(existing_ids)}")

# 3. Find the gap
missing = [h for h in all_hyp if h["id"] not in existing_ids]
print(f"Missing registry rows: {len(missing)}")

# 4. Backfill
created = 0
failed = 0
for h in missing:
    result = create_prediction_outcome(h["id"])
    if result:
        created += 1
        print(f"  CREATED [{h.get('status','?')}] {h['id'][:8]}... {h.get('title','')[:60]}")
    else:
        failed += 1
        print(f"  FAILED  {h['id'][:8]}...")

print(f"\nBackfill complete: {created} created, {failed} failed")

# 5. Verify
final = client.table("prediction_outcomes").select("status", count="exact").execute()
print(f"Total prediction_outcomes rows now: {final.count}")
