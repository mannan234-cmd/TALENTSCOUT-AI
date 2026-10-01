
from typing import List

from pydantic import BaseModel, Field

from app.services.cv_contact_detector import (
    CVContactInfo,
)

from app.models.cv_structure import (
    CVStructure,
)


class CVIntegratedContactResult(BaseModel):
    """
    Combined deterministic CV structure + contact information result.

    Contact information is extracted from the CV header/contact area
    using the deterministic CVContactDetector.
    """

    success: bool = True

    structure: CVStructure = Field(
        default_factory=CVStructure
    )

    contact_information: CVContactInfo = Field(
        default_factory=CVContactInfo
    )

    detected_lines: List[str] = Field(
        default_factory=list
    )

    warnings: List[str] = Field(
        default_factory=list
    )
