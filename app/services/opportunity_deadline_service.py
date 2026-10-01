from datetime import datetime, timezone

from pydantic import BaseModel

from app.models.opportunity import Opportunity


class OpportunityDeadlineStatus:
    """Deterministic deadline status values."""

    NO_DEADLINE = "no_deadline"
    UPCOMING = "upcoming"
    EXPIRED = "expired"


class OpportunityDeadlineInfo(BaseModel):
    deadline: datetime | None = None
    status: str
    is_expired: bool
    has_deadline: bool


class OpportunityDeadlineService:
    """Deadline normalization, classification, and structured information."""

    @staticmethod
    def normalize_deadline(deadline):
        if deadline is None:
            return None

        if not isinstance(deadline, datetime):
            raise ValueError("Deadline must be a datetime or None.")

        if deadline.tzinfo is None or deadline.utcoffset() is None:
            raise ValueError("Deadline must be timezone-aware.")

        return deadline.astimezone(timezone.utc)

    @classmethod
    def get_status(cls, deadline, *, now=None):
        normalized = cls.normalize_deadline(deadline)

        if normalized is None:
            return OpportunityDeadlineStatus.NO_DEADLINE

        if now is None:
            now = datetime.now(timezone.utc)
        else:
            now = cls.normalize_deadline(now)

        if normalized < now:
            return OpportunityDeadlineStatus.EXPIRED

        return OpportunityDeadlineStatus.UPCOMING

    @classmethod
    def get_opportunity_status(cls, opportunity, *, now=None):
        if not isinstance(opportunity, Opportunity):
            raise ValueError("Expected an Opportunity instance.")

        return cls.get_status(opportunity.deadline, now=now)

    @classmethod
    def get_deadline_info(cls, deadline, *, now=None):
        normalized = cls.normalize_deadline(deadline)
        status = cls.get_status(normalized, now=now)

        return OpportunityDeadlineInfo(
            deadline=normalized,
            status=status,
            is_expired=(status == OpportunityDeadlineStatus.EXPIRED),
            has_deadline=(normalized is not None),
        )
