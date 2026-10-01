from typing import Any, List
from pydantic import BaseModel, Field


class CVProfileDifference(BaseModel):
    field: str
    profile_value: Any = None
    cv_value: Any = None
    change_type: str
    selected: bool = False


class CVProfileComparisonResult(BaseModel):
    has_differences: bool = False
    differences: List[CVProfileDifference] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
