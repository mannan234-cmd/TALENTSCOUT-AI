
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.cv_workflow import CVWorkflowResult


class CVWorkflowRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cv_id: UUID
    source_text: str = Field(..., min_length=1)
    job_description: Optional[Union[str, Dict[str, Any]]] = None


class CVWorkflowResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success: bool
    cv_id: UUID

    extraction_completed: bool
    analysis_completed: bool
    matching_completed: bool
    recommendations_completed: bool

    warnings: List[str] = Field(default_factory=list)

    extraction: Optional[Dict[str, Any]] = None
    analysis: Optional[Dict[str, Any]] = None
    matching: Optional[Dict[str, Any]] = None
    recommendations: Optional[Dict[str, Any]] = None

    @classmethod
    def from_workflow_result(
        cls,
        result: CVWorkflowResult,
        cv_data: Optional[Dict[str, Any]] = None,
    ) -> "CVWorkflowResponse":

        cv_data = cv_data or {}

        return cls(
            success=result.success,
            cv_id=result.cv_id,
            extraction_completed=result.extraction_completed,
            analysis_completed=result.analysis_completed,
            matching_completed=result.matching_completed,
            recommendations_completed=result.recommendations_completed,
            warnings=result.warnings,
            extraction=cv_data.get("ai_extraction"),
            analysis=cv_data.get("ai_analysis"),
            matching=cv_data.get("ai_matching"),
            recommendations=cv_data.get("ai_recommendations"),
        )
