-- Create sources table
CREATE TABLE IF NOT EXISTS public.sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url TEXT UNIQUE,
    title TEXT,
    published_at TIMESTAMP WITH TIME ZONE,
    raw_text TEXT,
    retrieved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
