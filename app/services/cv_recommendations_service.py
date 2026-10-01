
import json
from typing import Any

from groq import Groq
from pydantic import ValidationError

from app.config.settings import settings
from app.models.cv_recommendations import CVRecommendationsResult
from app.services.cv_recommendations_prompt import (
    CV_RECOMMENDATIONS_JSON_SCHEMA,
    CV_RECOMMENDATIONS_SYSTEM_PROMPT,
    build_cv_recommendations_prompt,
)


class CVRecommendationsService:
    """
    Generates grounded CV recommendations from structured
    CV analysis and/or CV-job matching data.
    """

    def __init__(self, client: Any = None) -> None:
        self.client = client or Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    def recommend(
        self,
        cv_analysis: Any = None,
        cv_matching: Any = None,
    ) -> CVRecommendationsResult:
        """
        Generate and validate structured recommendations.
        """

        prompt = build_cv_recommendations_prompt(
            cv_analysis=cv_analysis,
            cv_matching=cv_matching,
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "cv_recommendations",
                        "strict": True,
                        "schema": CV_RECOMMENDATIONS_JSON_SCHEMA,
                    },
                },
                messages=[
                    {
                        "role": "system",
                        "content": CV_RECOMMENDATIONS_SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
            )
        except Exception as exc:
            raise RuntimeError(
                "Groq CV recommendations request failed."
            ) from exc

        try:
            content = response.choices[0].message.content
        except (AttributeError, IndexError, TypeError) as exc:
            raise RuntimeError(
                "Groq returned an invalid CV recommendations response."
            ) from exc

        if not content:
            raise RuntimeError(
                "Groq returned an empty CV recommendations response."
            )

        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Groq returned invalid JSON for CV recommendations."
            ) from exc

        try:
            result = CVRecommendationsResult.model_validate(payload)
        except ValidationError as exc:
            raise RuntimeError(
                "Groq CV recommendations response failed schema validation."
            ) from exc

        if not result.success:
            raise RuntimeError(
                "CV recommendations were not successful."
            )

        return result
