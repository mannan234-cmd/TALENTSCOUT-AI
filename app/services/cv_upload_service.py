from pathlib import Path
from typing import Optional
from uuid import UUID, uuid4

from app.models.cv import CV
from app.services.cv_service import cv_service
from app.services.cv_validator import cv_validator


class CVUploadService:
    """
    Handles CV validation, Storage upload, and CV database creation.

    Active-CV rule:
    - First CV for a profile becomes active.
    - Additional CVs are created as inactive.
    - Users can explicitly switch the active CV through CVService.
    """

    def upload_cv(
        self,
        profile_id: UUID,
        file_name: str,
        file_bytes: bytes,
        mime_type: Optional[str] = None,
    ) -> dict:

        validation = cv_validator.validate(
            file_name=file_name,
            file_bytes=file_bytes,
            mime_type=mime_type,
        )

        if not validation.is_valid:
            raise ValueError(validation.message)

        extension = Path(file_name).suffix.lower()
        unique_id = uuid4().hex

        storage_path = (
            f"{profile_id}/{unique_id}{extension}"
        )

        storage_uploaded = False

        try:
            # First CV becomes active.
            # Additional CVs become inactive.
            existing_active_cv = cv_service.get_active_cv(
                profile_id
            )

            is_active = existing_active_cv is None

            # Upload original file to private Storage.
            # CVService expects the parameter name "file_path".
            cv_service.upload_cv_file(
                file_path=storage_path,
                file_bytes=file_bytes,
                content_type=mime_type or "application/octet-stream",
            )

            storage_uploaded = True

            cv = CV(
                profile_id=profile_id,
                original_file_name=file_name,
                original_file_path=storage_path,
                file_type=validation.file_type,
                file_size_bytes=validation.file_size_bytes,
                extraction_status="Not Processed",
                analysis_status="Not Analyzed",
                improvement_status="Not Reviewed",
                is_active=is_active,
            )

            return cv_service.create_cv(cv)

        except Exception:

            # Roll back Storage upload if database creation fails.
            if storage_uploaded:
                try:
                    cv_service.delete_cv_file(
                        storage_path
                    )
                except Exception:
                    pass

            raise


cv_upload_service = CVUploadService()
