import json
from typing import Any, Dict


CV_ANALYSIS_SYSTEM_PROMPT = """
You are a professional CV analysis assistant.

Your task is to analyze structured information extracted from a candidate's CV.

GROUNDING RULES:
1. Use only information provided in the input.
2. Do not invent facts, skills, employers, degrees, certifications,
   achievements, responsibilities, dates, technologies, or outcomes.
3. Every substantive observation should be grounded in available CV evidence.
4. If evidence is missing, say that the information is not provided.
5. Do not convert assumptions into facts.
6. Do not infer a skill merely because it is common for a job title.
7. Do not invent measurable results or business impact.
8. Improvement suggestions may recommend clearer wording, stronger structure,
   or adding information if it genuinely exists, but must not fabricate it.
9. Preserve uncertainty when the source information is uncertain.
10. Keep analysis specific to the supplied CV.

ANALYSIS REQUIREMENTS:
- Identify evidence-based strengths.
- Identify weaknesses or areas where the CV is incomplete, unclear,
  inconsistent, or could be presented more effectively.
- Assess skills using only skills present in the supplied extraction.
- Analyze experience based on the supplied roles, dates, descriptions,
  employers, and evidence.
- Analyze education and certifications only when those sections contain data.
- Provide practical improvement suggestions without inventing content.
- Include warnings whenever the supplied information is insufficient
  for a reliable conclusion.

OUTPUT RULES:
- Return only JSON matching the supplied schema.
- Do not include markdown.
- Do not include commentary outside the JSON object.
- Keep evidence concise and directly connected to the source information.
"""


CV_ANALYSIS_JSON_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "strengths",
        "weaknesses",
        "skills_assessment",
        "experience_analysis",
        "education_analysis",
        "certifications_analysis",
        "improvement_suggestions",
        "warnings",
    ],
    "properties": {
        "strengths": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "title",
                    "description",
                    "evidence",
                ],
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "evidence": {
                        "type": ["string", "null"]
                    },
                },
            },
        },
        "weaknesses": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "title",
                    "description",
                    "evidence",
                ],
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "evidence": {
                        "type": ["string", "null"]
                    },
                },
            },
        },
        "skills_assessment": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "skill",
                    "assessment",
                    "evidence",
                ],
                "properties": {
                    "skill": {"type": "string"},
                    "assessment": {"type": "string"},
                    "evidence": {
                        "type": ["string", "null"]
                    },
                },
            },
        },
        "experience_analysis": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "title",
                    "description",
                    "evidence",
                ],
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "evidence": {
                        "type": ["string", "null"]
                    },
                },
            },
        },
        "education_analysis": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "title",
                    "description",
                    "evidence",
                ],
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "evidence": {
                        "type": ["string", "null"]
                    },
                },
            },
        },
        "certifications_analysis": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "title",
                    "description",
                    "evidence",
                ],
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "evidence": {
                        "type": ["string", "null"]
                    },
                },
            },
        },
        "improvement_suggestions": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "title",
                    "description",
                    "evidence",
                ],
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "evidence": {
                        "type": ["string", "null"]
                    },
                },
            },
        },
        "warnings": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
    },
}


def build_cv_analysis_prompt(
    extraction: Dict[str, Any],
) -> str:
    """
    Build a grounded analysis prompt from structured CV extraction data.
    """

    if not isinstance(extraction, dict):
        raise TypeError("extraction must be a dictionary.")

    serialized_extraction = json.dumps(
        extraction,
        ensure_ascii=False,
        indent=2,
    )

    return f"""
Analyze the following structured CV extraction.

Treat this extraction as the complete source of candidate information.
Do not use outside knowledge to fill missing details.

STRUCTURED CV EXTRACTION:
{serialized_extraction}

Return a JSON object matching the required CV analysis schema.

Remember:
- Ground observations in supplied evidence.
- Do not invent facts.
- Do not invent achievements or measurable outcomes.
- Do not infer skills that are not present.
- Identify missing or unclear information explicitly.
- Improvement suggestions must remain grounded.
""".strip()
