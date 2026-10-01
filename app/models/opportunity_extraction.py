
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class AIOpportunityExtraction(BaseModel):
    """
    Strict AI-extracted opportunity fields.

    These fields must be derived only from supplied source content.
    Missing information remains None/empty rather than being invented.
    """

    model_config = ConfigDict(extra="forbid")

    title: str = Field(default="")
    organization: str = Field(default="")
    description: str = Field(default="")

    location: Optional[str] = None
    remote: Optional[bool] = None

    opportunity_type: str = Field(default="other")

    eligibility: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)

    application_url: Optional[str] = None
    deadline: Optional[str] = None

    tags: List[str] = Field(default_factory=list)

    extraction_notes: List[str] = Field(default_factory=list)


class AIOpportunityExtractionRequest(BaseModel):
    """
    Input contract for AI extraction.

    raw_text must contain the source-provided opportunity content.
    """

    model_config = ConfigDict(extra="forbid")

    raw_text: str = Field(..., min_length=1)

    source_name: Optional[str] = None
    source_url: Optional[str] = None


class AIOpportunityExtractionResult(BaseModel):
    """
    Extraction result with provenance.

    raw_source_text is retained so the extracted result can always
    be traced back to the source content supplied to the model.
    """

    model_config = ConfigDict(extra="forbid")

    extraction: AIOpportunityExtraction
    raw_source_text: str = Field(..., min_length=1)

    source_name: Optional[str] = None
    source_url: Optional[str] = None

    model_name: Optional[str] = None
    extraction_version: str = "1.0"
