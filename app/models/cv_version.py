from datetime import datetime
from typing import Any, Dict, List
from pydantic import BaseModel, ConfigDict, Field


class CVVersion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str | None = None
    cv_id: str
    version_number: int = Field(..., ge=1)
    label: str = ""
    professional_cv: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None


class CVVersionHistory(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cv_id: str
    versions: List[CVVersion] = Field(default_factory=list)
