CREATE TABLE IF NOT EXISTS cv_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cv_id UUID NOT NULL REFERENCES cvs(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    label TEXT NOT NULL DEFAULT '',
    professional_cv JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT cv_versions_unique_version
        UNIQUE (cv_id, version_number)
);

CREATE INDEX IF NOT EXISTS idx_cv_versions_cv_id
    ON cv_versions(cv_id);

CREATE INDEX IF NOT EXISTS idx_cv_versions_created_at
    ON cv_versions(created_at DESC);
