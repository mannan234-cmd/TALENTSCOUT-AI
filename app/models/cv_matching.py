from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CVJobMatchItem(BaseModel):
    """
    Evidence-backed match observation between a CV and a job.
    """

    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    evidence: Optional[str] = None


class CVJobSkillMatch(BaseModel):
    """
    Evidence-backed assessment of one job-required skill.
    """

    model_config = ConfigDict(extra="forbid")

    skill: str = Field(..., min_length=1)
    match_status: str = Field(..., min_length=1)
    cv_evidence: Optional[str] = None
    job_evidence: Optional[str] = None
    explanation: str = Field(..., min_length=1)


class CVJobExperienceMatch(BaseModel):
    """
    Evidence-backed comparison of CV experience against
    job experience requirements.
    """

    model_config = ConfigDict(extra="forbid")

    requirement: str = Field(..., min_length=1)
    match_status: str = Field(..., min_length=1)
    cv_evidence: Optional[str] = None
    job_evidence: Optional[str] = None
    explanation: str = Field(..., min_length=1)


class CVJobEducationMatch(BaseModel):
    """
    Evidence-backed comparison of CV education against
    job education requirements.
    """

    model_config = ConfigDict(extra="forbid")

    requirement: str = Field(..., min_length=1)
    match_status: str = Field(..., min_length=1)
    cv_evidence: Optional[str] = None
    job_evidence: Optional[str] = None
    explanation: str = Field(..., min_length=1)


class CVJobGap(BaseModel):
    """
    Evidence-backed gap between the CV and job requirements.
    """

    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    cv_evidence: Optional[str] = None
    job_evidence: Optional[str] = None


class CVJobMatching(BaseModel):
    """
    Complete structured CV-to-job matching result.
    """

    model_config = ConfigDict(extra="forbid")

    overall_summary: str = Field(..., min_length=1)

    strengths: List[CVJobMatchItem] = Field(
        default_factory=list
    )

    weaknesses: List[CVJobMatchItem] = Field(
        default_factory=list
    )

    skills_match: List[CVJobSkillMatch] = Field(
        default_factory=list
    )

    experience_match: List[CVJobExperienceMatch] = Field(
        default_factory=list
    )

    education_match: List[CVJobEducationMatch] = Field(
        default_factory=list
    )

    gaps: List[CVJobGap] = Field(
        default_factory=list
    )

    warnings: List[str] = Field(
        default_factory=list
    )


class CVJobMatchingResult(BaseModel):
    """
    Result wrapper for CV-to-job matching.
    """

    model_config = ConfigDict(extra="forbid")

    success: bool = True

    matching: CVJobMatching = Field(
        default_factory=lambda: CVJobMatching(
            overall_summary="No matching result available.",
        )
    )

    warnings: List[str] = Field(
        default_factory=list
    )