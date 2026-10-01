
-- ============================================================
-- TalentScout AI
-- Phase 2 - Core Supabase / PostgreSQL Schema
-- ============================================================


-- ============================================================
-- 1. PROFILES
-- ============================================================

CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    full_name TEXT NOT NULL,
    email TEXT UNIQUE,

    phone TEXT,
    location TEXT,

    bio TEXT,
    career_summary TEXT,

    interests TEXT[],
    certifications TEXT[],
    achievements TEXT[],

    career_level TEXT,

    years_of_experience NUMERIC(4,1) DEFAULT 0,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
-- 2. SKILLS
-- ============================================================

CREATE TABLE IF NOT EXISTS skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    profile_id UUID NOT NULL
        REFERENCES profiles(id)
        ON DELETE CASCADE,

    skill_name TEXT NOT NULL,

    skill_category TEXT,

    proficiency_level TEXT,

    years_of_experience NUMERIC(4,1),

    source TEXT,

    is_verified BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
-- 3. EDUCATION
-- ============================================================

CREATE TABLE IF NOT EXISTS education (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    profile_id UUID NOT NULL
        REFERENCES profiles(id)
        ON DELETE CASCADE,

    institution_name TEXT NOT NULL,

    degree TEXT,

    field_of_study TEXT,

    start_date DATE,
    end_date DATE,

    currently_studying BOOLEAN NOT NULL DEFAULT FALSE,

    grade TEXT,
    description TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
-- 4. PROJECTS
-- ============================================================

CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    profile_id UUID NOT NULL
        REFERENCES profiles(id)
        ON DELETE CASCADE,

    project_name TEXT NOT NULL,

    description TEXT,

    project_url TEXT,
    github_url TEXT,

    technologies TEXT[],

    role TEXT,
    outcomes TEXT,

    start_date DATE,
    end_date DATE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
-- 5. EXPERIENCES
-- ============================================================

CREATE TABLE IF NOT EXISTS experiences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    profile_id UUID NOT NULL
        REFERENCES profiles(id)
        ON DELETE CASCADE,

    organization_name TEXT NOT NULL,

    job_title TEXT NOT NULL,

    employment_type TEXT,
    location TEXT,

    start_date DATE,
    end_date DATE,

    currently_working BOOLEAN NOT NULL DEFAULT FALSE,

    description TEXT,

    achievements TEXT[],

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
-- 6. CAREER GOALS
-- ============================================================

CREATE TABLE IF NOT EXISTS career_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    profile_id UUID NOT NULL
        REFERENCES profiles(id)
        ON DELETE CASCADE,

    goal_title TEXT NOT NULL,

    target_role TEXT,
    target_industry TEXT,
    target_location TEXT,
    target_timeline TEXT,

    description TEXT,

    priority TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'active',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
-- 7. OPPORTUNITIES
-- ============================================================

CREATE TABLE IF NOT EXISTS opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    title TEXT NOT NULL,
    organization_name TEXT NOT NULL,

    description TEXT,

    opportunity_type TEXT,
    category TEXT,

    location TEXT,
    work_mode TEXT,

    eligibility TEXT,

    required_skills TEXT[],
    preferred_skills TEXT[],

    education_requirements TEXT,

    deadline TIMESTAMPTZ,

    application_url TEXT,
    source_url TEXT,
    source_name TEXT,

    verification_status TEXT DEFAULT 'needs_verification',

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    last_checked_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
-- 8. MATCHES
-- ============================================================

CREATE TABLE IF NOT EXISTS matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    profile_id UUID NOT NULL
        REFERENCES profiles(id)
        ON DELETE CASCADE,

    opportunity_id UUID NOT NULL
        REFERENCES opportunities(id)
        ON DELETE CASCADE,

    match_score NUMERIC(5,2),

    eligible BOOLEAN,

    matched_skills TEXT[],
    missing_skills TEXT[],

    education_match BOOLEAN,
    experience_match BOOLEAN,
    interest_match BOOLEAN,
    career_goal_match BOOLEAN,

    category TEXT,

    reason TEXT,

    next_actions TEXT[],

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(profile_id, opportunity_id)
);


-- ============================================================
-- 9. SKILL GAPS
-- ============================================================

CREATE TABLE IF NOT EXISTS skill_gaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    profile_id UUID NOT NULL
        REFERENCES profiles(id)
        ON DELETE CASCADE,

    opportunity_id UUID
        REFERENCES opportunities(id)
        ON DELETE SET NULL,

    skill_name TEXT NOT NULL,

    importance TEXT,

    current_level TEXT,
    target_level TEXT,

    gap_description TEXT,

    status TEXT DEFAULT 'identified',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
-- 10. LEARNING PLANS
-- ============================================================

CREATE TABLE IF NOT EXISTS learning_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    profile_id UUID NOT NULL
        REFERENCES profiles(id)
        ON DELETE CASCADE,

    skill_gap_id UUID
        REFERENCES skill_gaps(id)
        ON DELETE SET NULL,

    skill_name TEXT NOT NULL,

    learning_goal TEXT,

    learn_steps TEXT[],
    practice_tasks TEXT[],

    project_idea TEXT,

    proof_strategy TEXT,

    estimated_duration_days INTEGER,

    status TEXT DEFAULT 'not_started',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
-- 11. APPLICATIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    profile_id UUID NOT NULL
        REFERENCES profiles(id)
        ON DELETE CASCADE,

    opportunity_id UUID NOT NULL
        REFERENCES opportunities(id)
        ON DELETE CASCADE,

    status TEXT NOT NULL DEFAULT 'saved',

    applied_at TIMESTAMPTZ,

    deadline TIMESTAMPTZ,

    notes TEXT,

    rejection_reason TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(profile_id, opportunity_id)
);


-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_skills_profile_id
    ON skills(profile_id);

CREATE INDEX IF NOT EXISTS idx_education_profile_id
    ON education(profile_id);

CREATE INDEX IF NOT EXISTS idx_projects_profile_id
    ON projects(profile_id);

CREATE INDEX IF NOT EXISTS idx_experiences_profile_id
    ON experiences(profile_id);

CREATE INDEX IF NOT EXISTS idx_career_goals_profile_id
    ON career_goals(profile_id);

CREATE INDEX IF NOT EXISTS idx_matches_profile_id
    ON matches(profile_id);

CREATE INDEX IF NOT EXISTS idx_matches_opportunity_id
    ON matches(opportunity_id);

CREATE INDEX IF NOT EXISTS idx_skill_gaps_profile_id
    ON skill_gaps(profile_id);

CREATE INDEX IF NOT EXISTS idx_learning_plans_profile_id
    ON learning_plans(profile_id);

CREATE INDEX IF NOT EXISTS idx_applications_profile_id
    ON applications(profile_id);

CREATE INDEX IF NOT EXISTS idx_applications_opportunity_id
    ON applications(opportunity_id);

CREATE INDEX IF NOT EXISTS idx_opportunities_deadline
    ON opportunities(deadline);

CREATE INDEX IF NOT EXISTS idx_opportunities_active
    ON opportunities(is_active);
