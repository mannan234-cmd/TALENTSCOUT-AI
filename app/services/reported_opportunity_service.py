from __future__ import annotations

from typing import Any

from app.services.supabase_service import SupabaseService


class ReportedOpportunityServiceError(ValueError):
    """Raised when a reported-opportunity operation is invalid."""


class ReportedOpportunityService:
    """Persistence service for opportunity reports."""

    TABLE_NAME = "reported_opportunities"

    @classmethod
    def _validate_ids(
        cls,
        profile_id: str,
        opportunity_id: str,
    ) -> None:
        if not profile_id:
            raise ReportedOpportunityServiceError(
                "profile_id cannot be empty."
            )

        if not opportunity_id:
            raise ReportedOpportunityServiceError(
                "opportunity_id cannot be empty."
            )

    @classmethod
    def _validate_reason(cls, reason: str) -> str:
        normalized = str(reason).strip()

        if not normalized:
            raise ReportedOpportunityServiceError(
                "reason cannot be empty."
            )

        return normalized

    @classmethod
    def save(
        cls,
        profile_id: str,
        opportunity_id: str,
        reason: str,
    ) -> dict[str, Any]:
        cls._validate_ids(profile_id, opportunity_id)
        normalized_reason = cls._validate_reason(reason)

        client = SupabaseService().supabase

        payload = {
            "profile_id": str(profile_id),
            "opportunity_id": str(opportunity_id),
            "reason": normalized_reason,
        }

        response = (
            client
            .table(cls.TABLE_NAME)
            .select("*")
            .eq("profile_id", str(profile_id))
            .eq("opportunity_id", str(opportunity_id))
            .eq("reason", normalized_reason)
            .limit(1)
            .execute()
        )

        if response.data:
            return dict(response.data[0])

        insert_response = (
            client
            .table(cls.TABLE_NAME)
            .insert(payload)
            .execute()
        )

        if not insert_response.data:
            raise ReportedOpportunityServiceError(
                "Supabase did not return the saved report."
            )

        return dict(insert_response.data[0])

    @classmethod
    def is_reported(
        cls,
        profile_id: str,
        opportunity_id: str,
        reason: str | None = None,
    ) -> bool:
        cls._validate_ids(profile_id, opportunity_id)

        client = SupabaseService().supabase

        query = (
            client
            .table(cls.TABLE_NAME)
            .select("id")
            .eq("profile_id", str(profile_id))
            .eq("opportunity_id", str(opportunity_id))
        )

        if reason is not None:
            query = query.eq(
                "reason",
                cls._validate_reason(reason),
            )

        response = query.limit(1).execute()

        return bool(response.data)

    @classmethod
    def list_reports(
        cls,
        profile_id: str,
    ) -> list[dict[str, Any]]:
        if not profile_id:
            raise ReportedOpportunityServiceError(
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
