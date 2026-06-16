import os
import json
from app.database import get_supabase_client
from app.pipeline.nodes import filter_new_signals_node
from app.main import app
from fastapi.testclient import TestClient

client = get_supabase_client()
api_client = TestClient(app)

print('--- 1. Pushing to CONFIRMED ---')
res = client.table('hypotheses').select('*').ilike('title', '%AI Innovation in India%').execute()
hyp_id = res.data[0]['id']
company_id = res.data[0]['company_id']

# Inject two more reinforcing signals to push confidence from 0.70 to 0.90
for i in range(2):
    state = {
        'company_id': company_id,
        'company_name': 'Accenture',
        'raw_signals': [{
            'company_id': company_id,
            'company_name': 'Accenture',
            'signal_type': 'HIRING',
            'subtype': 'AI_EXPANSION',
            'title': f'Accenture AI Expansion Update {i}',
            'content': 'More AI hiring.',
            'url': f'https://example.com/ai-expansion-india-3-{i}',
            'importance': 8.5,
            'confidence': 95,
            'agent': 'NewsAgent'
        }]
    }
    filter_new_signals_node(state)

hyp_res = client.table('hypotheses').select('confidence, status').eq('id', hyp_id).single().execute()
print(f"Confidence: {hyp_res.data['confidence']}, Status: {hyp_res.data['status']}")

print('\n--- 2. Resolving Outcome ---')
resolve_payload = {
    'outcome': 'CORRECT',
    'resolution_reason': 'Company officially confirmed massive AI expansion roadmap in India.'
}
resp = api_client.post(f'/hypotheses/{hyp_id}/resolve', json=resolve_payload)
print('Resolve API Status:', resp.status_code)

hyp_res_after = client.table('hypotheses').select('outcome, resolution_reason').eq('id', hyp_id).single().execute()
print(f"Outcome: {hyp_res_after.data['outcome']}, Reason: {hyp_res_after.data['resolution_reason']}")

print('\n--- 3. Checking Scorecard ---')
scorecard_resp = api_client.get('/analytics/scorecard')
print(json.dumps(scorecard_resp.json(), indent=2))
