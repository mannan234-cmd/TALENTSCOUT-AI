
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class StudentProfile(BaseModel):
    """
    Master student profile for TalentScout AI.

    This model represents the core information about a student
    that will later be used by:
    - CV analysis
    - Opportunity matching
    - Skill gap analysis
    - Career guidance
    - Application assistance
    - Interview preparation
    """

    full_name: str = Field(
        ...,
        min_length=2,
        description="Student's full name"
    )

    email: Optional[EmailStr] = Field(
        default=None,
        description="Student's email address"
    )

    phone: Optional[str] = Field(
        default=None,
        description="Student's phone number"
    )

    location: Optional[str] = Field(
        default=None,
        description="Student's current location"
    )

    bio: Optional[str] = Field(
        default=None,
        description="Short student biography"
    )

    career_summary: Optional[str] = Field(
        default=None,
        description="Professional or career summary"
    )

    interests: List[str] = Field(
        default_factory=list,
        description="Student's career or professional interests"
    )

    certifications: List[str] = Field(
        default_factory=list,
        description="Student's certifications"
    )

    achievements: List[str] = Field(
        default_factory=list,
        description="Student's achievements"
    )

    career_level: Optional[str] = Field(
        default=None,
        description="Student's current career level"
    )

    years_of_experience: float = Field(
        default=0,
        ge=0,
        description="Total years of professional experience"
    )
