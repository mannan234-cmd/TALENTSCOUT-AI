from typing import Any, Dict, Optional, Union
from uuid import UUID

from pydantic import ValidationError

from app.models.cv_ai_extraction import CVAIExtraction
from app.models.cv_matching import CVJobMatchingResult
from app.services.cv_matching_service import CVMatchingService
from app.services.cv_service import CVService


class CVMatchingIntegrationService:
    """
    Coordinates CV-job matching and persistence.

    Flow:
        CV database record
            -> structured AI extraction
            -> CVMatchingService
            -> validated matching result
            -> database persistence
    """

    def __init__(
        self,
        matching_service: Optional[CVMatchingService] = None,
    ) -> None:
        self.matching_service = (
            matching_service or CVMatchingService()
        )

    def match_and_persist_for_cv(
        self,
        cv_id: UUID,
        job_description: Union[str, Dict[str, Any]],
        cv_service: Optional[CVService] = None,
    ) -> CVJobMatchingResult:

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

        result = self.matching_service.match(
            cv_extraction=extraction,
            job_description=job_description,
        )

        if not result.success:
            raise RuntimeError(
                "CV-job matching was not successful."
            )

        service.save_ai_matching(
            cv_id=cv_id,
            result=result,
        )

        return result
