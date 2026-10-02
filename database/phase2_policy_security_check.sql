
SELECT
    tablename,
    policyname,
    cmd,
    permissive,
    roles,
    qual,
    with_check
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename IN ('cvs', 'certificates')
ORDER BY tablename, policyname;
