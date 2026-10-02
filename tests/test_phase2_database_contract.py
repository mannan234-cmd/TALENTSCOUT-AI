
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

MIGRATION = (
    ROOT
    / "supabase/migrations/"
    / "20261002_phase2_database_reproducibility.sql"
)


def read_migration():
    assert MIGRATION.exists(), (
        f"Migration missing: {MIGRATION}"
    )

    return MIGRATION.read_text(
        encoding="utf-8"
    )


def test_cv_table_contract():

    sql = read_migration()

    assert "CREATE TABLE IF NOT EXISTS public.cvs" in sql
    assert "profile_id UUID" in sql
    assert "original_file_name TEXT" in sql
    assert "original_file_path TEXT" in sql
    assert "extracted_text TEXT" in sql
    assert "ai_extraction JSONB" in sql
    assert "ai_analysis JSONB" in sql


def test_certificate_table_contract():

    sql = read_migration()

    assert (
        "CREATE TABLE IF NOT EXISTS public.certificates"
        in sql
    )

    assert "certificate_name TEXT" in sql
    assert "issuing_organization TEXT" in sql
    assert "certificate_file_path TEXT" in sql
    assert "verification_status TEXT" in sql


def test_storage_contract():

    sql = read_migration()

    assert "'cv-documents'" in sql
    assert "'certificate-documents'" in sql

    assert "cv_storage_select_own" in sql
    assert "certificate_storage_select_own" in sql


def test_opportunity_canonical_contract():

    sql = read_migration()

    assert (
        "ADD COLUMN IF NOT EXISTS organization TEXT"
        in sql
    )

    assert (
        "ADD COLUMN IF NOT EXISTS remote BOOLEAN"
        in sql
    )

    assert (
        "ADD COLUMN IF NOT EXISTS skills JSONB"
        in sql
    )

    assert (
        "ADD COLUMN IF NOT EXISTS fingerprint TEXT"
        in sql
    )

    assert (
        "idx_opportunities_fingerprint_unique"
        in sql
    )


def test_profile_based_rls():

    sql = read_migration()

    assert "auth.uid()" in sql
    assert "cvs_select_own" in sql
    assert "certificates_select_own" in sql
