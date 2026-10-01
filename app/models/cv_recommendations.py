from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CVRecommendationItem(BaseModel):
    """
    A single grounded recommendation.

    Recommendations must be actionable and based only on
    supplied CV analysis or CV-job matching evidence.
    """

    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    action: str = Field(..., min_length=1)
    evidence: Optional[str] = None
    priority: Optional[str] = None


class CVRecommendations(BaseModel):
    """
    Structured recommendations derived from CV analysis
    and/or CV-job matching results.
    """

    model_config = ConfigDict(extra="forbid")

    cv_improvements: List[CVRecommendationItem] = Field(
        default_factory=list
    )
    skill_recommendations: List[CVRecommendationItem] = Field(
        default_factory=list
    )
    experience_recommendations: List[CVRecommendationItem] = Field(
        default_factory=list
    )
    job_match_recommendations: List[CVRecommendationItem] = Field(
        default_factory=list
    )
    profile_recommendations: List[CVRecommendationItem] = Field(
        default_factory=list
    )
    warnings: List[str] = Field(default_factory=list)


class CVRecommendationsResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success: bool = True
    recommendations: CVRecommendations = Field(
        default_factory=CVRecommendations
    )
    warnings: List[str] = Field(default_factory=list)
