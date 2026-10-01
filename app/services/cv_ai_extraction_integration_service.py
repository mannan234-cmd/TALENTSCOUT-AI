
from typing import Optional

from app.models.cv_ai_extraction import CVAIExtractionResult
from app.services.cv_ai_extraction_service import (
    CVAIExtractionError,
    CVAIExtractionService,
)
from app.services.cv_service import CVService


class CVAIExtractionIntegrationError(Exception):
    """Raised when CV AI extraction integration fails."""


class CVAIExtractionIntegrationService:
    """
    Integration layer between extracted CV text and the
    AI-powered CV extraction service.

    Responsibilities:
    - Validate incoming CV text.
    - Delegate AI extraction to CVAIExtractionService.
    - Return the validated CVAIExtractionResult.
    - Preserve the existing extraction contract.
    """

    def __init__(
        self,
        extraction_service: Optional[CVAIExtractionService] = None,
    ) -> None:
        self.extraction_service = (
            extraction_service
            or CVAIExtractionService()
        )

    def extract_from_text(
        self,
        cv_text: str,
    ) -> CVAIExtractionResult:
        """
        Extract structured CV information from supplied CV text.
        """

        if not isinstance(cv_text, str):
            raise CVAIExtractionIntegrationError(
                "cv_text must be a string."
            )

        cleaned_text = cv_text.strip()

        if not cleaned_text:
            raise CVAIExtractionIntegrationError(
                "cv_text cannot be empty."
            )

        try:
            result = self.extraction_service.extract(
                cleaned_text
            )

        except CVAIExtractionError as exc:
            raise CVAIExtractionIntegrationError(
                f"CV AI extraction failed: {exc}"
            ) from exc

        except Exception as exc:
            raise CVAIExtractionIntegrationError(
                f"CV AI extraction integration failed: {exc}"
            ) from exc

        if not isinstance(result, CVAIExtractionResult):
            raise CVAIExtractionIntegrationError(
                "AI extraction service returned an invalid result type."
            )

        if not result.success:
            raise CVAIExtractionIntegrationError(
                "AI extraction service returned an unsuccessful result."
            )

        return result

    def extract_and_persist_for_cv(
        self,
        cv_id,
        cv_service: CVService | None = None,
    ):
        """
        Extract structured AI data from an existing CV's
        extracted_text and persist the result to cvs.ai_extraction.

        The deterministic extracted_text field and extraction_status
        are not modified by this method.
        """
        service = cv_service or CVService()

        cv = service.get_cv(cv_id)

        if cv is None:
            raise ValueError("CV not found.")

        extracted_text = cv.get("extracted_text")

        if not isinstance(extracted_text, str):
            raise ValueError(
                "CV does not contain extracted text."
            )

        cleaned_text = extracted_text.strip()

        if not cleaned_text:
            raise ValueError(
                "CV does not contain readable extracted text."
            )

        result = self.extract_from_text(cleaned_text)

        if not result.success:
            raise RuntimeError(
                "AI extraction was not successful."
            )

        service.save_ai_extraction(
            cv_id=cv_id,
            result=result,
        )

        return result
