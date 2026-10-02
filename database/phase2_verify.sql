
-- ============================================================
-- TalentScout AI — Phase 2 Verification
-- Run this in Supabase SQL Editor
-- ============================================================


-- 1. Tables

SELECT
    table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
      'profiles',
      'cvs',
      'certificates',
      'opportunities'
  )
ORDER BY table_name;


-- 2. CV columns

SELECT
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'cvs'
ORDER BY ordinal_position;


-- 3. Certificate columns

SELECT
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'certificates'
ORDER BY ordinal_position;


-- 4. Opportunity canonical columns

SELECT
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'opportunities'
  AND column_name IN (
      'organization',
      'remote',
      'eligibility',
      'requirements',
      'skills',
      'benefits',
      'source_type',
      'fingerprint',
      'tags',
      'metadata',
      'collected_at'
  )
ORDER BY column_name;


-- 5. RLS status

SELECT
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN (
      'profiles',
      'cvs',
      'certificates',
      'opportunities'
  )
ORDER BY tablename;


-- 6. Storage buckets

SELECT
    id,
    name,
    public
FROM storage.buckets
WHERE id IN (
    'cv-documents',
    'certificate-documents'
)
ORDER BY id;


-- 7. CV policies

SELECT
    policyname,
    cmd
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename = 'cvs'
ORDER BY policyname;


-- 8. Certificate policies

SELECT
    policyname,
    cmd
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename = 'certificates'
ORDER BY policyname;
