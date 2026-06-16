-- Create Hypothesis Type Enum
-- Note: Supabase Postgres supports ENUMs but using VARCHAR with check constraint is easier to alter later via API.
CREATE TABLE IF NOT EXISTS public.hypotheses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES public.companies(id) ON DELETE CASCADE,
    type VARCHAR NOT NULL, -- e.g. EXPANSION, RISK, PRODUCT_PIVOT, ACQUISITION_TARGET, GEOGRAPHIC_EXPANSION, GO_TO_MARKET_EXPANSION
    title TEXT NOT NULL,
    description TEXT,
    confidence FLOAT NOT NULL DEFAULT 0.50,
    status VARCHAR DEFAULT 'ACTIVE', -- ACTIVE, CONFIRMED, REJECTED
    themes JSONB DEFAULT '[]'::jsonb, -- Array of strings mapping to SignalSubtype logic
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.hypothesis_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hypothesis_id UUID REFERENCES public.hypotheses(id) ON DELETE CASCADE,
    captured_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    confidence FLOAT NOT NULL,
    status VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS public.hypothesis_evaluations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hypothesis_id UUID REFERENCES public.hypotheses(id) ON DELETE CASCADE,
    signal_id UUID REFERENCES public.signals(id) ON DELETE CASCADE,
    impact FLOAT NOT NULL, -- The delta applied (e.g. +0.10)
    reasoning TEXT NOT NULL, -- Explanation of why deterministic rule fired
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indices
CREATE INDEX IF NOT EXISTS idx_hypotheses_company_id ON public.hypotheses(company_id);
CREATE INDEX IF NOT EXISTS idx_hypothesis_snapshots_hypothesis_id ON public.hypothesis_snapshots(hypothesis_id, captured_at DESC);
CREATE INDEX IF NOT EXISTS idx_hypothesis_eval_hypothesis_id ON public.hypothesis_evaluations(hypothesis_id, created_at DESC);

-- RLS
ALTER TABLE public.hypotheses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.hypothesis_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.hypothesis_evaluations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable read access for all users" ON public.hypotheses FOR SELECT USING (true);
CREATE POLICY "Enable insert for service role" ON public.hypotheses FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update for service role" ON public.hypotheses FOR UPDATE USING (true);

CREATE POLICY "Enable read access for all users" ON public.hypothesis_snapshots FOR SELECT USING (true);
CREATE POLICY "Enable insert for service role" ON public.hypothesis_snapshots FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable read access for all users" ON public.hypothesis_evaluations FOR SELECT USING (true);
CREATE POLICY "Enable insert for service role" ON public.hypothesis_evaluations FOR INSERT WITH CHECK (true);
