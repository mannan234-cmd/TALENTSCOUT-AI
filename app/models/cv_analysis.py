from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CVAnalysisItem(BaseModel):
    """
    A grounded observation about the CV.

    Each item should be supported by information already present
    in the structured CV extraction.
    """

    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    evidence: Optional[str] = None


class CVAnalysisSkillAssessment(BaseModel):
    """
    Analysis of a skill already identified in the CV.
    """

    model_config = ConfigDict(extra="forbid")

    skill: str = Field(..., min_length=1)
    assessment: str = Field(..., min_length=1)
    evidence: Optional[str] = None


class CVAnalysis(BaseModel):
    """
    Structured, grounded analysis of an extracted CV.

    This model describes observations and improvement opportunities.
    It does not create new candidate facts.
    """

    model_config = ConfigDict(extra="forbid")

    strengths: List[CVAnalysisItem] = Field(
        default_factory=list
    )

    weaknesses: List[CVAnalysisItem] = Field(
        default_factory=list
    )

    skills_assessment: List[CVAnalysisSkillAssessment] = Field(
        default_factory=list
    )

    experience_analysis: List[CVAnalysisItem] = Field(
        default_factory=list
    )

    education_analysis: List[CVAnalysisItem] = Field(
        default_factory=list
    )

    certifications_analysis: List[CVAnalysisItem] = Field(
        default_factory=list
    )

    improvement_suggestions: List[CVAnalysisItem] = Field(
        default_factory=list
    )

    warnings: List[str] = Field(
        default_factory=list
    )


class CVAnalysisResult(BaseModel):
    """
    Result wrapper for CV analysis.
    """

    model_config = ConfigDict(extra="forbid")

    success: bool = True

    analysis: CVAnalysis = Field(
        default_factory=CVAnalysis
    )

    warnings: List[str] = Field(
        default_factory=list
    )
