"""
Argos — Adversarial Resolution Precision Test

Tests whether the tracker over-promotes SUPPORTED → CONFIRMED when fed
similar-but-not-confirming signals. This is the cause/outcome confusion test.

Each test case has:
  - A structured prediction (prediction_event, target, measurement)
  - A set of "trap" signals that are directionally related but don't confirm the event
  - Expected verdict: SUPPORTED or UNCHANGED (NOT CONFIRMED)

If any trap case returns CONFIRMED, the tracker prompt is still over-crediting.

Usage: python backend/audit_adversarial.py
"""

import sys, os, json
sys.path.insert(0, os.getcwd())
os.chdir("backend")
from dotenv import load_dotenv
load_dotenv()

from app.analysis.prediction_tracker import PredictionTracker

tracker = PredictionTracker()

# ─────────────────────────────────────────────────────────────────
# Adversarial test cases
# ─────────────────────────────────────────────────────────────────

TRAP_CASES = [
    {
        "name": "OpenAI Enterprise Platform — Trap: partnership ≠ platform launch",
        "hypothesis": {
            "id": "test-001",
            "title": "OpenAI will launch a dedicated enterprise data platform",
            "description": "OpenAI will release a standalone enterprise product built around customer-specific data.",
            "prediction_event": "OpenAI launches a named enterprise data platform product",
            "prediction_target": "OpenAI",
            "prediction_deadline_days": 180,
            "prediction_measurement": "Product announcement with named product + pricing page",
            "created_at": "2026-01-01T00:00:00Z",
        },
        "trap_signals": [
            {"id": "s1", "signal_type": "NEWS", "title": "OpenAI signs enterprise partnership with JPMorgan Chase",
             "content": "OpenAI and JPMorgan Chase announced a strategic partnership to deploy ChatGPT Enterprise across the bank's operations.", "collected_at": "2026-06-01"},
            {"id": "s2", "signal_type": "NEWS", "title": "OpenAI expands enterprise agreement with Microsoft Azure",
             "content": "Microsoft and OpenAI deepen their partnership with new enterprise-focused AI tools available via Azure.", "collected_at": "2026-06-02"},
            {"id": "s3", "signal_type": "HIRING", "title": "OpenAI hiring enterprise sales engineers",
             "content": "OpenAI posted 12 new enterprise sales engineering roles focused on Fortune 500 deployments.", "collected_at": "2026-06-03"},
        ],
        "expected": "SUPPORTED",  # Partnerships suggest enterprise focus but don't confirm platform LAUNCH
        "trap_description": "Enterprise partnerships ≠ dedicated data platform launch",
    },
    {
        "name": "Anthropic Mythos re-enable — Trap: regulatory discussion ≠ re-enablement",
        "hypothesis": {
            "id": "test-002",
            "title": "Anthropic will re-enable Mythos and Fable models in restricted markets",
            "description": "Anthropic will lift export restrictions on Mythos/Fable within 90 days.",
            "prediction_event": "Anthropic officially re-enables Mythos and Fable model access",
            "prediction_target": "Anthropic",
            "prediction_deadline_days": 90,
            "prediction_measurement": "Anthropic announcement of model availability restoration in previously blocked regions",
            "created_at": "2026-04-01T00:00:00Z",
        },
        "trap_signals": [
            {"id": "s4", "signal_type": "NEWS", "title": "Anthropic floats proposal to Howard Lutnick to end ban of Mythos models",
             "content": "Anthropic sent a proposal to Commerce Secretary Howard Lutnick requesting reconsideration of export restrictions on Mythos and Fable.", "collected_at": "2026-06-10"},
            {"id": "s5", "signal_type": "NEWS", "title": "Anthropic's Export Control Crackdown Leaves South Korea in AI Crossfire",
             "content": "South Korean developers report inability to access Anthropic's Mythos model due to US export controls.", "collected_at": "2026-06-11"},
            {"id": "s6", "signal_type": "NEWS", "title": "Anthropic implements stricter identity verification for API access",
             "content": "Anthropic now requires government ID verification for new API subscribers in restricted jurisdictions.", "collected_at": "2026-06-12"},
        ],
        "expected": "SUPPORTED",  # Lobbying ≠ re-enablement. Restrictions still in place.
        "trap_description": "Regulatory lobbying and compliance ≠ actual model re-enablement",
    },
    {
        "name": "Stripe Global Expansion — Trap: conference mention ≠ market launch",
        "hypothesis": {
            "id": "test-003",
            "title": "Stripe will launch payments infrastructure in Sub-Saharan Africa",
            "description": "Stripe will announce entry into 3+ new African markets with local payment methods.",
            "prediction_event": "Stripe officially launches payment processing in Sub-Saharan African markets",
            "prediction_target": "Stripe",
            "prediction_deadline_days": 120,
            "prediction_measurement": "Press release announcing live payment processing in named African countries",
            "created_at": "2026-03-01T00:00:00Z",
        },
        "trap_signals": [
            {"id": "s7", "signal_type": "NEWS", "title": "Stripe CEO discusses Africa opportunity at Davos",
             "content": "Patrick Collison mentioned Africa as a key growth opportunity in a panel discussion at the World Economic Forum.", "collected_at": "2026-06-01"},
            {"id": "s8", "signal_type": "HIRING", "title": "Stripe hiring regional partnerships manager for emerging markets",
             "content": "Stripe posted a role for Regional Partnerships Manager covering Middle East and Africa.", "collected_at": "2026-06-05"},
            {"id": "s9", "signal_type": "NEWS", "title": "Stripe processes $1 trillion in payment volume in 2025",
             "content": "Stripe announced record payment volume driven by strong growth in North America and Europe.", "collected_at": "2026-06-08"},
        ],
        "expected": "UNCHANGED",  # CEO mention and a hiring role ≠ market launch
        "trap_description": "Executive comment + hiring ≠ market launch announcement",
    },
    {
        "name": "CONTRADICTED precision — Trap: should not flip to CONFIRMED",
        "hypothesis": {
            "id": "test-004",
            "title": "Anthropic will reduce Claude API pricing by 40% within 60 days",
            "description": "Anthropic will announce significant pricing reduction to compete with OpenAI and Google.",
            "prediction_event": "Anthropic announces 40%+ reduction in Claude API token pricing",
            "prediction_target": "Anthropic",
            "prediction_deadline_days": 60,
            "prediction_measurement": "Official Anthropic pricing page showing reduced rates vs prior quarter",
            "created_at": "2026-05-01T00:00:00Z",
        },
        "trap_signals": [
            {"id": "s10", "signal_type": "NEWS", "title": "Anthropic raises Claude API prices by 10% citing compute costs",
             "content": "Anthropic adjusted its API pricing upward across all tiers, citing increased infrastructure and compute costs.", "collected_at": "2026-06-01"},
            {"id": "s11", "signal_type": "NEWS", "title": "Anthropic introduces new Claude Pro tier with enhanced features",
             "content": "Anthropic launched Claude Pro with additional features at premium pricing, expanding its enterprise offering.", "collected_at": "2026-06-03"},
        ],
        "expected": "CONTRADICTED",  # Price increase directly contradicts price reduction prediction
        "trap_description": "Price increase should produce CONTRADICTED, not CONFIRMED",
    },
]


