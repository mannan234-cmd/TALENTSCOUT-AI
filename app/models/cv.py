from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field
from app.models.cv_ai_extraction import CVAIExtraction
from app.models.cv_analysis import CVAnalysis


class CV(BaseModel):
    profile_id: UUID = Field(
        ...,
        description="Student profile UUID associated with this CV"
    )

    original_file_name: str = Field(
        ...,
        min_length=1,
        description="Original uploaded CV filename"
    )

    original_file_path: Optional[str] = Field(
        default=None,
        description="Path of the original CV in Supabase Storage"
    )

    file_type: str = Field(
        ...,
        min_length=1,
        description="Uploaded CV file type or MIME type"
    )

    file_size_bytes: Optional[int] = Field(
        default=None,
        ge=0,
        description="Original CV file size in bytes"
    )

    extracted_text: Optional[str] = Field(
        default=None,
        description="Text extracted from the CV"
    )

    ai_extraction: Optional[CVAIExtraction] = Field(
        default=None,
        description="Structured AI extraction grounded in the CV text"
    )

    ai_analysis: Optional[CVAnalysis] = Field(
        default=None,
        description="Structured AI analysis grounded in the CV extraction"
    )

    extraction_status: str = Field(
        default="Not Processed",
        description="Current CV text extraction status"
    )

    analysis_status: str = Field(
        default="Not Analyzed",
        description="Current CV analysis status"
    )

    improvement_status: str = Field(
        default="Not Reviewed",
        description="Current CV improvement review status"
    )

    is_active: bool = Field(
        default=True,
        description="Whether this CV is the student's active CV"
    )
