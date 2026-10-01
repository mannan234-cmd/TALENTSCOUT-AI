-- 5.20 — Saved Opportunity persistence
-- Stores which opportunities are saved for a profile.

CREATE TABLE IF NOT EXISTS public.saved_opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    profile_id UUID NOT NULL,

    opportunity_id UUID NOT NULL
        REFERENCES public.opportunities(id)
        ON DELETE CASCADE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT saved_opportunities_profile_opportunity_unique
        UNIQUE (profile_id, opportunity_id)
);

CREATE INDEX IF NOT EXISTS
    idx_saved_opportunities_profile_id
ON public.saved_opportunities (profile_id);

CREATE INDEX IF NOT EXISTS
    idx_saved_opportunities_opportunity_id
ON public.saved_opportunities (opportunity_id);
