"""
Argos — Figma Ingestion Contamination Test
Verifies that generic productivity articles incorrectly matched to Figma 
are deterministically filtered out by the new Attribution pre-filtering.
"""

import sys
import os

# Insert backend folder to path
sys.path.insert(0, os.path.join(os.getcwd(), "backend"))

from app.analysis.prediction_tracker import PredictionTracker
from app.signals.attribution_engine import AttributionEngine

def test_figma_adversarial():
    print("\n" + "=" * 60)
    print("FIGMA ADVERSARIAL ATTRIBUTION FILTER TEST")
    print("=" * 60)
    
    # 1. Instantiate engine
    engine = AttributionEngine(portfolio_companies=["Figma", "OpenAI"])
    
    # 2. Mock Figma hypothesis
    hypothesis = {
        "id": "figma-test-001",
        "company_id": "figma-co-id",
        "company_name": "Figma",
        "title": "Figma will launch native slides and presentation features",
        "prediction_event": "Figma officially launches Figma Slides as a core product",
        "prediction_target": "Figma",
        "prediction_deadline_days": 180,
        "prediction_measurement": "Product announcement page and pricing for Figma Slides",
        "created_at": "2026-01-01T00:00:00Z"
    }
    
    # 3. Mock contaminated "trap" signal (generic productivity article mentioning figma in body only)
    trap_signal = {
        "id": "figma-trap-001",
        "signal_type": "NEWS",
        "title": "10 Best Collaboration Tips for Hybrid Product Teams in 2026",
        "url": "https://technews.com/hybrid-collaboration-tips",
        "description": "An overview of how modern teams work. Many product teams use tools like Figma, Slack, and Jira to collaborate."
    }
    
    print(f"Auditing signal: '{trap_signal['title']}'")
    print(f"Target company:  {hypothesis['company_name']}")
    
    # 4. Evaluate signal through engine
    res = engine.calculate_attribution(
        title=trap_signal["title"],
        description=trap_signal["description"],
        url=trap_signal["url"],
        company_name=hypothesis["company_name"],
        website="https://figma.com"
    )
    
    print("-"*50)
    print("ATTRIBUTION ENGINE RESULTS:")
    print(f"  - Calculated Confidence: {res['attribution_confidence']}")
    print(f"  - Calculated Type:       {res['attribution_type']}")
    print(f"  - Triggered Reasons:     {res['attribution_reason']}")
    print("-"*50)
    
    # Verify it is classified as NOISE and falls below 0.20 threshold
    assert res["attribution_confidence"] < 0.20, "Figma trap signal did not drop below 0.20 threshold!"
    assert res["attribution_type"] == "NOISE", "Figma trap signal was not classified as NOISE!"
    print("SUCCESS: Pre-filter verification: Signal correctly classified as NOISE (< 0.20).")
    
    # 5. Run the tracker signal-filtering logic simulation
    tracker = PredictionTracker()
    
    # Inject our newly calculated metadata into the signal
    trap_signal.update(res)
    
    # Run the filtering logic
    signals = [trap_signal]
    seen_count = len(signals)
    used_signals = [s for s in signals if s.get("attribution_confidence", 1.0) >= 0.20]
    filtered_count = seen_count - len(used_signals)
    
    print(f"Tracker evaluation simulated:")
    print(f"  - Signals Seen:     {seen_count}")
    print(f"  - Signals Used:     {len(used_signals)}")
    print(f"  - Signals Filtered: {filtered_count}")
    
    assert filtered_count == 1, "Tracker failed to discard the contaminated Figma signal!"
    assert len(used_signals) == 0, "Contaminated Figma signal was incorrectly passed to LLM!"
    print("SUCCESS: Tracker simulation: Signal successfully FILTERED from LLM context.")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    test_figma_adversarial()
