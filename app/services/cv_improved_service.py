import json
from typing import Any, Dict

from app.models.cv_improved import CVImprovedResult
from app.services.groq_service import GroqService


class CVImprovedService:
    """
    Generates an improved CV while strictly grounding every factual
    statement in the supplied CV extraction/source data.
    """

    def __init__(self, client: Any = None) -> None:
        self.client = client or GroqService()

    @staticmethod
    def _dump(value: Any) -> Any:
        if hasattr(value, "model_dump"):
            return value.model_dump(mode="json")
        if isinstance(value, dict):
            return value
        return value

    def improve(
        self,
        extraction: Any,
        analysis: Any = None,
        recommendations: Any = None,
    ) -> CVImprovedResult:

        extraction_data = self._dump(extraction)
        analysis_data = self._dump(analysis)
        recommendations_data = self._dump(recommendations)

        prompt = f"""
You are a professional CV editor.

Improve the supplied CV content for clarity, professionalism, grammar,
structure, and impact.

STRICT GROUNDING RULES:
1. Never invent employers, job titles, dates, degrees, institutions,
   technologies, certifications, achievements, metrics, responsibilities,
   locations, or years of experience.
2. Never add a skill unless it is supported by the supplied CV data.
3. You may rewrite wording, improve grammar, remove repetition, and make
   existing achievements more concise and professional.
4. If a recommendation asks for information that is not supported by the
   CV, do NOT add that information.
5. Preserve factual meaning.
6. Do not fabricate metrics or quantify an achievement unless the original
   CV contains that quantity.
7. Return ONLY valid JSON matching the requested schema.

SOURCE CV EXTRACTION:
{json.dumps(extraction_data, ensure_ascii=False, default=str)}

CV ANALYSIS:
{json.dumps(analysis_data, ensure_ascii=False, default=str)}

CV RECOMMENDATIONS:
{json.dumps(recommendations_data, ensure_ascii=False, default=str)}

JSON SCHEMA:
{{
  "success": true,
  "professional_summary": "string",
  "experience": [
    {{
      "company": "existing company or empty string",
      "title": "existing title or empty string",
      "dates": "existing dates or empty string",
      "description": "professionally rewritten existing information"
    }}
  ],
  "skills": ["existing supported skills"],
  "education": [
    {{
      "degree": "existing degree",
      "institution": "existing institution",
      "dates": "existing dates or empty string"
    }}
  ],
  "certifications": ["existing supported certifications"],
  "projects": [
    {{
      "name": "existing project name",
      "description": "professionally rewritten existing information"
    }}
  ],
  "achievements": ["professionally rewritten existing achievements"],
  "languages": ["existing supported languages"],
  "warnings": ["limitations or information that could not safely be improved"]
}}
"""

        response = self.client.chat(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a strict, factual CV editor. "
                        "You must never invent CV facts."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError("AI returned an empty CV improvement response.")

        content = content.strip()

        if content.startswith("```"):
            content = content.replace("```json", "", 1)
            content = content.replace("```", "", 1).strip()

        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"AI returned invalid JSON for improved CV: {exc}"
            ) from exc

        return CVImprovedResult.model_validate(payload)


cv_improved_service = CVImprovedService()
