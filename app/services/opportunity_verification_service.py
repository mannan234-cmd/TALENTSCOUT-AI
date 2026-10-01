from datetime import datetime, timezone

from app.models.opportunity import (
    Opportunity,
    OpportunityVerificationStatus,
)


class OpportunityVerificationError(ValueError):
    """Raised when opportunity verification cannot be performed."""


class OpportunityVerificationService:
    """Service for source-based opportunity verification state transitions."""

    @staticmethod
    def verify(
        opportunity: Opportunity,
        *,
        verified_at: datetime | None = None,
    ) -> Opportunity:
        if not isinstance(opportunity, Opportunity):
            raise OpportunityVerificationError(
                "Expected an Opportunity instance."
            )

        if verified_at is None:
            verified_at = datetime.now(timezone.utc)

        if (
            verified_at.tzinfo is None
            or verified_at.utcoffset() is None
        ):
            raise OpportunityVerificationError(
                "verified_at must be timezone-aware."
            )

        verified_at = verified_at.astimezone(timezone.utc)

        updated = opportunity.model_copy(deep=True)

        updated.verification_status = (
            OpportunityVerificationStatus.VERIFIED
        )
        updated.verified_at = verified_at

        return updated


    @staticmethod
    def reverify(
        opportunity: Opportunity,
        *,
        verified_at: datetime | None = None,
    ) -> Opportunity:
        """
        Re-verify an existing opportunity while preserving
        source provenance and all opportunity content.
        """
        if not isinstance(opportunity, Opportunity):
            raise OpportunityVerificationError(
                "Expected an Opportunity instance."
            )

        if (
            opportunity.verification_status
            != OpportunityVerificationStatus.VERIFIED
        ):
            raise OpportunityVerificationError(
                "Only a verified opportunity can be re-verified."
            )

        if verified_at is None:
            verified_at = datetime.now(timezone.utc)

        if (
            verified_at.tzinfo is None
            or verified_at.utcoffset() is None
        ):
            raise OpportunityVerificationError(
                "verified_at must be timezone-aware."
            )

        verified_at = verified_at.astimezone(timezone.utc)

        if (
            opportunity.verified_at is not None
            and verified_at <= opportunity.verified_at
        ):
            raise OpportunityVerificationError(
                "Re-verification timestamp must be newer "
                "than the existing verification timestamp."
            )

        updated = opportunity.model_copy(deep=True)

        updated.verification_status = (
            OpportunityVerificationStatus.VERIFIED
        )
        updated.verified_at = verified_at

        return updated

    @staticmethod
    def mark_needs_verification(
        opportunity: Opportunity,
    ) -> Opportunity:
        if not isinstance(opportunity, Opportunity):
            raise OpportunityVerificationError(
                "Expected an Opportunity instance."
            )

        updated = opportunity.model_copy(deep=True)

        updated.verification_status = (
            OpportunityVerificationStatus.NEEDS_VERIFICATION
        )
        updated.verified_at = None

        return updated

    @staticmethod
    def mark_expired(
        opportunity: Opportunity,
    ) -> Opportunity:
        if not isinstance(opportunity, Opportunity):
            raise OpportunityVerificationError(
                "Expected an Opportunity instance."
            )

        updated = opportunity.model_copy(deep=True)

        updated.verification_status = (
            OpportunityVerificationStatus.EXPIRED
        )
        updated.verified_at = None

        return updated
