from app.database import get_supabase_client

def clear_db():
    client = get_supabase_client()
    print("Clearing hypotheses...")
    client.table("hypothesis_evaluations").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    client.table("hypothesis_snapshots").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    client.table("hypotheses").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    print("Done clearing hypotheses.")

if __name__ == "__main__":
    clear_db()
