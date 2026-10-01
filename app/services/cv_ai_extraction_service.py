
import json
from typing import Any, Dict, Optional, Set

from groq import Groq
from pydantic import ValidationError

from app.config.settings import settings
from app.models.cv_ai_extraction import (
    CVAIExtraction,
    CVAIExtractionResult,
)
from app.services.cv_ai_extraction_prompt import (
    CV_AI_EXTRACTION_SYSTEM_PROMPT,
    CV_AI_EXTRACTION_JSON_SCHEMA,
    build_cv_ai_extraction_prompt,
)


class CVAIExtractionError(Exception):
    """Raised when AI-based CV extraction fails."""


class CVAIExtractionService:
    """
    Groq-powered CV extraction service.

    The service enforces both:
    1. JSON/schema-level required fields.
    2. Pydantic structural/type validation.
    """

    REQUIRED_TOP_LEVEL_FIELDS: Set[str] = {
        "full_name",
        "professional_title",
        "professional_summary",
        "skills",
        "education",
        "experience",
        "projects",
        "certifications",
        "achievements",
        "languages",
        "interests",
        "warnings",
    }

    def __init__(
        self,
        client: Optional[Groq] = None,
        model: Optional[str] = None,
    ) -> None:
        self.client = client or Groq(api_key=settings.GROQ_API_KEY)
        self.model = model or settings.GROQ_MODEL

    def extract(self, cv_text: str) -> CVAIExtractionResult:
        """
        Extract structured information from CV text using Groq.
        """

        if not isinstance(cv_text, str):
            raise CVAIExtractionError("cv_text must be a string.")

        cleaned_text = cv_text.strip()

        if not cleaned_text:
            raise CVAIExtractionError("cv_text cannot be empty.")

        try:
            user_prompt = build_cv_ai_extraction_prompt(cleaned_text)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": CV_AI_EXTRACTION_SYSTEM_PROMPT,
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
                        "name": "cv_ai_extraction",
                        "strict": True,
                        "schema": CV_AI_EXTRACTION_JSON_SCHEMA,
                    },
                },
            )

            content = self._extract_response_content(response)
            payload = self._parse_json(content)

            self._validate_required_top_level_fields(payload)

            extraction = CVAIExtraction.model_validate(payload)

            warnings = list(extraction.warnings)

            return CVAIExtractionResult(
                success=True,
                extraction=extraction,
                source_text_length=len(cleaned_text),
                warnings=warnings,
            )

        except CVAIExtractionError:
            raise

        except ValidationError as exc:
            raise CVAIExtractionError(
                f"AI extraction validation failed: {exc}"
            ) from exc

        except Exception as exc:
            raise CVAIExtractionError(
                f"AI extraction request failed: {exc}"
            ) from exc

    @classmethod
    def _validate_required_top_level_fields(
        cls,
        payload: Dict[str, Any],
    ) -> None:
        """
        Ensure every required schema field is physically present.

        Pydantic defaults are intentionally not relied upon here because
        the AI response itself must satisfy the structured-output contract.
        """

        missing = sorted(
            cls.REQUIRED_TOP_LEVEL_FIELDS - set(payload.keys())
        )

        if missing:
            raise CVAIExtractionError(
                "AI extraction response is missing required fields: "
                + ", ".join(missing)
            )

    @staticmethod
    def _extract_response_content(response: Any) -> str:
        try:
            content = response.choices[0].message.content
        except (AttributeError, IndexError, TypeError) as exc:
            raise CVAIExtractionError(
                "Groq response did not contain a valid message."
            ) from exc

        if not isinstance(content, str) or not content.strip():
            raise CVAIExtractionError(
                "Groq returned an empty extraction response."
            )

        return content.strip()

    @staticmethod
    def _parse_json(content: str) -> Dict[str, Any]:
        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            raise CVAIExtractionError(
                f"Groq returned invalid JSON: {exc}"
            ) from exc

        if not isinstance(payload, dict):
            raise CVAIExtractionError(
                "Groq JSON response must be an object."
            )

        return payload
