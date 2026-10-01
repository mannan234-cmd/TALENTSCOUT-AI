from typing import Any, Dict, List
from pydantic import BaseModel, ConfigDict, Field


class CVImprovedSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    section: str
    content: Any = None


class CVImprovedResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success: bool = True
    professional_summary: str = ""
    experience: List[Dict[str, Any]] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    education: List[Dict[str, Any]] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
