from app.database import get_supabase_client

client = get_supabase_client()
hyps = client.table('hypotheses').select('*').execute().data

for h in hyps:
    print(f"\n{'='*50}")
    print(f"BELIEF: {h['title']}")
    print(f"{'='*50}")
    print(h['description'])
