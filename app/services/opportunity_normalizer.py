from datetime import datetime, timezone
from typing import Optional

from app.models.opportunity import Opportunity
from app.models.opportunity_collection import CollectedOpportunity


class OpportunityNormalizationError(ValueError):
    """Raised when a collected opportunity cannot be normalized."""


class OpportunityNormalizer:
    """
    Converts a CollectedOpportunity into the canonical Opportunity model.
    """

    ALLOWED_TYPES = {
        "job",
        "internship",
        "scholarship",
        "fellowship",
        "competition",
        "hackathon",
        "grant",
        "apprenticeship",
        "training",
        "other",
    }

    @staticmethod
    def _clean_text(value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        value = str(value).strip()

        return value if value else None

    @staticmethod
    def _clean_required_text(
        value: str,
        field_name: str,
    ) -> str:
        cleaned = OpportunityNormalizer._clean_text(value)

        if not cleaned:
            raise OpportunityNormalizationError(
                f"{field_name} is required and cannot be empty."
            )

        return cleaned

    @staticmethod
    def _clean_list(values):
        """
        Trim strings, remove empty values, and deduplicate
        case-insensitively while preserving first occurrence.
        """
        result = []
        seen = set()

        for value in values or []:
            if value is None:
                continue

            cleaned = str(value).strip()

            if not cleaned:
                continue

            key = cleaned.casefold()

            if key in seen:
                continue

            seen.add(key)
            result.append(cleaned)

        return result

    @staticmethod
    def _normalize_type(value: Optional[str]) -> str:
        if not value:
            return "other"

        normalized = str(value).strip().casefold()

        if normalized in OpportunityNormalizer.ALLOWED_TYPES:
            return normalized

        return "other"

    @staticmethod
    def _utc(
        value: Optional[datetime],
    ) -> Optional[datetime]:
        if value is None:
            return None

        if value.tzinfo is None or value.utcoffset() is None:
            raise OpportunityNormalizationError(
                "Datetime values must be timezone-aware."
            )

        return value.astimezone(timezone.utc)

    @classmethod
    def normalize(
        cls,
        collected: CollectedOpportunity,
    ) -> Opportunity:
        if not isinstance(
            collected,
            CollectedOpportunity,
        ):
            raise OpportunityNormalizationError(
                "normalize() requires a CollectedOpportunity."
            )

        title = cls._clean_required_text(
            collected.title,
            "title",
        )

        organization = cls._clean_required_text(
            collected.organization,
            "organization",
        )

        source_name = cls._clean_text(
            collected.source_name
        )

        collected_at = cls._utc(
            collected.collected_at
        )

        if collected_at is None:
            collected_at = datetime.now(timezone.utc)

        metadata = dict(
            collected.metadata or {}
        )

        metadata.setdefault(
            "normalized",
            True,
        )

        metadata.setdefault(
            "normalization_version",
            "1.0",
        )

        if source_name:
            metadata.setdefault(
                "source_name",
                source_name,
            )

        if collected.source_url:
            metadata.setdefault(
                "source_url",
                str(collected.source_url),
            )

        if collected.application_url:
            metadata.setdefault(
                "application_url",
                str(collected.application_url),
            )

        return Opportunity(
            title=title,
            organization=organization,
            opportunity_type=cls._normalize_type(
                collected.opportunity_type
            ),
            description=(
                cls._clean_text(
                    collected.description
                )
                or ""
            ),
            location=cls._clean_text(
                collected.location
            ),
            remote=collected.remote,
            eligibility=cls._clean_list(
                collected.eligibility
            ),
            requirements=cls._clean_list(
                collected.requirements
            ),
            skills=cls._clean_list(
                collected.skills
            ),
            benefits=cls._clean_list(
                collected.benefits
            ),
            application_url=collected.application_url,
            source_url=collected.source_url,
            source_name=source_name,
            source_type=collected.source_type,
            deadline=cls._utc(
                collected.deadline
            ),
            verification_status="needs_verification",
            verified_at=None,
            fingerprint=None,
            tags=cls._clean_list(
                collected.tags
            ),
            metadata=metadata,
            collected_at=collected_at,
            updated_at=collected_at,
        )
