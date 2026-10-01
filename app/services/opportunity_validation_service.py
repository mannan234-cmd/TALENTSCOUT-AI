from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from pydantic import ValidationError

from app.models.opportunity import (
    Opportunity,
    OpportunityCreate,
    OpportunityUpdate,
)


class OpportunityValidationError(ValueError):
    """Raised when an opportunity fails business validation."""


class OpportunityValidationService:
    """
    Business-level validation for opportunity records.

    Pydantic handles structural/type validation.
    This service handles additional application-level rules.
    """

    URL_FIELDS = (
        "application_url",
        "source_url",
    )

    LIST_FIELDS = (
        "eligibility",
        "requirements",
        "skills",
        "benefits",
        "tags",
    )

    REQUIRED_CREATE_FIELDS = (
        "title",
        "organization",
        "description",
        "opportunity_type",
        "source_type",
        "verification_status",
    )

    @staticmethod
    def _validate_url(value: str | None, field_name: str) -> None:
        if value is None or value == "":
            return

        # Pydantic v2 may provide HttpUrl/AnyUrl objects here.
        # Convert them to their string representation before urlparse().
        value = str(value)

        parsed = urlparse(value)

        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise OpportunityValidationError(
                f"{field_name} must be a valid HTTP/HTTPS URL."
            )

    @staticmethod
    def _validate_deadline(deadline: datetime | None) -> None:
        if deadline is None:
            return

        if deadline.tzinfo is None or deadline.utcoffset() is None:
            raise OpportunityValidationError(
                "deadline must be timezone-aware."
            )

    @staticmethod
    def _validate_verified_at(
        verified_at: datetime | None,
        verification_status: str,
    ) -> None:
        if verified_at is not None:
            if verified_at.tzinfo is None or verified_at.utcoffset() is None:
                raise OpportunityValidationError(
                    "verified_at must be timezone-aware."
                )

        if verification_status == "verified" and verified_at is None:
            raise OpportunityValidationError(
                "verified_at is required when verification_status is 'verified'."
            )

        if verification_status != "verified" and verified_at is not None:
            raise OpportunityValidationError(
                "verified_at must be empty unless verification_status is 'verified'."
            )

    @staticmethod
    def _validate_text(value: Any, field_name: str, minimum: int) -> None:
        if not isinstance(value, str):
            raise OpportunityValidationError(
                f"{field_name} must be a string."
            )

        if len(value.strip()) < minimum:
            raise OpportunityValidationError(
                f"{field_name} must contain at least {minimum} characters."
            )

    @classmethod
    def _validate_urls(cls, opportunity: Opportunity) -> None:
        for field_name in cls.URL_FIELDS:
            cls._validate_url(
                getattr(opportunity, field_name),
                field_name,
            )

    @classmethod
    def validate(cls, opportunity: Opportunity) -> Opportunity:
        """
        Validate an already constructed Opportunity.

        Returns the validated model unchanged.
        """
        cls._validate_text(opportunity.title, "title", 3)
        cls._validate_text(opportunity.organization, "organization", 2)

        cls._validate_urls(opportunity)
        cls._validate_deadline(opportunity.deadline)
        cls._validate_verified_at(
            opportunity.verified_at,
            opportunity.verification_status.value
            if hasattr(opportunity.verification_status, "value")
            else opportunity.verification_status,
        )

        return opportunity

    @classmethod
    def validate_create(
        cls,
        payload: dict[str, Any] | OpportunityCreate,
    ) -> OpportunityCreate:
        """
        Validate and normalize an opportunity creation payload.
        """
        try:
            if isinstance(payload, OpportunityCreate):
                model = payload
            else:
                model = OpportunityCreate.model_validate(payload)
        except ValidationError as exc:
            raise OpportunityValidationError(
                f"Invalid opportunity payload: {exc}"
            ) from exc

        verification_status = (
            model.verification_status.value
            if hasattr(model.verification_status, "value")
            else model.verification_status
        )

        cls._validate_urls_from_model(model)
        cls._validate_deadline(model.deadline)
        cls._validate_verified_at(
            model.verified_at,
            verification_status,
        )

        return model

    @classmethod
    def validate_update(
        cls,
        payload: dict[str, Any] | OpportunityUpdate,
    ) -> OpportunityUpdate:
        """
        Validate a partial opportunity update.
        """
        try:
            if isinstance(payload, OpportunityUpdate):
                model = payload
            else:
                model = OpportunityUpdate.model_validate(payload)
        except ValidationError as exc:
            raise OpportunityValidationError(
                f"Invalid opportunity update: {exc}"
            ) from exc

        if model.application_url is not None:
            cls._validate_url(model.application_url, "application_url")

        if model.source_url is not None:
            cls._validate_url(model.source_url, "source_url")

        if model.deadline is not None:
            cls._validate_deadline(model.deadline)

        verification_status = (
            model.verification_status.value
            if hasattr(model.verification_status, "value")
            else model.verification_status
        )

        if model.verified_at is not None:
            if (
                model.verified_at.tzinfo is None
                or model.verified_at.utcoffset() is None
            ):
                raise OpportunityValidationError(
                    "verified_at must be timezone-aware."
                )

        if verification_status == "verified" and model.verified_at is None:
            raise OpportunityValidationError(
                "verified_at is required when changing verification_status to 'verified'."
            )

        return model

    @staticmethod
    def _validate_urls_from_model(model: Any) -> None:
        for field_name in (
            "application_url",
            "source_url",
        ):
            OpportunityValidationService._validate_url(
                getattr(model, field_name, None),
                field_name,
            )

    @classmethod
    def is_valid(
        cls,
        opportunity: Opportunity,
    ) -> bool:
        try:
            cls.validate(opportunity)
            return True
        except (OpportunityValidationError, ValidationError, ValueError):
            return False
