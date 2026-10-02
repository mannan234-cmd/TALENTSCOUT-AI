
-- ============================================================
-- TalentScout AI
-- Phase 1 deployment hardening: authenticated profile ownership
-- ============================================================

ALTER TABLE public.profiles
    ADD COLUMN IF NOT EXISTS user_id UUID;

-- Link every profile to Supabase Auth.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'profiles_user_id_fkey'
          AND conrelid = 'public.profiles'::regclass
    ) THEN
        ALTER TABLE public.profiles
            ADD CONSTRAINT profiles_user_id_fkey
            FOREIGN KEY (user_id)
            REFERENCES auth.users(id)
            ON DELETE CASCADE;
    END IF;
END $$;

-- Backfill existing profiles using matching email.
UPDATE public.profiles AS p
SET user_id = u.id
FROM auth.users AS u
WHERE p.user_id IS NULL
  AND p.email IS NOT NULL
  AND lower(trim(p.email)) = lower(trim(u.email));

-- One profile per authenticated account.
CREATE UNIQUE INDEX IF NOT EXISTS idx_profiles_user_id_unique
    ON public.profiles(user_id)
    WHERE user_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_profiles_user_id
    ON public.profiles(user_id);

-- ------------------------------------------------------------
-- Row Level Security
-- ------------------------------------------------------------

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS profiles_select_own ON public.profiles;
DROP POLICY IF EXISTS profiles_insert_own ON public.profiles;
DROP POLICY IF EXISTS profiles_update_own ON public.profiles;
DROP POLICY IF EXISTS profiles_delete_own ON public.profiles;

CREATE POLICY profiles_select_own
ON public.profiles
FOR SELECT
TO authenticated
USING (user_id = auth.uid());

CREATE POLICY profiles_insert_own
ON public.profiles
FOR INSERT
TO authenticated
WITH CHECK (user_id = auth.uid());

CREATE POLICY profiles_update_own
ON public.profiles
FOR UPDATE
TO authenticated
USING (user_id = auth.uid())
WITH CHECK (user_id = auth.uid());

CREATE POLICY profiles_delete_own
ON public.profiles
FOR DELETE
TO authenticated
USING (user_id = auth.uid());