def run_adversarial():
    print("\n" + "=" * 70)
    print("ADVERSARIAL RESOLUTION PRECISION TEST")
    print("=" * 70)
    print("Goal: Tracker must NOT return CONFIRMED for trap signals.")
    print("      CONTRADICTED test must return CONTRADICTED, not CONFIRMED.")
    print()

    results = []
    passes = 0
    fails = 0

    for case in TRAP_CASES:
        print(f"TEST: {case['name']}")
        print(f"  Trap: {case['trap_description']}")
        print(f"  Expected: {case['expected']}")

        verdict = tracker._classify_evidence(case["hypothesis"], case["trap_signals"])
        actual = verdict.get("verdict", "UNKNOWN")
        structured = verdict.get("prediction_structured", False)
        cause_check = verdict.get("cause_vs_outcome_check", "")

        passed = actual == case["expected"]
        if passed:
            passes += 1
            symbol = "✅ PASS"
        else:
            fails += 1
            symbol = f"❌ FAIL (got {actual}, expected {case['expected']})"

        print(f"  Result: {symbol}")
        print(f"  Verdict confidence: {verdict.get('confidence', '?')}")
        print(f"  Prediction structured: {structured}")
        print(f"  Cause/Outcome check: {cause_check}")
        print(f"  Reasoning: {verdict.get('reasoning', '')}")
        print()

        results.append({
            "name": case["name"],
            "expected": case["expected"],
            "actual": actual,
            "passed": passed,
            "confidence": verdict.get("confidence"),
            "reasoning": verdict.get("reasoning", ""),
            "cause_check": cause_check,
        })

    print("=" * 70)
    print(f"ADVERSARIAL RESULTS: {passes}/{len(TRAP_CASES)} passed")

    if fails == 0:
        print("✅ All trap cases handled correctly. CONFIRMED precision is protected.")
    else:
        print(f"❌ {fails} trap case(s) failed. Tracker over-promoting verdicts.")
        print()
        print("FAILED CASES:")
        for r in results:
            if not r["passed"]:
                print(f"  [{r['expected']} → {r['actual']}] {r['name']}")
                print(f"    Reasoning: {r['reasoning']}")

    print()
    print(f"Adversarial pass rate: {passes/len(TRAP_CASES)*100:.0f}%")
    print("Target: 100% (tracker must never CONFIRM trap signals)")
    return passes, fails


if __name__ == "__main__":
    run_adversarial()
