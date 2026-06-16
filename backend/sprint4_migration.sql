-- Add Outcome Tracking columns to hypotheses
ALTER TABLE public.hypotheses 
ADD COLUMN IF NOT EXISTS outcome VARCHAR DEFAULT 'PENDING',
ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS resolution_reason TEXT,
ADD COLUMN IF NOT EXISTS predicted_time_horizon VARCHAR; -- 30_days, 90_days, 180_days, 365_days
