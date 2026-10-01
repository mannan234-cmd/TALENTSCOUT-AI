from typing import Any, Dict, List
from pydantic import BaseModel, ConfigDict, Field


class ProfessionalCV(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str = ""
    contact_line: str = ""
    professional_summary: str = ""
    experience: List[Dict[str, Any]] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    education: List[Dict[str, Any]] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
