
from typing import List, Optional

from pydantic import BaseModel, Field


class CVSection(BaseModel):
    """
    Represents one detected section of a CV.
    """

    section_type: str = Field(
        ...,
        description=(
            "Normalized section category, "
            "such as skills, experience, education, "
            "projects, or certifications."
        ),
    )

    heading: str = Field(
        ...,
        min_length=1,
        description=(
            "Original heading text detected in the CV."
        ),
    )

    content: str = Field(
        default="",
        description=(
            "Text belonging to this CV section."
        ),
    )

    start_line: Optional[int] = Field(
        default=None,
        ge=0,
        description=(
            "Zero-based line number where "
            "the section starts."
        ),
    )

    end_line: Optional[int] = Field(
        default=None,
        ge=0,
        description=(
            "Zero-based line number where "
            "the section ends."
        ),
    )


class CVStructure(BaseModel):
    """
    Represents the detected structural organization
    of a complete CV.
    """

    sections: List[CVSection] = Field(
        default_factory=list,
        description=(
            "Ordered list of sections detected "
            "in the CV."
        ),
    )

    total_sections: int = Field(
        default=0,
        ge=0,
        description=(
            "Total number of detected sections."
        ),
    )

    has_contact_information: bool = Field(
        default=False,
        description=(
            "Whether contact information "
            "was detected."
        ),
    )

    has_summary: bool = Field(
        default=False,
        description=(
            "Whether a professional summary "
            "or objective was detected."
        ),
    )

    has_skills: bool = Field(
        default=False,
        description=(
            "Whether a skills section "
            "was detected."
        ),
    )

    has_experience: bool = Field(
        default=False,
        description=(
            "Whether work experience or "
            "internship information was detected."
        ),
    )

    has_education: bool = Field(
        default=False,
        description=(
            "Whether education information "
            "was detected."
        ),
    )

    has_projects: bool = Field(
        default=False,
        description=(
            "Whether a projects section "
            "was detected."
        ),
    )

    has_certifications: bool = Field(
        default=False,
        description=(
            "Whether certifications "
            "were detected."
        ),
    )

    has_achievements: bool = Field(
        default=False,
        description=(
            "Whether achievements "
            "were detected."
        ),
    )


class CVStructureResult(BaseModel):
    """
    Final result returned by the CV structure detector.
    """

    success: bool = Field(
        default=True,
        description=(
            "Whether structure detection "
            "completed successfully."
        ),
    )

    structure: CVStructure = Field(
        default_factory=CVStructure,
        description=(
            "Detected CV structure."
        ),
    )

    warnings: List[str] = Field(
        default_factory=list,
        description=(
            "Non-fatal warnings generated "
            "during structure detection."
        ),
    )
