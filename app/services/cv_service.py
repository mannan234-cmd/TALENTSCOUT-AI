from typing import List, Optional
from uuid import UUID

from app.models.cv import CV
from app.models.cv_ai_extraction import CVAIExtractionResult
from app.models.cv_analysis import CVAnalysisResult
from app.models.cv_matching import CVJobMatchingResult
from app.models.cv_recommendations import CVRecommendationsResult
from app.services.supabase_service import supabase


class CVService:
    TABLE_NAME = "cvs"
    BUCKET_NAME = "cv-documents"

    def create_cv(self, cv: CV) -> dict:
        cv_data = cv.model_dump(
            exclude_none=True,
            mode="json"
        )

        response = (
            supabase
            .table(self.TABLE_NAME)
            .insert(cv_data)
            .execute()
        )

        if not response.data:
            raise RuntimeError(
                "CV creation failed: "
                "Supabase returned no data."
            )

        return response.data[0]

    def get_cv(
        self,
        cv_id: UUID
    ) -> Optional[dict]:

        response = (
            supabase
            .table(self.TABLE_NAME)
            .select("*")
            .eq("id", str(cv_id))
            .limit(1)
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    def get_profile_cvs(
        self,
        profile_id: UUID
    ) -> List[dict]:

        response = (
            supabase
            .table(self.TABLE_NAME)
            .select("*")
            .eq("profile_id", str(profile_id))
            .order("created_at", desc=True)
            .execute()
        )

        return response.data or []

    def get_active_cv(
        self,
        profile_id: UUID
    ) -> Optional[dict]:

        response = (
            supabase
            .table(self.TABLE_NAME)
            .select("*")
            .eq("profile_id", str(profile_id))
            .eq("is_active", True)
            .limit(1)
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    def update_cv(
        self,
        cv_id: UUID,
        cv: CV
    ) -> Optional[dict]:

        cv_data = cv.model_dump(
            exclude_none=True,
            mode="json"
        )

        response = (
            supabase
            .table(self.TABLE_NAME)
            .update(cv_data)
            .eq("id", str(cv_id))
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    def update_extraction_status(
        self,
        cv_id: UUID,
        extraction_status: str
    ) -> Optional[dict]:

        valid_statuses = {
            "Not Processed",
            "Processing",
            "Completed",
            "Failed"
        }

        if extraction_status not in valid_statuses:
            raise ValueError(
                f"Invalid extraction status: "
                f"{extraction_status}"
            )

        response = (
            supabase
            .table(self.TABLE_NAME)
            .update({
                "extraction_status": extraction_status
            })
            .eq("id", str(cv_id))
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    def update_analysis_status(
        self,
        cv_id: UUID,
        analysis_status: str
    ) -> Optional[dict]:

        valid_statuses = {
            "Not Analyzed",
            "Processing",
            "Completed",
            "Failed"
        }

        if analysis_status not in valid_statuses:
            raise ValueError(
                f"Invalid analysis status: "
                f"{analysis_status}"
            )

        response = (
            supabase
            .table(self.TABLE_NAME)
            .update({
                "analysis_status": analysis_status
            })
            .eq("id", str(cv_id))
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    def update_improvement_status(
        self,
        cv_id: UUID,
        improvement_status: str
    ) -> Optional[dict]:

        valid_statuses = {
            "Not Reviewed",
            "Under Review",
            "Approved",
            "Generated"
        }

        if improvement_status not in valid_statuses:
            raise ValueError(
                f"Invalid improvement status: "
                f"{improvement_status}"
            )

        response = (
            supabase
            .table(self.TABLE_NAME)
            .update({
                "improvement_status": improvement_status
            })
            .eq("id", str(cv_id))
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    def set_active_status(
        self,
        cv_id: UUID,
        is_active: bool
    ) -> Optional[dict]:

        response = (
            supabase
            .table(self.TABLE_NAME)
            .update({
                "is_active": is_active
            })
            .eq("id", str(cv_id))
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    def set_active_cv(
        self,
        profile_id: UUID,
        cv_id: UUID
    ) -> Optional[dict]:

        # -------------------------------------------------
        # Verify CV belongs to the requested profile
        # -------------------------------------------------

        target_cv = self.get_cv(cv_id)

        if target_cv is None:
            raise ValueError(
                "CV not found."
            )

        if target_cv["profile_id"] != str(profile_id):
            raise ValueError(
                "CV does not belong to the specified profile."
            )

        # -------------------------------------------------
        # Deactivate all CVs for this profile
        # -------------------------------------------------

        supabase \
            .table(self.TABLE_NAME) \
            .update({
                "is_active": False
            }) \
            .eq("profile_id", str(profile_id)) \
            .execute()

        # -------------------------------------------------
        # Activate requested CV
        # -------------------------------------------------

        response = (
            supabase
            .table(self.TABLE_NAME)
            .update({
                "is_active": True
            })
            .eq("id", str(cv_id))
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    def delete_cv(
        self,
        cv_id: UUID
    ) -> bool:

        response = (
            supabase
            .table(self.TABLE_NAME)
            .delete()
            .eq("id", str(cv_id))
            .execute()
        )

        return bool(response.data)

    def delete_cv_with_file(
        self,
        cv_id: UUID
    ) -> bool:

        # -------------------------------------------------
        # Get CV before deleting database record
        # -------------------------------------------------

        cv = self.get_cv(cv_id)

        if cv is None:
            return False

        storage_path = cv.get(
            "original_file_path"
        )

        # -------------------------------------------------
        # Delete database record
        # -------------------------------------------------

        deleted = self.delete_cv(cv_id)

        if not deleted:
            return False

        # -------------------------------------------------
        # Delete original Storage file
        # -------------------------------------------------

        if storage_path:
            try:
                self.delete_cv_file(
                    storage_path
                )
            except Exception:
                # Database deletion succeeded.
                # Storage cleanup failure should not
                # falsely report database deletion failure.
                pass

        return True

    def upload_cv_file(
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
                "CV file upload failed."
            )

        return file_path

    def delete_cv_file(
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
                "Unable to create CV signed URL."
            )

        if isinstance(response, dict):
            signed_url = response.get(
                "signedURL"
            )

            if signed_url:
                return signed_url

        raise RuntimeError(
            "Supabase did not return a signed CV URL."
        )

    # TALENTSCOUT_CV_EXTRACTION_WORKFLOW

    def extract_cv_text(self, cv_id: UUID) -> dict:
        """
        Download the original CV from Supabase Storage,
        extract readable text, save it to the CV record,
        and update extraction status.

        The original CV file is never modified.
        """

        from app.services.cv_text_extractor import (
            cv_text_extractor,
            CVTextExtractionError,
        )

        cv = self.get_cv(cv_id)

        if cv is None:
            raise ValueError(
                "CV not found."
            )

        storage_path = cv.get(
            "original_file_path"
        )

        if not storage_path:
            raise ValueError(
                "CV does not have an original storage path."
            )

        file_name = cv.get(
            "original_file_name"
        )

        if not file_name:
            raise ValueError(
                "CV does not have an original filename."
            )

        # Mark extraction as Processing
        self.update_extraction_status(
            cv_id=cv_id,
            extraction_status="Processing",
        )

        try:

            # Download original CV
            file_bytes = (
                supabase
                .storage
                .from_(self.BUCKET_NAME)
                .download(storage_path)
            )

            if not file_bytes:
                raise CVTextExtractionError(
                    "Downloaded CV file is empty."
                )

            # Extract readable text
            extracted_text = (
                cv_text_extractor.extract(
                    file_name=file_name,
                    file_bytes=file_bytes,
                )
            )

            if not extracted_text.strip():
                raise CVTextExtractionError(
                    "No readable text was extracted from the CV."
                )

            # Save extracted text
            response = (
                supabase
                .table(self.TABLE_NAME)
                .update({
                    "extracted_text": extracted_text,
                    "extraction_status": "Completed",
                })
                .eq(
                    "id",
                    str(cv_id)
                )
                .execute()
            )

            if not response.data:
                raise RuntimeError(
                    "CV extraction succeeded, but "
                    "the extracted text could not be saved."
                )

            return response.data[0]

        except Exception:

            # Record failure
            try:
                self.update_extraction_status(
                    cv_id=cv_id,
                    extraction_status="Failed",
                )
            except Exception:
                pass

            raise

    def save_ai_extraction(
        self,
        cv_id: UUID,
        result: CVAIExtractionResult,
    ) -> Optional[dict]:
        """
        Persist a validated structured AI extraction for a CV.

        The extraction is stored as JSONB in the cvs.ai_extraction
        column. The existing deterministic extracted_text and
        extraction_status fields are not modified.
        """

        if not isinstance(result, CVAIExtractionResult):
            raise TypeError(
                "result must be a CVAIExtractionResult."
            )

        if not result.success:
            raise ValueError(
                "Cannot persist an unsuccessful AI extraction result."
            )

        extraction_data = result.extraction.model_dump(
            mode="json"
        )

        response = (
            supabase.table(self.TABLE_NAME)
            .update({
                "ai_extraction": extraction_data,
            })
            .eq("id", str(cv_id))
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    def save_ai_analysis(
        self,
        cv_id: UUID,
        result: CVAnalysisResult,
    ) -> Optional[dict]:
        """
        Persist a validated structured AI analysis for a CV.

        The analysis is stored as JSONB in the cvs.ai_analysis
        column. Existing CV extraction fields and statuses are
        not modified.
        """

        if not isinstance(result, CVAnalysisResult):
            raise TypeError(
                "result must be a CVAnalysisResult."
            )

        if not result.success:
            raise ValueError(
                "Cannot persist an unsuccessful CV analysis result."
            )

        analysis_data = result.analysis.model_dump(
            mode="json"
        )

        response = (
            supabase.table(self.TABLE_NAME)
            .update({
                "ai_analysis": analysis_data,
            })
            .eq("id", str(cv_id))
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    def save_ai_recommendations(
        self,
        cv_id: UUID,
        result: CVRecommendationsResult,
    ):
        if not isinstance(result, CVRecommendationsResult):
            raise TypeError(
                "result must be a CVRecommendationsResult instance."
            )

        if not result.success:
            raise ValueError(
                "Cannot persist unsuccessful CV recommendations."
            )

        payload = result.recommendations.model_dump(mode="json")

        response = (
            supabase
            .table("cvs")
            .update({"ai_recommendations": payload})
            .eq("id", str(cv_id))
            .execute()
        )

        return response

    def save_ai_matching(
        self,
        cv_id: UUID,
        result: CVJobMatchingResult,
    ) -> Optional[dict]:
        """
        Persist a validated structured AI CV-job matching result
        for a CV.

        The matching result is stored as JSONB in the
        cvs.ai_matching column.

        Existing CV extraction and analysis fields are not modified.
        """

        if not isinstance(result, CVJobMatchingResult):
            raise TypeError(
                "result must be a CVJobMatchingResult."
            )

        if not result.success:
            raise ValueError(
                "Cannot persist an unsuccessful CV-job matching result."
            )

        matching_data = result.matching.model_dump(
            mode="json"
        )

        response = (
            supabase.table(self.TABLE_NAME)
            .update({
                "ai_matching": matching_data,
            })
            .eq("id", str(cv_id))
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]


cv_service = CVService()