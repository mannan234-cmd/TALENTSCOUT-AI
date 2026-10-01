
from typing import Optional
from uuid import UUID

from pydantic import ValidationError

from app.models.cv_analysis import CVAnalysis
from app.models.cv_matching import CVJobMatching
from app.models.cv_recommendations import CVRecommendationsResult
from app.services.cv_recommendations_service import (
    CVRecommendationsService,
)
from app.services.cv_service import CVService


class CVRecommendationsIntegrationService:
    def __init__(
        self,
        recommendations_service: Optional[
            CVRecommendationsService
        ] = None,
    ) -> None:
        self.recommendations_service = (
            recommendations_service
            or CVRecommendationsService()
        )

    def recommend_and_persist_for_cv(
        self,
        cv_id: UUID,
        cv_service: Optional[CVService] = None,
    ) -> CVRecommendationsResult:
        service = cv_service or CVService()

        cv = service.get_cv(cv_id)

        if cv is None:
            raise ValueError("CV not found.")

        ai_analysis = cv.get("ai_analysis")
        ai_matching = cv.get("ai_matching")

        if ai_analysis is None and ai_matching is None:
            raise ValueError(
                "CV does not contain AI analysis or AI matching."
            )

        analysis = None
        matching = None

        if ai_analysis is not None:
            try:
                analysis = CVAnalysis.model_validate(ai_analysis)
            except ValidationError as exc:
                raise ValueError(
                    "CV contains invalid AI analysis."
                ) from exc

        if ai_matching is not None:
            try:
                matching = CVJobMatching.model_validate(ai_matching)
            except ValidationError as exc:
                raise ValueError(
                    "CV contains invalid AI matching."
                ) from exc

        result = self.recommendations_service.recommend(
            cv_analysis=analysis,
            cv_matching=matching,
        )

        if not result.success:
            raise RuntimeError(
                "CV recommendations were not successful."
            )

        service.save_ai_recommendations(
            cv_id=cv_id,
            result=result,
        )

        return result
