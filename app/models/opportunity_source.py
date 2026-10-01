from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from app.models.opportunity import OpportunitySourceType


class OpportunitySource(BaseModel):
    """
    Canonical source definition for opportunity collection.
    """

    model_config = ConfigDict(extra="forbid")

    id: Optional[str] = None
    name: str = Field(..., min_length=2)
    source_type: OpportunitySourceType = OpportunitySourceType.OTHER
    base_url: HttpUrl
    description: str = ""
    is_active: bool = True
    collection_enabled: bool = True
    priority: int = Field(default=100, ge=0, le=1000)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()

        if len(value) < 2:
            raise ValueError("Source name must contain at least 2 characters.")

        return value

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str) -> str:
        return value.strip()

    @field_validator("base_url")
    @classmethod
    def validate_http_url(cls, value: HttpUrl) -> HttpUrl:
        if value.scheme not in {"http", "https"}:
            raise ValueError("Source URL must use HTTP or HTTPS.")

        return value


class OpportunitySourceCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=2)
    source_type: OpportunitySourceType = OpportunitySourceType.OTHER
    base_url: HttpUrl
    description: str = ""
    is_active: bool = True
    collection_enabled: bool = True
    priority: int = Field(default=100, ge=0, le=1000)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class OpportunitySourceUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = None
    source_type: Optional[OpportunitySourceType] = None
    base_url: Optional[HttpUrl] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    collection_enabled: Optional[bool] = None
    priority: Optional[int] = Field(default=None, ge=0, le=1000)
    metadata: Optional[Dict[str, Any]] = None
