import os
import json
from app.database import get_supabase_client
from app.pipeline.nodes import correlate_signals_node
from app.analysis.watchlist_scorer import WatchlistScorer

client = get_supabase_client()
companies = client.table('companies').select('id, name').execute().data

# We test 3 specific companies in DB: OpenAI, Accenture, Razorpay
targets = ['openai', 'accenture', 'razorpay']
results = {}

scorer = WatchlistScorer()

for target in targets:
    target_company = next((c for c in companies if target in c['name'].lower()), None)
    if not target_company:
        continue
        
    company_id = target_company['id']
    company_name = target_company['name']
    
    print(f"\n=========================================")
    print(f"Processing {company_name}")
    print(f"=========================================")
    
    # Get all real signals
    sigs_res = client.table('signals').select('*').eq('company_id', company_id).order('collected_at', desc=False).limit(60).execute()
    real_signals = sigs_res.data
    
    if not real_signals:
        print(f"No signals found for {company_name}")
        continue
        
    print(f"Signals found: {len(real_signals)}")
    
    # Run correlator to generate hypotheses
    state = {
        'company_id': company_id,
        'company_name': company_name,
        'new_signals': real_signals
    }
    
    print("Running Hypothesis Engine...")
    correlate_signals_node(state)
    
    # Run watchlist scorer on all signals to generate evaluations/snapshots
    print("Running Watchlist Scorer...")
    for sig in real_signals:
        scorer.evaluate_signal(company_id, sig)
        
    # Gather Results
    hyp_res = client.table('hypotheses').select('*').eq('company_id', company_id).execute()
    hyps = hyp_res.data
    
    correlations_res = client.table('signals').select('id', count='exact').eq('company_id', company_id).eq('signal_type', 'CORRELATION').execute()
    evals_res = client.table('hypothesis_evaluations').select('id', count='exact').in_('hypothesis_id', [h['id'] for h in hyps] if hyps else ['00000000-0000-0000-0000-000000000000']).execute()
    snaps_res = client.table('hypothesis_snapshots').select('id', count='exact').in_('hypothesis_id', [h['id'] for h in hyps] if hyps else ['00000000-0000-0000-0000-000000000000']).execute()
    
    results[company_name] = {
        'signals_count': len(real_signals),
        'correlations_count': correlations_res.count or 0,
        'hypotheses': hyps,
        'evaluations_count': evals_res.count or 0,
        'snapshots_count': snaps_res.count or 0
    }
    
    print(f"Correlations generated: {results[company_name]['correlations_count']}")
    print(f"Hypotheses generated: {len(hyps)}")
    for h in hyps:
        print(f"  - {h['title']} (Conf: {h['confidence']}, Status: {h['status']})")
    print(f"Database rows -> Evaluations: {results[company_name]['evaluations_count']}, Snapshots: {results[company_name]['snapshots_count']}")

print("\n\n=== FINAL ANALYSIS ===")
all_hyps = []
for c_name, data in results.items():
    for h in data['hypotheses']:
        h['company'] = c_name
        all_hyps.append(h)

if all_hyps:
    strongest = max(all_hyps, key=lambda x: x['confidence'])
    weakest = min(all_hyps, key=lambda x: x['confidence'])
    
    company_confidences = {}
    for c_name, data in results.items():
        if data['hypotheses']:
            avg_conf = sum(h['confidence'] for h in data['hypotheses']) / len(data['hypotheses'])
            company_confidences[c_name] = avg_conf
            
    highest_conf_company = max(company_confidences.items(), key=lambda x: x[1])
    
    print(f"Strongest Hypothesis: {strongest['title']} ({strongest['company']}) - Conf: {strongest['confidence']}")
    print(f"Weakest Hypothesis: {weakest['title']} ({weakest['company']}) - Conf: {weakest['confidence']}")
    print(f"Highest Forecasting Confidence Company: {highest_conf_company[0]} (Avg Conf: {highest_conf_company[1]:.2f})")
else:
    print("No hypotheses generated across any company.")
