
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CVExtractedSkill(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1)
    category: Optional[str] = None
    evidence: Optional[str] = None


class CVExtractedEducation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    grade: Optional[str] = None
    evidence: Optional[str] = None


class CVExtractedExperience(BaseModel):
    model_config = ConfigDict(extra="forbid")

    employer: Optional[str] = None
    job_title: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    evidence: Optional[str] = None


class CVExtractedProject(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
    role: Optional[str] = None
    evidence: Optional[str] = None


class CVExtractedCertification(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1)
    issuing_organization: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_id: Optional[str] = None
    evidence: Optional[str] = None


class CVExtractedAchievement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    date: Optional[str] = None
    evidence: Optional[str] = None


class CVExtractedLanguage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1)
    proficiency: Optional[str] = None
    evidence: Optional[str] = None


class CVAIExtraction(BaseModel):
    """
    Structured information extracted from a CV.

    Values must be grounded in the supplied CV text.
    Missing information should remain None or an empty list.
    """

    model_config = ConfigDict(extra="forbid")

    full_name: Optional[str] = None
    professional_title: Optional[str] = None
    professional_summary: Optional[str] = None

    skills: List[CVExtractedSkill] = Field(default_factory=list)
    education: List[CVExtractedEducation] = Field(default_factory=list)
    experience: List[CVExtractedExperience] = Field(default_factory=list)
    projects: List[CVExtractedProject] = Field(default_factory=list)
    certifications: List[CVExtractedCertification] = Field(default_factory=list)
    achievements: List[CVExtractedAchievement] = Field(default_factory=list)
    languages: List[CVExtractedLanguage] = Field(default_factory=list)

    interests: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class CVAIExtractionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success: bool = True
    extraction: CVAIExtraction = Field(default_factory=CVAIExtraction)
    source_text_length: int = Field(default=0, ge=0)
    warnings: List[str] = Field(default_factory=list)
