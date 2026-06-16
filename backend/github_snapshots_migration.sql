-- Create github_snapshots table for deterministic engineering velocity tracking
CREATE TABLE IF NOT EXISTS public.github_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES public.companies(id) ON DELETE CASCADE,
    captured_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Absolute counters at time of snapshot
    stars INTEGER DEFAULT 0,
    forks INTEGER DEFAULT 0,
    repo_count INTEGER DEFAULT 0,
    
    -- Rolling 30 day metrics at time of snapshot
    contributors_30d INTEGER DEFAULT 0,
    commits_30d INTEGER DEFAULT 0,
    releases_30d INTEGER DEFAULT 0
);

-- Index for fast lookup of latest snapshot per company
CREATE INDEX IF NOT EXISTS idx_github_snapshots_company_id_captured_at 
ON public.github_snapshots(company_id, captured_at DESC);

-- Alter companies table to store the rolling engineering_velocity_score
ALTER TABLE public.companies
ADD COLUMN IF NOT EXISTS engineering_velocity_score INTEGER DEFAULT 0;

-- Update RLS policies
ALTER TABLE public.github_snapshots ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable read access for all users" ON public.github_snapshots
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for service role" ON public.github_snapshots
    FOR INSERT WITH CHECK (true);
