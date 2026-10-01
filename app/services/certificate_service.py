from typing import List, Optional
from uuid import UUID

from app.models.certificate import Certificate
from app.services.supabase_service import supabase


class CertificateService:
    TABLE_NAME = "certificates"
    BUCKET_NAME = "certificate-documents"

    def create_certificate(
        self,
        certificate: Certificate
    ) -> dict:
        certificate_data = (
            certificate
            .model_dump(
                exclude_none=True,
                mode="json"
            )
        )

        response = (
            supabase
            .table(self.TABLE_NAME)
            .insert(certificate_data)
            .execute()
        )

        if not response.data:
            raise RuntimeError(
                "Certificate creation failed: "
                "Supabase returned no data."
            )

        return response.data[0]

    def get_certificate(
        self,
        certificate_id: UUID
    ) -> Optional[dict]:
        response = (
            supabase
            .table(self.TABLE_NAME)
            .select("*")
            .eq("id", str(certificate_id))
            .limit(1)
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    def get_profile_certificates(
        self,
        profile_id: UUID
    ) -> List[dict]:
        response = (
            supabase
            .table(self.TABLE_NAME)
            .select("*")
            .eq("profile_id", str(profile_id))
            .order(
                "created_at",
                desc=True
            )
            .execute()
        )

        return response.data or []

    def update_certificate(
        self,
        certificate_id: UUID,
        certificate: Certificate
    ) -> Optional[dict]:
        certificate_data = (
            certificate
            .model_dump(
                exclude_none=True,
                mode="json"
            )
        )

        response = (
            supabase
            .table(self.TABLE_NAME)
            .update(certificate_data)
            .eq("id", str(certificate_id))
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    def update_verification_result(
        self,
        certificate_id: UUID,
        verification_status: str,
        verification_notes: Optional[str] = None
    ) -> Optional[dict]:
        """
        Save the overall evidence-based verification
        result to the certificate record.

        This method intentionally updates only the
        verification fields. It does not overwrite
        certificate metadata with AI-extracted data.
        """

        valid_statuses = {
            "Not Verified",
            "AI Review",
            "Verified",
            "Needs Review"
        }

        if verification_status not in valid_statuses:
            raise ValueError(
                "Invalid verification status: "
                f"{verification_status}"
            )

        update_data = {
            "verification_status":
                verification_status,
            "verification_notes":
                verification_notes
        }

        response = (
            supabase
            .table(self.TABLE_NAME)
            .update(update_data)
            .eq(
                "id",
                str(certificate_id)
            )
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    def delete_certificate(
        self,
        certificate_id: UUID
    ) -> bool:
        response = (
            supabase
            .table(self.TABLE_NAME)
            .delete()
            .eq("id", str(certificate_id))
            .execute()
        )

        return bool(response.data)

    def upload_certificate_file(
        self,
        file_path: str,
        file_bytes: bytes,
        content_type: str
    ) -> str:
        storage_response = (
            supabase
            .storage
            .from_(self.BUCKET_NAME)
            .upload(
                file_path,
                file_bytes,
                {
                    "content-type": content_type,
                    "upsert": "false"
                }
            )
        )

        if storage_response is None:
            raise RuntimeError(
                "Certificate file upload failed."
            )

        return file_path

    def delete_certificate_file(
        self,
        file_path: str
    ) -> bool:
        response = (
            supabase
            .storage
            .from_(self.BUCKET_NAME)
            .remove([file_path])
        )

        return bool(response)

    def create_signed_url(
        self,
        file_path: str,
        expires_in: int = 3600
    ) -> str:
        response = (
            supabase
            .storage
            .from_(self.BUCKET_NAME)
            .create_signed_url(
                file_path,
                expires_in
            )
        )

        if not response:
            raise RuntimeError(
                "Unable to create certificate "
                "signed URL."
            )

        if isinstance(response, dict):
            signed_url = response.get(
                "signedURL"
            )

            if signed_url:
                return signed_url

        raise RuntimeError(
            "Supabase did not return a signed "
            "certificate URL."
        )


certificate_service = CertificateService()
