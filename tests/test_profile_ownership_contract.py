from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_profile_ownership_migration_exists():

    migration = (
        ROOT
        / "database/migrations/"
        / "20261002_add_profile_user_ownership.sql"
    )

    sql = migration.read_text(
        encoding="utf-8"
    )

    assert "ADD COLUMN IF NOT EXISTS user_id UUID" in sql
    assert "REFERENCES auth.users(id)" in sql
    assert "auth.uid()" in sql


def test_profile_service_enforces_ownership():

    source = (
        ROOT
        / "app/services/profile_service.py"
    ).read_text(
        encoding="utf-8"
    )

    assert 'profile_data["user_id"] = user_id' in source
    assert '.eq("user_id", user_id)' in source
    assert 'profile_data.pop("user_id", None)' in source


def test_supabase_service_has_security_boundary():

    source = (
        ROOT
        / "app/services/supabase_service.py"
    ).read_text(
        encoding="utf-8"
    )

    assert "admin_client" in source
    assert "SUPABASE_SERVICE_ROLE_KEY" in source
