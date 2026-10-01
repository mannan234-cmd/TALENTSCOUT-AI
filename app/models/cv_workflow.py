from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CVWorkflowResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success: bool = True
    cv_id: UUID
    extraction_completed: bool = False
    analysis_completed: bool = False
    matching_completed: bool = False
    recommendations_completed: bool = False
    warnings: List[str] = Field(default_factory=list)
