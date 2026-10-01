import json
from typing import Any, Dict, Optional, Set

from groq import Groq
from pydantic import ValidationError

from app.config.settings import settings
from app.models.cv_ai_extraction import CVAIExtraction
from app.models.cv_analysis import (
    CVAnalysis,
    CVAnalysisResult,
)
from app.services.cv_analysis_prompt import (
    CV_ANALYSIS_JSON_SCHEMA,
    CV_ANALYSIS_SYSTEM_PROMPT,
    build_cv_analysis_prompt,
)


class CVAnalysisError(Exception):
    """Raised when CV analysis fails."""


class CVAnalysisService:
    REQUIRED_TOP_LEVEL_FIELDS: Set[str] = {
        "strengths",
        "weaknesses",
        "skills_assessment",
        "experience_analysis",
        "education_analysis",
        "certifications_analysis",
        "improvement_suggestions",
        "warnings",
    }

    def __init__(
        self,
        client: Optional[Groq] = None,
        model: Optional[str] = None,
    ) -> None:
        self.client = client or Groq(
            api_key=settings.GROQ_API_KEY
        )
        self.model = model or settings.GROQ_MODEL

    def analyze(
        self,
        extraction: CVAIExtraction,
    ) -> CVAnalysisResult:
        if not isinstance(extraction, CVAIExtraction):
            raise CVAnalysisError(
                "extraction must be a CVAIExtraction."
            )

        extraction_data = extraction.model_dump(
            mode="json"
        )

        try:
            user_prompt = build_cv_analysis_prompt(
                extraction_data
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": CV_ANALYSIS_SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                temperature=0,
        max_completion_tokens=8192,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "cv_analysis",
                        "strict": True,
                        "schema": CV_ANALYSIS_JSON_SCHEMA,
                    },
                },
            )

            content = self._extract_response_content(
                response
            )

            payload = self._parse_json(content)

            self._validate_required_top_level_fields(
                payload
            )

            analysis = CVAnalysis.model_validate(
                payload
            )

            warnings = list(analysis.warnings)

            return CVAnalysisResult(
                success=True,
                analysis=analysis,
                warnings=warnings,
            )

        except CVAnalysisError:
            raise

        except ValidationError as exc:
            raise CVAnalysisError(
                f"CV analysis validation failed: {exc}"
            ) from exc

        except Exception as exc:
            raise CVAnalysisError(
                f"CV analysis request failed: {exc}"
            ) from exc

    @classmethod
    def _validate_required_top_level_fields(
        cls,
        payload: Dict[str, Any],
    ) -> None:
        missing = sorted(
            cls.REQUIRED_TOP_LEVEL_FIELDS
            - set(payload.keys())
        )

        if missing:
            raise CVAnalysisError(
                "CV analysis response is missing required fields: "
                + ", ".join(missing)
            )

    @staticmethod
    def _extract_response_content(
        response: Any,
    ) -> str:
        try:
            content = response.choices[0].message.content
        except (
            AttributeError,
            IndexError,
            TypeError,
        ) as exc:
            raise CVAnalysisError(
                "Groq response did not contain a valid message."
            ) from exc

        if not isinstance(content, str) or not content.strip():
            raise CVAnalysisError(
                "Groq returned an empty analysis response."
            )

        return content.strip()

    @staticmethod
    def _parse_json(
        content: str,
    ) -> Dict[str, Any]:
        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            raise CVAnalysisError(
                f"Groq returned invalid JSON: {exc}"
            ) from exc

        if not isinstance(payload, dict):
            raise CVAnalysisError(
                "Groq JSON response must be an object."
            )

        return payload
