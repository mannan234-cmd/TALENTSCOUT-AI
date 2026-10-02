
SELECT
    EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name = 'cvs'
    ) AS cvs_table,

    EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name = 'certificates'
    ) AS certificates_table,

    (
        SELECT COUNT(*)
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'cvs'
          AND column_name IN (
              'profile_id',
              'original_file_name',
              'original_file_path',
              'extracted_text',
              'ai_extraction',
              'ai_analysis',
              'ai_matching',
              'ai_recommendations'
          )
    ) = 8 AS cvs_columns,

    (
        SELECT COUNT(*)
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'certificates'
          AND column_name IN (
              'profile_id',
              'certificate_name',
              'issuing_organization',
              'certificate_file_path',
              'verification_status'
          )
    ) = 5 AS certificate_columns,

    (
        SELECT COUNT(*)
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
              'verified_at',
              'fingerprint',
              'tags',
              'metadata',
              'collected_at'
          )
    ) = 12 AS opportunity_columns,

    (
        SELECT rowsecurity
        FROM pg_tables
        WHERE schemaname = 'public'
          AND tablename = 'cvs'
    ) AS cvs_rls,

    (
        SELECT rowsecurity
        FROM pg_tables
        WHERE schemaname = 'public'
          AND tablename = 'certificates'
    ) AS certificates_rls,

    EXISTS (
        SELECT 1
        FROM storage.buckets
        WHERE id = 'cv-documents'
          AND public = FALSE
    ) AS cv_bucket_private,

    EXISTS (
        SELECT 1
        FROM storage.buckets
        WHERE id = 'certificate-documents'
          AND public = FALSE
    ) AS certificate_bucket_private,

    (
        SELECT COUNT(*)
        FROM pg_policies
        WHERE schemaname = 'public'
          AND tablename = 'cvs'
          AND policyname IN (
              'cvs_select_own',
              'cvs_insert_own',
              'cvs_update_own',
              'cvs_delete_own'
          )
    ) = 4 AS cvs_own_policies,

    (
        SELECT COUNT(*)
        FROM pg_policies
        WHERE schemaname = 'public'
          AND tablename = 'certificates'
          AND policyname IN (
              'certificates_select_own',
              'certificates_insert_own',
              'certificates_update_own',
              'certificates_delete_own'
          )
    ) = 4 AS certificate_own_policies;
