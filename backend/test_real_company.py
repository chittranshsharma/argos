import os
import json
from app.database import get_supabase_client
from app.pipeline.nodes import correlate_signals_node

client = get_supabase_client()
companies = client.table('companies').select('id, name').execute().data

targets = ['openai', 'anthropic', 'databricks', 'palantir']
target_company = None
for c in companies:
    if c['name'].lower() in targets:
        target_company = c
        break

if not target_company:
    print('No target company found.')
    exit(1)

company_id = target_company['id']
company_name = target_company['name']

print(f'--- Using Company: {company_name} ---')
sigs = client.table('signals').select('*').eq('company_id', company_id).execute()
real_signals = sigs.data
print(f'Total Real Signals Found: {len(real_signals)}')

# Run pipeline directly with these real signals
state = {
    'company_id': company_id,
    'company_name': company_name,
    'new_signals': real_signals
}

print('\n--- Running Correlator & Hypothesis Engine ---')
correlate_signals_node(state)

print('\n--- Verifying Results ---')
res = client.table('hypotheses').select('*').eq('company_id', company_id).order('created_at', desc=True).limit(5).execute()
hyps = res.data
print(f'Found {len(hyps)} hypotheses generated purely from real signals.')
for h in hyps:
    print(f"- {h['title']} (Conf: {h['confidence']}, Status: {h['status']})")
