-- Add last_evidence_at to track drift and staleness
ALTER TABLE public.hypotheses 
ADD COLUMN IF NOT EXISTS last_evidence_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
