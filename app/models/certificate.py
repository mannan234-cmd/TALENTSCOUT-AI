from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class Certificate(BaseModel):
    """
    Certificate record for a student's master profile.

    The original certificate file is stored separately in
    Supabase Storage. This model stores its metadata and
    verification information.
    """

    profile_id: UUID = Field(
        ...,
        description="Student profile UUID"
    )

    certificate_name: str = Field(
        ...,
        min_length=2,
        description="Name of the certificate"
    )

    course_name: Optional[str] = Field(
        default=None,
        description=(
            "Name of the course or training associated "
            "with the certificate"
        )
    )

    issuing_organization: Optional[str] = Field(
        default=None,
        description="Organization that issued the certificate"
    )

    issue_date: Optional[date] = Field(
        default=None,
        description="Certificate issue date"
    )

    expiration_date: Optional[date] = Field(
        default=None,
        description="Certificate expiration date"
    )

    credential_id: Optional[str] = Field(
        default=None,
        description="Certificate credential ID"
    )

    credential_url: Optional[HttpUrl] = Field(
        default=None,
        description="URL where the credential can be verified"
    )

    certificate_file_path: Optional[str] = Field(
        default=None,
        description="Path of the certificate file in Supabase Storage"
    )

    certificate_file_name: Optional[str] = Field(
        default=None,
        description="Original uploaded filename"
    )

    certificate_file_type: Optional[str] = Field(
        default=None,
        description="Uploaded file MIME type"
    )

    verification_status: str = Field(
        default="Not Verified",
        description="Current certificate verification status"
    )

    verification_notes: Optional[str] = Field(
        default=None,
        description="Notes about certificate verification"
    )