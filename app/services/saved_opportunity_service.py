from __future__ import annotations

from typing import Any

from app.services.supabase_service import SupabaseService


class SavedOpportunityServiceError(ValueError):
    """Raised when a saved-opportunity operation is invalid."""


class SavedOpportunityService:
    """Persistence service for profile-specific saved opportunities."""

    TABLE_NAME = "saved_opportunities"

    @classmethod
    def _validate_ids(
        cls,
        profile_id: str,
        opportunity_id: str,
    ) -> None:
        if not profile_id:
            raise SavedOpportunityServiceError(
                "profile_id cannot be empty."
            )

        if not opportunity_id:
            raise SavedOpportunityServiceError(
                "opportunity_id cannot be empty."
            )

    @classmethod
    def save(
        cls,
        profile_id: str,
        opportunity_id: str,
    ) -> dict[str, Any]:
        """Save an opportunity for a profile.

        The database unique constraint makes this operation idempotent:
        the same profile/opportunity pair cannot be stored twice.
        """
        cls._validate_ids(
            profile_id,
            opportunity_id,
        )

        client = SupabaseService().supabase

        payload = {
            "profile_id": str(profile_id),
            "opportunity_id": str(opportunity_id),
        }

        response = (
            client
            .table(cls.TABLE_NAME)
            .upsert(
                payload,
                on_conflict="profile_id,opportunity_id",
            )
            .execute()
        )

        if not response.data:
            raise SavedOpportunityServiceError(
                "Supabase did not return the saved opportunity."
            )

        return dict(response.data[0])

    @classmethod
    def unsave(
        cls,
        profile_id: str,
        opportunity_id: str,
    ) -> bool:
        """Remove a saved opportunity from a profile."""
        cls._validate_ids(
            profile_id,
            opportunity_id,
        )

        client = SupabaseService().supabase

        response = (
            client
            .table(cls.TABLE_NAME)
            .delete()
            .eq("profile_id", str(profile_id))
            .eq("opportunity_id", str(opportunity_id))
            .execute()
        )

        return bool(response.data)

    @classmethod
    def is_saved(
        cls,
        profile_id: str,
        opportunity_id: str,
    ) -> bool:
        """Return whether an opportunity is saved for a profile."""
        cls._validate_ids(
            profile_id,
            opportunity_id,
        )

        client = SupabaseService().supabase

        response = (
            client
            .table(cls.TABLE_NAME)
            .select("id")
            .eq("profile_id", str(profile_id))
            .eq("opportunity_id", str(opportunity_id))
            .limit(1)
            .execute()
        )

        return bool(response.data)

    @classmethod
    def list_saved(
        cls,
        profile_id: str,
    ) -> list[dict[str, Any]]:
        """Return saved opportunities for a profile."""
        if not profile_id:
            raise SavedOpportunityServiceError(
                "profile_id cannot be empty."
            )

        client = SupabaseService().supabase

        response = (
            client
            .table(cls.TABLE_NAME)
            .select("*")
            .eq("profile_id", str(profile_id))
            .order("created_at", desc=True)
            .execute()
        )

        return [
            dict(row)
            for row in (response.data or [])
        ]
