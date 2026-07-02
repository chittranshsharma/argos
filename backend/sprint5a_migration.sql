-- =============================================================
-- SPRINT 5A MIGRATION: Forecast Registry
-- Run this in your Supabase SQL Editor
-- =============================================================

-- 1. Forward-compat: calibrated_confidence (calibration logic postponed until 50+ resolved)
ALTER TABLE public.hypotheses
ADD COLUMN IF NOT EXISTS calibrated_confidence float;

-- 2. Forecast Registry Table
CREATE TABLE IF NOT EXISTS public.prediction_outcomes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hypothesis_id UUID NOT NULL REFERENCES public.hypotheses(id) ON DELETE CASCADE,

    -- State machine:
    -- UNRESOLVED -> SUPPORTED -> CONFIRMED (terminal)
    -- UNRESOLVED -> CONTRADICTED -> CONFIRMED (recovery allowed!)
    -- CONTRADICTED -> INCORRECT (terminal)
    -- UNRESOLVED | SUPPORTED | CONTRADICTED -> EXPIRED (terminal, deadline enforced)
    status TEXT NOT NULL DEFAULT 'UNRESOLVED',

    -- Evidence references
    evidence_signal_ids TEXT[] DEFAULT '{}',
    evidence_count INTEGER DEFAULT 0,

    -- LLM verdict snapshot for auditability
    verdict_payload JSONB,
    confidence FLOAT,

    -- Resolution
    resolution_reason TEXT,
    resolved_at TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_prediction_outcomes_hypothesis
    ON public.prediction_outcomes(hypothesis_id);

CREATE INDEX IF NOT EXISTS idx_prediction_outcomes_status
    ON public.prediction_outcomes(status);
