"""
Argos — Forecast Leaderboard  (Sprint 5D)
==========================================
Prints five tables:

  1. Per-row detail          — forecast_id | company | horizon | confidence | outcome
  2. Accuracy by horizon     — Resolved | Confirmed | Contradicted | Expired | Hit Rate
  3. Resolution volume       — Active | Resolved | Resolution Rate  (per horizon)
  4. Confidence calibration  — Resolved | Hit Rate  (per 0.1-wide bucket)
  5. Calibration verdict     — Only issued when ≥3 buckets AND ≥10 resolved per bucket

Run:
    python backend/forecast_leaderboard.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "backend"))

from app.database import (
    get_supabase_client,
    get_forecast_horizon_breakdown,
    get_forecast_confidence_calibration,
)

# ── Helpers ──────────────────────────────────────────────────────────────────

W = 90  # total output width

def _hr(char: str = "─") -> str:
    return char * W

def _header(title: str) -> None:
    print()
    print(_hr("═"))
    pad = (W - len(title) - 2) // 2
    print(" " * pad + f" {title} ")
    print(_hr("═"))

def _pct(value) -> str:
    """Format a 0–1 float as a percentage string, or '—' if None."""
    if value is None:
        return "—"
    return f"{value * 100:.1f}%"


# ── Table 1: Per-row detail ───────────────────────────────────────────────────

def _print_detail_rows(rows: list) -> None:
    _header("FORECAST DETAIL — All Outcomes")

    col_w = [38, 20, 7, 6, 13]
    headers = ["Forecast ID", "Company", "Horizon", "Conf", "Outcome"]

    # Header row
    header_line = " | ".join(h.ljust(col_w[i]) for i, h in enumerate(headers))
    print(header_line)
    print(_hr("─"))

    for item in rows:
        conf_str = f"{item['confidence']:.2f}" if item['confidence'] is not None else "—"
        cols = [
            item["forecast_id"][:col_w[0]].ljust(col_w[0]),
            item["company_name"][:col_w[1]].ljust(col_w[1]),
            item["horizon"].ljust(col_w[2]),
            conf_str.ljust(col_w[3]),
            item["status"].ljust(col_w[4]),
        ]
        print(" | ".join(cols))

    print(_hr("─"))
    print(f"  Total rows: {len(rows)}")


# ── Table 2: Accuracy by Horizon ─────────────────────────────────────────────

def _print_horizon_accuracy(horizon_rows: list) -> None:
    _header("ACCURACY BY HORIZON")

    fmt = "{:<8} {:>10} {:>12} {:>14} {:>9} {:>10}"
    print(fmt.format("Horizon", "Resolved", "Confirmed", "Contradicted", "Expired", "Hit Rate"))
    print(_hr("─"))

    for r in horizon_rows:
        print(fmt.format(
            r["horizon"],
            r["resolved"],
            r["confirmed"],
            r["contradicted"],
            r["expired"],
            _pct(r["hit_rate"]),
        ))

    if not horizon_rows:
        print("  No resolved outcomes yet.")
    print(_hr("─"))
    print("  Hit Rate = Confirmed ÷ (Confirmed + Contradicted). Expired excluded from denominator.")


# ── Table 3: Resolution Volume ────────────────────────────────────────────────

def _print_resolution_volume(horizon_rows: list) -> None:
    _header("RESOLUTION VOLUME BY HORIZON")

    fmt = "{:<8} {:>8} {:>10} {:>18}"
    print(fmt.format("Horizon", "Active", "Resolved", "Resolution Rate"))
    print(_hr("─"))

    for r in horizon_rows:
        print(fmt.format(
            r["horizon"],
            r["active"],
            r["resolved"],
            _pct(r["resolution_rate"]),
        ))

    if not horizon_rows:
        print("  No data yet.")
    print(_hr("─"))
    print("  Resolution Rate = Resolved ÷ (Active + Resolved).")
    print("  Low rate on 90d+ likely means deadlines haven't passed yet — not that forecasts are bad.")


# ── Table 4: Confidence Calibration ──────────────────────────────────────────

def _print_confidence_calibration(calibration: dict) -> None:
    _header("CONFIDENCE CALIBRATION")

    buckets = calibration.get("buckets", [])
    verdict = calibration.get("verdict")
    verdict_reason = calibration.get("verdict_reason", "")

    fmt = "{:<12} {:>10} {:>12} {:>14} {:>10} {:>10}"
    print(fmt.format("Bucket", "Resolved", "Confirmed", "Contradicted", "Expired", "Hit Rate"))
    print(_hr("─"))

    any_data = False
    for b in buckets:
        if b["resolved"] == 0:
            # Still print the row so the table is always complete
            print(fmt.format(b["label"], "—", "—", "—", "—", "—"))
        else:
            any_data = True
            print(fmt.format(
                b["label"],
                b["resolved"],
                b["confirmed"],
                b["contradicted"],
                b["expired"],
                _pct(b["hit_rate"]),
            ))

    print(_hr("─"))

    if not any_data:
        print("  No resolved forecasts in any confidence bucket yet.")

    # ── Calibration Verdict ───────────────────────────────────────────────────
    print()
    print("CALIBRATION VERDICT:")
    if verdict is None:
        print(f"  ⏳  PENDING — {verdict_reason}")
        print()
        print("  Minimum required before any verdict:")
        print("    • ≥ 3 confidence buckets populated")
        print("    • ≥ 10 resolved forecasts per populated bucket")
        print()
        print("  A 1/1 bucket and a 0/1 bucket do not constitute evidence.")
        print("  Run more volume, then re-run this script.")
    elif verdict == "CORRELATED":
        print(f"  ✅  CORRELATED — {verdict_reason}")
        print()
        print("  Confidence score is earning its place. Calibration work in Sprint 5C may be worth pursuing.")
    elif verdict == "WEAK":
        print(f"  ⚠️   WEAK — {verdict_reason}")
        print()
        print("  Inconclusive. Collect more forecasts before deciding whether to invest in calibration.")
    elif verdict == "UNCORRELATED":
        print(f"  ❌  UNCORRELATED — {verdict_reason}")
        print()
        print("  Confidence scoring is not predicting outcomes. Do NOT build on top of it.")
        print("  Sprint 5C should be blocked until the root cause is diagnosed.")


# ── Main ──────────────────────────────────────────────────────────────────────

def run_leaderboard() -> None:
    print("Connecting to Supabase...")
    client = get_supabase_client()

    print("Querying prediction_outcomes...")
    res = client.table("prediction_outcomes").select(
        "id, status, confidence, resolved_at, hypotheses(title, prediction_deadline_days, created_at)"
    ).execute()
    raw_rows = res.data or []

    if not raw_rows:
        print("\nNo prediction outcomes found in database.")
        return

    # ── Build detail rows ─────────────────────────────────────────────────────
    from app.database import _classify_horizon

    detail_rows = []
    for r in raw_rows:
        hyp = r.get("hypotheses") or {}
        if not hyp:
            continue
        deadline = hyp.get("prediction_deadline_days", 30)
        horizon  = _classify_horizon(deadline)
        detail_rows.append({
            "forecast_id":   r["id"],
            "company_name":  hyp.get("title", "Unknown")[:30],
            "horizon":       horizon,
            "confidence":    r.get("confidence"),
            "status":        r.get("status", "UNRESOLVED"),
        })

    resolved = [d for d in detail_rows if d["status"] in ("CONFIRMED", "INCORRECT", "CONTRADICTED", "EXPIRED")]
    active   = [d for d in detail_rows if d not in resolved]

    print(f"\nActive Forecasts:   {len(active)}")
    print(f"Resolved Forecasts: {len(resolved)}")

    # ── Print all five tables ─────────────────────────────────────────────────
    _print_detail_rows(detail_rows)

    horizon_rows   = get_forecast_horizon_breakdown()
    calibration    = get_forecast_confidence_calibration()

    _print_horizon_accuracy(horizon_rows)
    _print_resolution_volume(horizon_rows)
    _print_confidence_calibration(calibration)

    print()
    print(_hr("═"))
    print()


if __name__ == "__main__":
    run_leaderboard()
