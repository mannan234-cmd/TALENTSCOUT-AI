from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CertificateVerification(BaseModel):
    """
    Structured evidence-based certificate verification result.

    This model records whether available evidence matches,
    conflicts, or is unavailable.

    AI extraction alone does not establish certificate
    authenticity.
    """

    certificate_id: UUID = Field(
        ...,
        description="Certificate database UUID"
    )

    profile_id: UUID = Field(
        ...,
        description="Student profile UUID"
    )

    verification_status: str = Field(
        default="Not Verified",
        description="Overall verification status"
    )

    holder_name_match: Optional[bool] = Field(
        default=None,
        description=(
            "Legacy boolean comparison for certificate "
            "holder and profile name"
        )
    )

    holder_name_result: str = Field(
        default="NOT AVAILABLE",
        description=(
            "MATCH, MISMATCH, or NOT AVAILABLE"
        )
    )

    certificate_name_match: Optional[bool] = Field(
        default=None,
        description=(
            "Legacy boolean comparison for certificate name"
        )
    )

    certificate_name_result: str = Field(
        default="NOT AVAILABLE",
        description=(
            "MATCH, MISMATCH, or NOT AVAILABLE"
        )
    )

    course_name_match: Optional[bool] = Field(
        default=None,
        description=(
            "Legacy boolean comparison for course name"
        )
    )

    course_name_result: str = Field(
        default="NOT AVAILABLE",
        description=(
            "MATCH, MISMATCH, or NOT AVAILABLE"
        )
    )

    issuer_match: Optional[bool] = Field(
        default=None,
        description=(
            "Legacy boolean comparison for issuer"
        )
    )

    issuer_result: str = Field(
        default="NOT AVAILABLE",
        description=(
            "MATCH, MISMATCH, or NOT AVAILABLE"
        )
    )

    issue_date_match: Optional[bool] = Field(
        default=None,
        description=(
            "Legacy boolean comparison for issue date"
        )
    )

    issue_date_result: str = Field(
        default="NOT AVAILABLE",
        description=(
            "MATCH, MISMATCH, or NOT AVAILABLE"
        )
    )

    credential_id_present: bool = Field(
        default=False,
        description=(
            "Whether a credential ID is visibly present"
        )
    )

    credential_url_present: bool = Field(
        default=False,
        description=(
            "Whether a credential or verification URL "
            "is visibly present"
        )
    )

    original_image_available: bool = Field(
        default=False,
        description=(
            "Whether the original certificate image "
            "is available"
        )
    )

    evidence_points: List[str] = Field(
        default_factory=list,
        description=(
            "Evidence supporting the verification result"
        )
    )

    review_flags: List[str] = Field(
        default_factory=list,
        description=(
            "Issues or missing evidence requiring review"
        )
    )

    verification_notes: Optional[str] = Field(
        default=None,
        description=(
            "Human-readable verification explanation"
        )
    )
