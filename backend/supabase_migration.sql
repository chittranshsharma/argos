-- Create sources table
CREATE TABLE IF NOT EXISTS public.sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url TEXT UNIQUE,
    title TEXT,
    published_at TIMESTAMP WITH TIME ZONE,
    raw_text TEXT,
    retrieved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Alter signals table to add new fields
ALTER TABLE public.signals
ADD COLUMN IF NOT EXISTS entity_type TEXT DEFAULT 'COMPANY',
ADD COLUMN IF NOT EXISTS subtype TEXT,
ADD COLUMN IF NOT EXISTS source_id UUID REFERENCES public.sources(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'ACTIVE',
ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS agent TEXT,
ADD COLUMN IF NOT EXISTS extraction_model TEXT;

-- Drop raw_text from signals if it existed (depends on previous schema)
-- ALTER TABLE public.signals DROP COLUMN IF EXISTS raw_text;

-- Update RLS policies for sources if needed
ALTER TABLE public.sources ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable read access for all users" ON public.sources
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for service role" ON public.sources
    FOR INSERT WITH CHECK (true);
