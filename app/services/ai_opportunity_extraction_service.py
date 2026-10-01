
from __future__ import annotations

import json
from typing import Optional

from groq import Groq
from pydantic import ValidationError

from app.models.opportunity_extraction import (
    AIOpportunityExtraction,
    AIOpportunityExtractionResult,
)
from app.services.opportunity_extraction_prompt import (
    build_messages,
)


class AIOpportunityExtractionError(RuntimeError):
    """Raised when AI opportunity extraction fails."""


class AIOpportunityExtractionService:
    """
    Groq-backed opportunity extraction service.

    Uses Groq Structured Outputs so the model is constrained to the
    extraction schema before Pydantic performs final validation.
    """

    DEFAULT_MODEL = "openai/gpt-oss-20b"

    def __init__(
        self,
        client: Optional[Groq] = None,
        model_name: Optional[str] = None,
    ) -> None:
        self.client = client or Groq()
        self.model_name = model_name or self.DEFAULT_MODEL

    @staticmethod
    def _response_schema() -> dict:
        """
        Return a Groq-compatible JSON Schema.

        Strict Structured Outputs requires every field to be required.
        Optional semantic values are therefore represented as nullable
        JSON fields rather than omitted fields.
        """

        return {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "organization": {"type": "string"},
                "description": {"type": "string"},
                "location": {
                    "type": ["string", "null"],
                },
                "remote": {
                    "type": ["boolean", "null"],
                },
                "opportunity_type": {
                    "type": "string",
                },
                "eligibility": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "requirements": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "skills": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "benefits": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "application_url": {
                    "type": ["string", "null"],
                },
                "deadline": {
                    "type": ["string", "null"],
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "extraction_notes": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": [
                "title",
                "organization",
                "description",
                "location",
                "remote",
                "opportunity_type",
                "eligibility",
                "requirements",
                "skills",
                "benefits",
                "application_url",
                "deadline",
                "tags",
                "extraction_notes",
            ],
            "additionalProperties": False,
        }

    def extract(
        self,
        raw_text: str,
        *,
        source_name: Optional[str] = None,
        source_url: Optional[str] = None,
    ) -> AIOpportunityExtractionResult:

        if not isinstance(raw_text, str) or not raw_text.strip():
            raise AIOpportunityExtractionError(
                "raw_text must contain source content."
            )

        messages = build_messages(
            raw_text=raw_text,
            source_name=source_name,
            source_url=source_url,
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "opportunity_extraction",
                        "strict": True,
                        "schema": self._response_schema(),
                    },
                },
            )
        except Exception as exc:
            raise AIOpportunityExtractionError(
                f"Groq extraction request failed: {exc}"
            ) from exc

        try:
            content = response.choices[0].message.content
        except Exception as exc:
            raise AIOpportunityExtractionError(
                "Groq returned an invalid response structure."
            ) from exc

        if not content or not content.strip():
            raise AIOpportunityExtractionError(
                "Groq returned an empty extraction response."
            )

        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            raise AIOpportunityExtractionError(
                "Groq returned invalid JSON."
            ) from exc

        if not isinstance(payload, dict):
            raise AIOpportunityExtractionError(
                "Groq extraction must be a JSON object."
            )

        try:
            extraction = AIOpportunityExtraction.model_validate(payload)
        except ValidationError as exc:
            raise AIOpportunityExtractionError(
                f"AI extraction failed schema validation: {exc}"
            ) from exc

        return AIOpportunityExtractionResult(
            extraction=extraction,
            raw_source_text=raw_text,
            source_name=source_name,
            source_url=source_url,
            model_name=self.model_name,
            extraction_version="1.1",
        )
