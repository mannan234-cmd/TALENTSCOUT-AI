-- ============================================================
-- TalentScout_AI — Phase 5.1
-- Opportunity Database
-- ============================================================

CREATE TABLE IF NOT EXISTS public.opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    title TEXT NOT NULL,
    organization TEXT NOT NULL,

    opportunity_type TEXT NOT NULL DEFAULT 'other',

    description TEXT NOT NULL DEFAULT '',

    location TEXT,
    remote BOOLEAN,

    eligibility JSONB NOT NULL DEFAULT '[]'::jsonb,
    requirements JSONB NOT NULL DEFAULT '[]'::jsonb,
    skills JSONB NOT NULL DEFAULT '[]'::jsonb,
    benefits JSONB NOT NULL DEFAULT '[]'::jsonb,

    application_url TEXT,
    source_url TEXT,

    source_name TEXT,
    source_type TEXT NOT NULL DEFAULT 'other',

    deadline TIMESTAMPTZ,

    verification_status TEXT NOT NULL DEFAULT 'needs_verification',
    verified_at TIMESTAMPTZ,

    fingerprint TEXT,

    tags JSONB NOT NULL DEFAULT '[]'::jsonb,

    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    collected_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT opportunities_title_not_empty
        CHECK (length(trim(title)) >= 3),

    CONSTRAINT opportunities_organization_not_empty
        CHECK (length(trim(organization)) >= 2),

    CONSTRAINT opportunities_type_valid
        CHECK (
            opportunity_type IN (
                'job',
                'internship',
                'scholarship',
                'fellowship',
                'competition',
                'hackathon',
                'grant',
                'apprenticeship',
                'training',
                'other'
            )
        ),

    CONSTRAINT opportunities_source_type_valid
        CHECK (
            source_type IN (
                'official',
                'university',
                'government',
                'company',
                'nonprofit',
                'aggregator',
                'other'
            )
        ),

    CONSTRAINT opportunities_verification_status_valid
        CHECK (
            verification_status IN (
                'verified',
                'needs_verification',
                'expired'
            )
        )
);

CREATE INDEX IF NOT EXISTS idx_opportunities_type
    ON public.opportunities(opportunity_type);

CREATE INDEX IF NOT EXISTS idx_opportunities_verification_status
    ON public.opportunities(verification_status);

CREATE INDEX IF NOT EXISTS idx_opportunities_deadline
    ON public.opportunities(deadline);

CREATE INDEX IF NOT EXISTS idx_opportunities_organization
    ON public.opportunities(organization);

CREATE INDEX IF NOT EXISTS idx_opportunities_source_url
    ON public.opportunities(source_url);

CREATE UNIQUE INDEX IF NOT EXISTS idx_opportunities_fingerprint_unique
    ON public.opportunities(fingerprint)
    WHERE fingerprint IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_opportunities_skills_gin
    ON public.opportunities
    USING GIN(skills);

CREATE INDEX IF NOT EXISTS idx_opportunities_tags_gin
    ON public.opportunities
    USING GIN(tags);

ALTER TABLE public.opportunities ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "opportunities_select_authenticated"
    ON public.opportunities;

CREATE POLICY "opportunities_select_authenticated"
ON public.opportunities
FOR SELECT
TO authenticated
USING (true);

DROP POLICY IF EXISTS "opportunities_insert_authenticated"
    ON public.opportunities;

CREATE POLICY "opportunities_insert_authenticated"
ON public.opportunities
FOR INSERT
TO authenticated
WITH CHECK (true);

DROP POLICY IF EXISTS "opportunities_update_authenticated"
    ON public.opportunities;

CREATE POLICY "opportunities_update_authenticated"
ON public.opportunities
FOR UPDATE
TO authenticated
USING (true)
WITH CHECK (true);

DROP POLICY IF EXISTS "opportunities_delete_authenticated"
    ON public.opportunities;

CREATE POLICY "opportunities_delete_authenticated"
ON public.opportunities
FOR DELETE
TO authenticated
USING (true);
