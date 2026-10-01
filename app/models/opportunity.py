from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class OpportunityType(str, Enum):
    JOB = "job"
    INTERNSHIP = "internship"
    SCHOLARSHIP = "scholarship"
    FELLOWSHIP = "fellowship"
    COMPETITION = "competition"
    HACKATHON = "hackathon"
    GRANT = "grant"
    APPRENTICESHIP = "apprenticeship"
    TRAINING = "training"
    OTHER = "other"


class OpportunityVerificationStatus(str, Enum):
    VERIFIED = "verified"
    NEEDS_VERIFICATION = "needs_verification"
    EXPIRED = "expired"


class OpportunitySourceType(str, Enum):
    OFFICIAL = "official"
    UNIVERSITY = "university"
    GOVERNMENT = "government"
    COMPANY = "company"
    NONPROFIT = "nonprofit"
    AGGREGATOR = "aggregator"
    OTHER = "other"


class Opportunity(BaseModel):
    """
    Canonical opportunity representation.

    This model intentionally separates:
    - opportunity facts
    - source information
    - verification state
    - deadline information
    - searchable metadata
    """

    model_config = ConfigDict(extra="forbid")

    id: Optional[str] = None

    title: str = Field(..., min_length=3, max_length=500)
    organization: str = Field(..., min_length=2, max_length=300)

    opportunity_type: OpportunityType = OpportunityType.OTHER

    description: str = Field(default="", max_length=20000)

    location: Optional[str] = Field(default=None, max_length=500)
    remote: Optional[bool] = None

    eligibility: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)

    benefits: List[str] = Field(default_factory=list)

    application_url: Optional[HttpUrl] = None
    source_url: Optional[HttpUrl] = None

    source_name: Optional[str] = Field(default=None, max_length=300)
    source_type: OpportunitySourceType = OpportunitySourceType.OTHER

    deadline: Optional[datetime] = None

    verification_status: OpportunityVerificationStatus = (
        OpportunityVerificationStatus.NEEDS_VERIFICATION
    )

    verified_at: Optional[datetime] = None

    fingerprint: Optional[str] = Field(
        default=None,
        min_length=8,
        max_length=128,
    )

    tags: List[str] = Field(default_factory=list)

    metadata: Dict[str, Any] = Field(default_factory=dict)

    collected_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator(
        "eligibility",
        "requirements",
        "skills",
        "benefits",
        "tags",
        mode="before",
    )
    @classmethod
    def normalize_string_lists(cls, value):
        if value is None:
            return []

        if isinstance(value, str):
            value = [value]

        if not isinstance(value, list):
            raise TypeError("Expected a list of strings.")

        cleaned = []
        seen = set()

        for item in value:
            if item is None:
                continue

            text = str(item).strip()

            if not text:
                continue

            key = text.casefold()

            if key in seen:
                continue

            seen.add(key)
            cleaned.append(text)

        return cleaned

    @field_validator("title", "organization", mode="before")
    @classmethod
    def normalize_required_text(cls, value):
        if value is None:
            raise ValueError("This field is required.")

        value = str(value).strip()

        if not value:
            raise ValueError("This field cannot be empty.")

        return value

    @field_validator("deadline")
    @classmethod
    def validate_deadline(cls, value):
        if value is not None and value.tzinfo is None:
            raise ValueError("deadline must be timezone-aware.")

        return value

    @field_validator("verified_at")
    @classmethod
    def validate_verified_at(cls, value):
        if value is not None and value.tzinfo is None:
            raise ValueError("verified_at must be timezone-aware.")

        return value


class OpportunityCreate(Opportunity):
    """
    Input model for creating a new opportunity.
    """

    id: Optional[str] = None


class OpportunityUpdate(BaseModel):
    """
    Partial update model.
    """

    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = Field(default=None, min_length=3, max_length=500)
    organization: Optional[str] = Field(default=None, min_length=2, max_length=300)

    opportunity_type: Optional[OpportunityType] = None

    description: Optional[str] = Field(default=None, max_length=20000)

    location: Optional[str] = Field(default=None, max_length=500)
    remote: Optional[bool] = None

    eligibility: Optional[List[str]] = None
    requirements: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    benefits: Optional[List[str]] = None

    application_url: Optional[HttpUrl] = None
    source_url: Optional[HttpUrl] = None

    source_name: Optional[str] = Field(default=None, max_length=300)
    source_type: Optional[OpportunitySourceType] = None

    deadline: Optional[datetime] = None

    verification_status: Optional[OpportunityVerificationStatus] = None

    verified_at: Optional[datetime] = None

    fingerprint: Optional[str] = Field(
        default=None,
        min_length=8,
        max_length=128,
    )

    tags: Optional[List[str]] = None

    metadata: Optional[Dict[str, Any]] = None

    @field_validator(
        "deadline",
        "verified_at",
    )
    @classmethod
    def validate_datetime_fields(cls, value):
        if value is not None and value.tzinfo is None:
            raise ValueError("Datetime fields must be timezone-aware.")

        return value


class OpportunitySearchFilters(BaseModel):
    """
    Search/filter contract used later by the opportunity service and UI.
    """

    model_config = ConfigDict(extra="forbid")

    query: Optional[str] = None

    opportunity_types: List[OpportunityType] = Field(
        default_factory=list
    )

    verification_statuses: List[OpportunityVerificationStatus] = Field(
        default_factory=list
    )

    location: Optional[str] = None
    remote: Optional[bool] = None

    skills: List[str] = Field(default_factory=list)

    deadline_from: Optional[datetime] = None
    deadline_to: Optional[datetime] = None

    organization: Optional[str] = None

    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)
