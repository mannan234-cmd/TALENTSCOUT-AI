
import json
from typing import Any, Dict, Union

from groq import Groq
from pydantic import ValidationError

from app.config.settings import settings
from app.models.cv_ai_extraction import CVAIExtraction
from app.models.cv_matching import CVJobMatchingResult
from app.services.cv_matching_prompt import (
    CV_JOB_MATCHING_JSON_SCHEMA,
    CV_JOB_MATCHING_SYSTEM_PROMPT,
    build_cv_job_matching_prompt,
)


class CVMatchingService:

    def __init__(self, client: Any = None) -> None:
        self.client = client or Groq(
            api_key=settings.GROQ_API_KEY
        )

        self.model = settings.GROQ_MODEL

    def match(
        self,
        cv_extraction: CVAIExtraction,
        job_description: Union[str, Dict[str, Any]],
    ) -> CVJobMatchingResult:

        if not isinstance(cv_extraction, CVAIExtraction):
            raise TypeError(
                "cv_extraction must be a CVAIExtraction instance."
            )

        prompt = build_cv_job_matching_prompt(
            cv_extraction=cv_extraction.model_dump(),
            job_description=job_description,
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "cv_job_matching",
                        "strict": True,
                        "schema": CV_JOB_MATCHING_JSON_SCHEMA,
                    },
                },
                messages=[
                    {
                        "role": "system",
                        "content": CV_JOB_MATCHING_SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
            )

        except Exception as exc:
            raise RuntimeError(
                "Groq CV-job matching request failed."
            ) from exc

        try:
            content = response.choices[0].message.content
        except (AttributeError, IndexError, TypeError) as exc:
            raise RuntimeError(
                "Groq returned an invalid CV-job matching response."
            ) from exc

        if not content:
            raise RuntimeError(
                "Groq returned an empty CV-job matching response."
            )

        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Groq returned invalid JSON for CV-job matching."
            ) from exc

        try:
            result = CVJobMatchingResult.model_validate(
                payload
            )
        except ValidationError as exc:
            raise RuntimeError(
                "Groq CV-job matching response failed schema validation."
            ) from exc

        if not result.success:
            raise RuntimeError(
                "CV-job matching was not successful."
            )

        return result
