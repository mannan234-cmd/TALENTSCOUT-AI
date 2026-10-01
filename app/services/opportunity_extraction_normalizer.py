
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from app.models.opportunity_collection import CollectedOpportunity
from app.models.opportunity_extraction import AIOpportunityExtraction


class AIOpportunityExtractionNormalizationError(ValueError):
    """Raised when AI extraction cannot be safely normalized."""


class AIOpportunityExtractionNormalizer:
    """
    Converts validated AI extraction output into the existing
    CollectedOpportunity contract.

    This layer deliberately performs no AI reasoning. It only
    normalizes and validates already-extracted source data.
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
    def _clean_list(values: list[str]) -> list[str]:
        result: list[str] = []
        seen: set[str] = set()

        for value in values:
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
    def _parse_deadline(
        value: Optional[str],
    ) -> Optional[datetime]:
        if value is None:
            return None

        value = str(value).strip()

        if not value:
            return None

        try:
            parsed = datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
        except ValueError as exc:
            raise AIOpportunityExtractionNormalizationError(
                f"Invalid extracted deadline: {value}"
            ) from exc

        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise AIOpportunityExtractionNormalizationError(
                "Extracted deadline must be timezone-aware."
            )

        return parsed.astimezone(timezone.utc)

    @classmethod
    def normalize(
        cls,
        extraction: AIOpportunityExtraction,
        *,
        source_name: Optional[str] = None,
        source_url: Optional[str] = None,
    ) -> CollectedOpportunity:

        if not isinstance(
            extraction,
            AIOpportunityExtraction,
        ):
            raise AIOpportunityExtractionNormalizationError(
                "extraction must be AIOpportunityExtraction."
            )

        title = extraction.title.strip()
        organization = extraction.organization.strip()

        if len(title) < 3:
            raise AIOpportunityExtractionNormalizationError(
                "Extracted title is empty or too short."
            )

        if len(organization) < 2:
            raise AIOpportunityExtractionNormalizationError(
                "Extracted organization is empty or too short."
            )

        opportunity_type = (
            extraction.opportunity_type.strip().lower()
            or "other"
        )

        if opportunity_type not in cls.ALLOWED_TYPES:
            opportunity_type = "other"

        deadline = cls._parse_deadline(
            extraction.deadline
        )

        metadata = {
            "ai_extracted": True,
            "extraction_version": "1.1",
        }

        if extraction.extraction_notes:
            metadata["extraction_notes"] = cls._clean_list(
                extraction.extraction_notes
            )

        return CollectedOpportunity(
            title=title,
            organization=organization,
            description=extraction.description.strip(),
            location=(
                extraction.location.strip()
                if extraction.location
                else None
            ),
            remote=extraction.remote,
            opportunity_type=opportunity_type,
            eligibility=cls._clean_list(
                extraction.eligibility
            ),
            requirements=cls._clean_list(
                extraction.requirements
            ),
            skills=cls._clean_list(
                extraction.skills
            ),
            benefits=cls._clean_list(
                extraction.benefits
            ),
            application_url=extraction.application_url,
            source_url=source_url or extraction.application_url,
            source_name=source_name,
            deadline=deadline,
            tags=cls._clean_list(
                extraction.tags
            ),
            metadata=metadata,
            collected_at=datetime.now(timezone.utc),
        )
