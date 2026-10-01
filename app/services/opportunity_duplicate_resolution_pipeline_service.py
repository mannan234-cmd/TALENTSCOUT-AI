from typing import Dict, List, Tuple

from app.models.opportunity import Opportunity
from app.models.opportunity_duplicate_resolution import (
    OpportunityDuplicateResolutionResult,
)
from app.services.opportunity_duplicate_resolution_service import (
    OpportunityDuplicateResolutionService,
)


class OpportunityDuplicateResolutionPipelineError(ValueError):
    """Raised when duplicate-resolution pipeline input is invalid."""


class OpportunityDuplicateResolutionPipelineService:
    """
    Pipeline boundary for deterministic opportunity duplicate resolution.

    This service:
    1. validates the input collection,
    2. groups opportunities by stable fingerprint,
    3. selects one canonical record per identity group,
    4. returns canonical opportunities plus provenance results.

    It does not perform student matching, ranking, recommendation,
    or persistence.
    """

    @classmethod
    def resolve(
        cls,
        opportunities: List[Opportunity],
    ) -> Tuple[
        List[Opportunity],
        List[OpportunityDuplicateResolutionResult],
    ]:
        if opportunities is None:
            raise OpportunityDuplicateResolutionPipelineError(
                "Opportunities cannot be None."
            )

        if not isinstance(opportunities, list):
            raise OpportunityDuplicateResolutionPipelineError(
                "Opportunities must be a list."
            )

        if any(
            not isinstance(opportunity, Opportunity)
            for opportunity in opportunities
        ):
            raise OpportunityDuplicateResolutionPipelineError(
                "All items must be Opportunity instances."
            )

        if not opportunities:
            return [], []

        results = (
            OpportunityDuplicateResolutionService.resolve_all(
                opportunities
            )
        )

        groups = (
            OpportunityDuplicateResolutionService
            .group_by_fingerprint(opportunities)
        )

        canonical_opportunities = []

        for result in results:
            group = groups[result.fingerprint]

            canonical_index = result.canonical_record_index

            canonical_opportunities.append(
                group[canonical_index]
            )

        return canonical_opportunities, results
