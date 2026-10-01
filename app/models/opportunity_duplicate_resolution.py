
from typing import List

from pydantic import BaseModel, Field

from app.models.opportunity import Opportunity
from app.services.opportunity_identity_service import (
    OpportunityIdentityService,
)


class OpportunityDuplicateResolutionResult(BaseModel):
    """
    Structured result for one duplicate-identity group.

    This model represents opportunity identity and provenance
    resolution only. It does not perform student matching,
    scoring, ranking, recommendation, or personalization.
    """

    fingerprint: str = Field(min_length=1)

    canonical_record_index: int = Field(ge=0)

    duplicate_record_indices: List[int] = Field(
        default_factory=list
    )

    source_urls: List[str] = Field(
        default_factory=list
    )

    source_names: List[str] = Field(
        default_factory=list
    )

    record_count: int = Field(ge=1)

    duplicate_count: int = Field(ge=0)

    @classmethod
    def from_records(
        cls,
        records: List[Opportunity],
        canonical_record_index: int,
    ) -> "OpportunityDuplicateResolutionResult":

        if not records:
            raise ValueError(
                "At least one opportunity record is required."
            )

        if not 0 <= canonical_record_index < len(records):
            raise ValueError(
                "canonical_record_index is out of range."
            )

        fingerprint = OpportunityIdentityService.fingerprint(
            records[canonical_record_index]
        )

        duplicate_indices = [
            index
            for index in range(len(records))
            if index != canonical_record_index
        ]

        source_urls = sorted(
            {
                str(record.source_url).strip()
                for record in records
                if record.source_url
                and str(record.source_url).strip()
            },
            key=str.casefold,
        )

        source_names = sorted(
            {
                str(record.source_name).strip()
                for record in records
                if record.source_name
                and str(record.source_name).strip()
            },
            key=str.casefold,
        )

        return cls(
            fingerprint=fingerprint,
            canonical_record_index=canonical_record_index,
            duplicate_record_indices=duplicate_indices,
            source_urls=source_urls,
            source_names=source_names,
            record_count=len(records),
            duplicate_count=len(duplicate_indices),
        )
