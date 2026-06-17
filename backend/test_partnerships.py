"""
Sprint E.1: Test PartnershipAgent hardening.
Reports raw -> normalized -> removed self-refs -> final graph edges.
"""
import logging
from app.agents.partnership_agent import PartnershipsAgent, normalize_partner, is_self_reference
from app.database import get_supabase_client, save_signal
from app.memory.graph_db import GraphDB

logging.basicConfig(level=logging.WARNING)

TARGET_COMPANIES = ["OpenAI", "Anthropic", "Databricks", "Stripe", "Snowflake"]


def run():
    client = get_supabase_client()
    companies = (
        client.table("companies")
        .select("*")
        .in_("name", TARGET_COMPANIES)
        .execute()
        .data or []
    )

    agent = PartnershipsAgent()
    all_signals = []
    grand_totals = {
        "raw": 0, "self_refs": 0, "dupes": 0, "final": 0
    }

    for co in companies:
        print(f"\n{'='*55}")
        print(f"  {co['name']}")
        print(f"{'='*55}")
        signals = agent.collect(co["name"], co["id"])

        stats = signals[0].pop("_stats", {}) if signals else {}
        raw_count          = stats.get("raw_count", 0)
        self_refs_removed  = stats.get("self_refs_removed", 0)
        dupes_collapsed    = stats.get("duplicates_collapsed", 0)
        final_count        = len(signals)
        raw_names          = stats.get("raw_partner_names", [])
        norm_names         = stats.get("normalized_partner_names", [])

        collapse_rate = (
            round((raw_count - final_count - self_refs_removed) / raw_count * 100, 1)
            if raw_count else 0
        )

        print(f"  Raw events extracted:    {raw_count}")
        print(f"  Self-refs removed:       {self_refs_removed}")
        print(f"  Duplicates collapsed:    {dupes_collapsed}")
        print(f"  Collapse rate:           {collapse_rate}%")
        print(f"  Final signals:           {final_count}")

        if raw_names:
            print(f"\n  Raw partner names:     {raw_names}")
        if norm_names:
            print(f"  Normalized partners:   {list(dict.fromkeys(norm_names))}")

        print(f"\n  Signals:")
        for sig in signals:
            p = sig.get("payload", {})
            raw  = p.get("partner_name_raw", p.get("partner_name", ""))
            norm = p.get("partner_name", "")
            normalized_flag = " [normalized]" if p.get("partner_was_normalized") else ""
            print(f"    [{sig['subtype']}] {norm}{normalized_flag}")
            print(f"      Raw: {raw} | Conf: {p.get('confidence')} | Value: {p.get('estimated_value')}")

        # Save to DB
        for sig in signals:
            save_signal(sig)
        all_signals.extend(signals)

        grand_totals["raw"]      += raw_count
        grand_totals["self_refs"] += self_refs_removed
        grand_totals["dupes"]    += dupes_collapsed
        grand_totals["final"]    += final_count

    # Graph edge summary
    print(f"\n{'='*55}")
    print(f"  GRAPH EDGES (PARTNERS_WITH)")
    print(f"{'='*55}")
    graph = GraphDB()
    edge_count = 0
    for co in companies:
        g = graph.get_company_graph(co["name"])
        company_edges = [l for l in g["links"] if l["relation"] == "PARTNERS_WITH"]
        if company_edges:
            print(f"\n  {co['name']}:")
            for e in company_edges:
                edge_count += 1
                print(f"    -> {e['target']}")
    graph.close()

    print(f"\n{'='*55}")
    print(f"  TOTALS")
    print(f"{'='*55}")
    print(f"  Total raw events:          {grand_totals['raw']}")
    print(f"  Total self-refs removed:   {grand_totals['self_refs']}")
    print(f"  Total dupes collapsed:     {grand_totals['dupes']}")
    print(f"  Total final signals:       {grand_totals['final']}")
    print(f"  Total graph edges:         {edge_count}")


if __name__ == "__main__":
    run()
