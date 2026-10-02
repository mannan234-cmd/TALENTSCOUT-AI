
-- ============================================================
-- Phase 2 Security Fix
-- Remove legacy unrestricted CV/Certificate policies.
-- Ownership policies remain unchanged.
-- ============================================================

DROP POLICY IF EXISTS "Allow CV deletes"
ON public.cvs;

DROP POLICY IF EXISTS "Allow CV inserts"
ON public.cvs;

DROP POLICY IF EXISTS "Allow CV reads"
ON public.cvs;

DROP POLICY IF EXISTS "Allow CV updates"
ON public.cvs;


DROP POLICY IF EXISTS "Allow certificate deletes"
ON public.certificates;

DROP POLICY IF EXISTS "Allow certificate inserts"
ON public.certificates;

DROP POLICY IF EXISTS "Allow certificate reads"
ON public.certificates;

DROP POLICY IF EXISTS "Allow certificate updates"
ON public.certificates;
