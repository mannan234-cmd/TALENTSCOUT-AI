
from urllib.parse import urlparse

from app.models.opportunity import (
    Opportunity,
    OpportunityVerificationStatus,
)
from app.services.opportunity_deadline_service import (
    OpportunityDeadlineService,
)
from app.services.opportunity_verification_service import (
    OpportunityVerificationService,
)


class OpportunityQualityControlError(ValueError):
    """Raised when opportunity quality control cannot be performed."""


class OpportunityQualityIssue:
    """
    Production representation of one opportunity quality issue.
    """

    def __init__(
        self,
        *,
        field: str,
        code: str,
        message: str,
    ):
        if not field or not field.strip():
            raise OpportunityQualityControlError(
                "Quality issue field cannot be empty."
            )

        if not code or not code.strip():
            raise OpportunityQualityControlError(
                "Quality issue code cannot be empty."
            )

        if not message or not message.strip():
            raise OpportunityQualityControlError(
                "Quality issue message cannot be empty."
            )

        self.field = field
        self.code = code
        self.message = message

    def to_dict(self):
        return {
            "field": self.field,
            "code": self.code,
            "message": self.message,
        }


class OpportunityQualityControlResult:
    """
    Production QC result.

    This model intentionally contains only data-quality information.
    It does not contain student scores, matching, ranking, or
    recommendation fields.
    """

    def __init__(
        self,
        *,
        opportunity_id=None,
        is_valid: bool,
        issues=None,
    ):
        self.opportunity_id = opportunity_id
        self.is_valid = bool(is_valid)
        self.issues = list(issues or [])

    @property
    def issue_count(self):
        return len(self.issues)

    def to_dict(self):
        return {
            "opportunity_id": self.opportunity_id,
            "is_valid": self.is_valid,
            "issues": [
                issue.to_dict()
                for issue in self.issues
            ],
            "issue_count": self.issue_count,
        }


class OpportunityQualityControlService:
    """
    Production opportunity quality-control service.

    Scope:
    - identity completeness
    - provenance completeness
    - URL integrity
    - verification consistency
    - deadline structural safety

    Out of scope:
    - student matching
    - ranking
    - recommendations
    - student scoring
    """

    @staticmethod
    def _is_valid_url(value):
        if value is None:
            return False

        try:
            parsed = urlparse(str(value))
            return (
                parsed.scheme in {"http", "https"}
                and bool(parsed.netloc)
            )
        except Exception:
            return False

    @classmethod
    def _issue(cls, field, code, message):
        return OpportunityQualityIssue(
            field=field,
            code=code,
            message=message,
        )

    @classmethod
    def check(cls, opportunity):
        if not isinstance(opportunity, Opportunity):
            raise OpportunityQualityControlError(
                "Expected an Opportunity instance."
            )

        issues = []

        # ----------------------------------------------------------
        # Identity
        # ----------------------------------------------------------

        if not str(opportunity.title or "").strip():
            issues.append(
                cls._issue(
                    "title",
                    "MISSING_TITLE",
                    "Opportunity title is missing.",
                )
            )

        if not str(opportunity.organization or "").strip():
            issues.append(
                cls._issue(
                    "organization",
                    "MISSING_ORGANIZATION",
                    "Opportunity organization is missing.",
                )
            )

        # ----------------------------------------------------------
        # Provenance
        # ----------------------------------------------------------

        if not str(opportunity.source_name or "").strip():
            issues.append(
                cls._issue(
                    "source_name",
                    "MISSING_SOURCE_NAME",
                    "Opportunity source name is missing.",
                )
            )

        if not cls._is_valid_url(opportunity.source_url):
            issues.append(
                cls._issue(
                    "source_url",
                    "INVALID_SOURCE_URL",
                    "Opportunity source URL is missing or invalid.",
                )
            )

        # ----------------------------------------------------------
        # Application URL
        #
        # Opportunity model already validates malformed URLs.
        # This remains a defensive QC check for completeness.
        # ----------------------------------------------------------

        if (
            opportunity.application_url is not None
            and not cls._is_valid_url(
                opportunity.application_url
            )
        ):
            issues.append(
                cls._issue(
                    "application_url",
                    "INVALID_APPLICATION_URL",
                    "Opportunity application URL is invalid.",
                )
            )

        # ----------------------------------------------------------
        # Verification consistency
        # ----------------------------------------------------------

        if (
            opportunity.verification_status
            == OpportunityVerificationStatus.VERIFIED
            and opportunity.verified_at is None
        ):
            issues.append(
                cls._issue(
                    "verified_at",
                    "MISSING_VERIFICATION_TIMESTAMP",
                    "Verified opportunity must have "
                    "a verification timestamp.",
                )
            )

        if (
            opportunity.verification_status
            != OpportunityVerificationStatus.VERIFIED
            and opportunity.verified_at is not None
        ):
            issues.append(
                cls._issue(
                    "verified_at",
                    "UNEXPECTED_VERIFICATION_TIMESTAMP",
                    "Non-verified opportunity must not have "
                    "a verification timestamp.",
                )
            )

        # ----------------------------------------------------------
        # Deadline / verification timestamp structural safety
        # ----------------------------------------------------------

        if opportunity.verified_at is not None:
            if (
                opportunity.verified_at.tzinfo is None
                or opportunity.verified_at.utcoffset() is None
            ):
                issues.append(
                    cls._issue(
                        "verified_at",
                        "NAIVE_VERIFICATION_TIMESTAMP",
                        "Verification timestamp must be timezone-aware.",
                    )
                )

        if opportunity.deadline is not None:
            if (
                opportunity.deadline.tzinfo is None
                or opportunity.deadline.utcoffset() is None
            ):
                issues.append(
                    cls._issue(
                        "deadline",
                        "NAIVE_DEADLINE",
                        "Deadline must be timezone-aware.",
                    )
                )

        return OpportunityQualityControlResult(
            opportunity_id=str(opportunity.id)
            if opportunity.id is not None
            else None,
            is_valid=len(issues) == 0,
            issues=issues,
        )

    @classmethod
    def validate(cls, opportunity):
        """
        Alias for callers that prefer validation terminology.
        """
        return cls.check(opportunity)
