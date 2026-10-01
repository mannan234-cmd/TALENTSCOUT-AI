from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.models.opportunity import (
    Opportunity,
    OpportunitySourceType,
)
from app.models.opportunity_source import OpportunitySource


class CollectedOpportunity(BaseModel):
    """
    Raw-but-structured opportunity returned by a collector.

    It is intentionally separate from Opportunity so collection does
    not bypass the validation/normalization pipeline.
    """

    model_config = ConfigDict(extra="forbid")

    title: str
    organization: str
    description: str = ""
    location: Optional[str] = None
    remote: Optional[bool] = None

    opportunity_type: str = "other"

    eligibility: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)

    application_url: Optional[HttpUrl] = None
    source_url: Optional[HttpUrl] = None

    source_name: Optional[str] = None
    source_type: OpportunitySourceType = OpportunitySourceType.OTHER

    deadline: Optional[datetime] = None

    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    collected_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def source_identifier(self) -> str:
        if self.source_url:
            return str(self.source_url)

        if self.source_name:
            return self.source_name

        return "unknown"


class CollectionResult(BaseModel):
    """
    Standard result returned by every collector.
    """

    model_config = ConfigDict(extra="forbid")

    source_id: str
    source_name: str

    started_at: datetime
    completed_at: datetime

    opportunities: List[CollectedOpportunity] = Field(
        default_factory=list
    )

    errors: List[str] = Field(default_factory=list)

    pages_processed: int = Field(default=0, ge=0)
    items_seen: int = Field(default=0, ge=0)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0

    @property
    def collected_count(self) -> int:
        return len(self.opportunities)


class OpportunityCollector(ABC):
    """
    Abstract collector contract.

    Concrete collectors must implement:
      - collector_name
      - supports()
      - collect()
    """

    @property
    @abstractmethod
    def collector_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def supports(self, source: OpportunitySource) -> bool:
        raise NotImplementedError

    @abstractmethod
    def collect(
        self,
        source: OpportunitySource,
    ) -> CollectionResult:
        raise NotImplementedError


class BaseOpportunityCollector(OpportunityCollector):
    """
    Shared collector helper for concrete implementations.
    """

    @property
    def collector_name(self) -> str:
        return self.__class__.__name__

    def build_result(
        self,
        source: OpportunitySource,
        *,
        started_at: datetime,
        opportunities: Optional[List[CollectedOpportunity]] = None,
        errors: Optional[List[str]] = None,
        pages_processed: int = 0,
        items_seen: int = 0,
    ) -> CollectionResult:
        completed_at = datetime.now(timezone.utc)

        return CollectionResult(
            source_id=source.id or "",
            source_name=source.name,
            started_at=started_at,
            completed_at=completed_at,
            opportunities=opportunities or [],
            errors=errors or [],
            pages_processed=pages_processed,
            items_seen=items_seen,
        )
