from typing import Optional
from uuid import UUID

from pydantic import ValidationError

from app.models.cv_ai_extraction import CVAIExtraction
from app.models.cv_analysis import CVAnalysisResult
from app.services.cv_analysis_service import CVAnalysisService
from app.services.cv_service import CVService


class CVAnalysisIntegrationService:
    """
    Coordinates structured CV analysis and persistence.

    The analysis is based only on the existing structured
    AI extraction stored for the CV.
    """

    def __init__(
        self,
        analysis_service: Optional[CVAnalysisService] = None,
    ) -> None:
        self.analysis_service = (
            analysis_service or CVAnalysisService()
        )

    def analyze_and_persist_for_cv(
        self,
        cv_id: UUID,
        cv_service: Optional[CVService] = None,
    ) -> CVAnalysisResult:
        service = cv_service or CVService()

        cv = service.get_cv(cv_id)

        if cv is None:
            raise ValueError("CV not found.")

        ai_extraction = cv.get("ai_extraction")

        if ai_extraction is None:
            raise ValueError(
                "CV does not contain structured AI extraction."
            )

        if isinstance(ai_extraction, dict):
            try:
                extraction = CVAIExtraction.model_validate(
                    ai_extraction
                )
            except ValidationError as exc:
                raise ValueError(
                    "CV contains invalid structured AI extraction."
                ) from exc

        elif isinstance(ai_extraction, CVAIExtraction):
            extraction = ai_extraction

        else:
            raise ValueError(
                "CV ai_extraction has an invalid format."
            )

        result = self.analysis_service.analyze(extraction)

        if not result.success:
            raise RuntimeError(
                "CV analysis was not successful."
            )

        service.save_ai_analysis(
            cv_id=cv_id,
            result=result,
        )

        return result
