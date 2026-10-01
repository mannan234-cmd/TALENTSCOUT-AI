
from typing import List

from app.models.opportunity import Opportunity
from app.models.opportunity_duplicate_resolution import OpportunityDuplicateResolutionResult
from app.services.opportunity_identity_service import OpportunityIdentityService


class OpportunityDuplicateResolutionError(ValueError):
    """Raised when duplicate resolution cannot be completed."""


class OpportunityDuplicateResolutionService:
    """
    Resolves multiple records representing the same opportunity.

    This service:
    - does NOT rank opportunities for students
    - does NOT calculate student-match scores
    - does NOT recommend opportunities
    - only selects a deterministic canonical source record
    """

    @staticmethod
    def _text_present(value) -> bool:
        if value is None:
            return False

        return bool(str(value).strip())

    @classmethod
    def canonical_record_key(
        cls,
        opportunity: Opportunity,
    ):
        """
        Build a deterministic source-record completeness key.

        Higher completeness wins.

        Tie-breakers are deterministic and are not student
        preference or opportunity-quality rankings.
        """

        completeness = sum(
            [
                cls._text_present(
                    opportunity.description
                ),
                cls._text_present(
                    opportunity.location
                ),
                opportunity.remote is not None,
                bool(opportunity.eligibility),
                bool(opportunity.requirements),
                bool(opportunity.skills),
                bool(opportunity.benefits),
                cls._text_present(
                    opportunity.application_url
                ),
                cls._text_present(
                    opportunity.deadline
                ),
                bool(opportunity.tags),
            ]
        )

        return (
            completeness,
            len(
                opportunity.description or ""
            ),
            len(
                opportunity.requirements or []
            ),
            len(
                opportunity.skills or []
            ),
            len(
                opportunity.benefits or []
            ),
            len(
                opportunity.eligibility or []
            ),
            len(
                opportunity.tags or []
            ),
            int(
                cls._text_present(
                    opportunity.application_url
                )
            ),
            (
                str(
                    opportunity.source_name or ""
                ).casefold()
            ),
        )

    @classmethod
    def select_canonical_record(
        cls,
        opportunities: List[Opportunity],
    ) -> int:
        """
        Return the canonical record index.

        The method intentionally operates only on the supplied
        source records. It does not perform student matching.
        """

        if not opportunities:
            raise OpportunityDuplicateResolutionError(
                "At least one opportunity is required."
            )

        return max(
            range(len(opportunities)),
            key=lambda index: cls.canonical_record_key(
                opportunities[index]
            ),
        )

    @classmethod
    def resolve(
        cls,
        opportunities: List[Opportunity],
    ) -> Opportunity:
        """
        Return the canonical Opportunity record.
        """

        if not opportunities:
            raise OpportunityDuplicateResolutionError(
                "At least one opportunity is required."
            )

        canonical_index = (
            cls.select_canonical_record(
                opportunities
            )
        )

        return opportunities[
            canonical_index
        ]

    @classmethod
    def resolve_group(
        cls,
        opportunities: List[Opportunity],
    ) -> OpportunityDuplicateResolutionResult:
        """
        Resolve one opportunity identity group.

        All records must share the same identity fingerprint.
        """

        if not opportunities:
            raise OpportunityDuplicateResolutionError(
                "At least one opportunity is required."
            )

        fingerprints = {
            OpportunityIdentityService.fingerprint(
                opportunity
            )
            for opportunity in opportunities
        }

        if len(fingerprints) != 1:
            raise OpportunityDuplicateResolutionError(
                "All opportunities in a resolution group must "
                "share the same fingerprint."
            )

        canonical_index = cls.select_canonical_record(
            opportunities
        )

        return OpportunityDuplicateResolutionResult.from_records(
            opportunities,
            canonical_record_index=canonical_index,
        )

    @classmethod
    def group_by_fingerprint(
        cls,
        opportunities: List[Opportunity],
    ):
        """
        Group opportunities by stable opportunity identity.
        """

        if not opportunities:
            return {}

        groups = {}

        for opportunity in opportunities:
            fingerprint = (
                OpportunityIdentityService.fingerprint(
                    opportunity
                )
            )

            groups.setdefault(
                fingerprint,
                [],
            ).append(opportunity)

        return groups

    @classmethod
    def resolve_all(
        cls,
        opportunities: List[Opportunity],
    ):
        """
        Resolve every opportunity identity group.
        """

        groups = cls.group_by_fingerprint(
            opportunities
        )

        results = []

        for fingerprint in sorted(groups):
            results.append(
                cls.resolve_group(
                    groups[fingerprint]
                )
            )

        return results

