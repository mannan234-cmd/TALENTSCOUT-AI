from typing import Any, Dict, Optional, Union
from uuid import UUID

from app.models.cv_workflow import CVWorkflowResult
from app.services.cv_ai_extraction_integration_service import (
    CVAIExtractionIntegrationService,
)
from app.services.cv_analysis_integration_service import (
    CVAnalysisIntegrationService,
)
from app.services.cv_matching_integration_service import (
    CVMatchingIntegrationService,
)
from app.services.cv_recommendations_integration_service import (
    CVRecommendationsIntegrationService,
)


class CVWorkflowService:
    """
    Production orchestration for the completed CV AI pipeline.

    Extraction -> Analysis -> optional Job Matching -> Recommendations.
    """

    def __init__(
        self,
        extraction_service: Optional[
            CVAIExtractionIntegrationService
        ] = None,
        analysis_service: Optional[
            CVAnalysisIntegrationService
        ] = None,
        matching_service: Optional[
            CVMatchingIntegrationService
        ] = None,
        recommendations_service: Optional[
            CVRecommendationsIntegrationService
        ] = None,
    ) -> None:
        self.extraction_service = (
            extraction_service or CVAIExtractionIntegrationService()
        )
        self.analysis_service = (
            analysis_service or CVAnalysisIntegrationService()
        )
        self.matching_service = (
            matching_service or CVMatchingIntegrationService()
        )
        self.recommendations_service = (
            recommendations_service
            or CVRecommendationsIntegrationService()
        )

    def run(
        self,
        cv_id: UUID,
        source_text: str,
        job_description: Optional[
            Union[str, Dict[str, Any]]
        ] = None,
    ) -> CVWorkflowResult:

        if not source_text or not source_text.strip():
            raise ValueError("source_text must not be empty.")

        warnings = []

        # 1. Extraction
        extraction_result = (
            self.extraction_service.extract_and_persist_for_cv(
                cv_id=cv_id,
            )
        )

        if not extraction_result.success:
            raise RuntimeError(
                "CV extraction was not successful."
            )

        warnings.extend(extraction_result.warnings)

        # 2. Analysis
        analysis_result = (
            self.analysis_service.analyze_and_persist_for_cv(
                cv_id=cv_id,
            )
        )

        if not analysis_result.success:
            raise RuntimeError(
                "CV analysis was not successful."
            )

        warnings.extend(analysis_result.warnings)

        # 3. Optional job matching
        matching_completed = False

        if job_description is not None:
            matching_result = (
                self.matching_service.match_and_persist_for_cv(
                    cv_id=cv_id,
                    job_description=job_description,
                )
            )

            if not matching_result.success:
                raise RuntimeError(
                    "CV-job matching was not successful."
                )

            warnings.extend(matching_result.warnings)
            matching_completed = True

        # 4. Recommendations
        recommendations_result = (
            self.recommendations_service.recommend_and_persist_for_cv(
                cv_id=cv_id,
            )
        )

        if not recommendations_result.success:
            raise RuntimeError(
                "CV recommendations were not successful."
            )

        warnings.extend(recommendations_result.warnings)

        return CVWorkflowResult(
            success=True,
            cv_id=cv_id,
            extraction_completed=True,
            analysis_completed=True,
            matching_completed=matching_completed,
            recommendations_completed=True,
            warnings=warnings,
        )
