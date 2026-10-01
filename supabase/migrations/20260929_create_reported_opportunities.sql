-- 5.21 — Report Opportunity persistence
-- Stores user reports against opportunities.

CREATE TABLE IF NOT EXISTS public.reported_opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    profile_id UUID NOT NULL,

    opportunity_id UUID NOT NULL
        REFERENCES public.opportunities(id)
        ON DELETE CASCADE,

    reason TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT reported_opportunities_reason_not_empty
        CHECK (length(trim(reason)) > 0)
);

CREATE INDEX IF NOT EXISTS
    idx_reported_opportunities_profile_id
ON public.reported_opportunities (profile_id);

CREATE INDEX IF NOT EXISTS
    idx_reported_opportunities_opportunity_id
ON public.reported_opportunities (opportunity_id);

CREATE INDEX IF NOT EXISTS
    idx_reported_opportunities_created_at
ON public.reported_opportunities (created_at DESC);
