from __future__ import annotations

import json

from typing import Any

from app.models.opportunity import (
    Opportunity,
    OpportunitySearchFilters,
)
from app.services.supabase_service import SupabaseService


class OpportunitySearchServiceError(ValueError):
    """Raised when Opportunity search cannot be completed."""


class OpportunitySearchService:
    """
    Production Opportunity search service.

    Responsibilities:
    - validate search filters
    - build the Supabase query
    - apply supported filters
    - paginate results
    - convert database rows into Opportunity models
    - ignore database-only fields such as created_at
    """

    TABLE_NAME = "opportunities"

    @staticmethod
    def _clean_db_row(row: dict[str, Any]) -> dict[str, Any]:
        """
        Remove database-only fields that are not part of Opportunity.
        """
        cleaned = dict(row)
        cleaned.pop("created_at", None)
        return cleaned

    @classmethod
    def _build_query(
        cls,
        filters: OpportunitySearchFilters,
    ):
        """
        Build the Supabase query for the supplied filters.
        """
        client = SupabaseService().supabase

        query = client.table(cls.TABLE_NAME).select("*")

        if filters.query:
            search_term = str(filters.query).strip()

            if search_term:
                escaped = (
                    search_term
                    .replace("%", r"\%")
                    .replace("_", r"\_")
                )

                query = query.or_(
                    f"title.ilike.%{escaped}%,"
                    f"organization.ilike.%{escaped}%,"
                    f"description.ilike.%{escaped}%"
                )

        if filters.opportunity_types:
            values = [
                item.value
                if hasattr(item, "value")
                else str(item)
                for item in filters.opportunity_types
            ]
            query = query.in_("opportunity_type", values)

        if filters.verification_statuses:
            values = [
                item.value
                if hasattr(item, "value")
                else str(item)
                for item in filters.verification_statuses
            ]
            query = query.in_("verification_status", values)

        if filters.location:
            location = str(filters.location).strip()
            if location:
                query = query.ilike(
                    "location",
                    f"%{location}%"
                )

        if filters.remote is not None:
            query = query.eq("remote", filters.remote)

        if filters.organization:
            organization = str(filters.organization).strip()
            if organization:
                query = query.ilike(
                    "organization",
                    f"%{organization}%"
                )

        if filters.skills:
            skills = [
                str(skill).strip()
                for skill in filters.skills
                if str(skill).strip()
            ]

            if skills:
                # PostgreSQL skills is JSONB. PostgREST expects
                # the JSON array representation for contains().
                query = query.contains(
                    "skills",
                    json.dumps(skills),
                )

        if filters.deadline_from is not None:
            query = query.gte(
                "deadline",
                filters.deadline_from.isoformat(),
            )

        if filters.deadline_to is not None:
            query = query.lte(
                "deadline",
                filters.deadline_to.isoformat(),
            )

        query = (
            query
            .order("deadline", desc=False, nullsfirst=False)
            .order("updated_at", desc=True)
            .range(
                filters.offset,
                filters.offset + filters.limit - 1,
            )
        )

        return query

    @classmethod
    def search(
        cls,
        filters: OpportunitySearchFilters | None = None,
    ) -> list[Opportunity]:
        """
        Search persisted opportunities using the canonical
        OpportunitySearchFilters contract.
        """
        if filters is None:
            filters = OpportunitySearchFilters()

        if not isinstance(filters, OpportunitySearchFilters):
            raise OpportunitySearchServiceError(
                "search() requires OpportunitySearchFilters."
            )

        try:
            query = cls._build_query(filters)
            response = query.execute()

            rows = response.data or []

            opportunities: list[Opportunity] = []

            for row in rows:
                if not isinstance(row, dict):
                    raise OpportunitySearchServiceError(
                        "Supabase returned an invalid Opportunity row."
                    )

                cleaned = cls._clean_db_row(row)

                opportunities.append(
                    Opportunity.model_validate(cleaned)
                )

            return opportunities

        except OpportunitySearchServiceError:
            raise

        except Exception as exc:
            raise OpportunitySearchServiceError(
                f"Opportunity search failed: {exc}"
            ) from exc

    @classmethod
    def search_one(
        cls,
        filters: OpportunitySearchFilters,
    ) -> Opportunity | None:
        """
        Return the first matching opportunity, if any.
        """
        results = cls.search(
            filters.model_copy(update={"limit": 1})
        )

        return results[0] if results else None
