
import json


CV_RECOMMENDATIONS_SYSTEM_PROMPT = (
    "You are a CV recommendation assistant.\n\n"
    "Generate actionable recommendations using ONLY the supplied "
    "structured CV analysis and/or CV-job matching information.\n\n"
    "GROUNDING RULES:\n"
    "1. Never invent facts, skills, experience, qualifications, "
    "achievements, employers, dates, metrics, certifications, or "
    "job requirements.\n"
    "2. Every substantive recommendation must be grounded in supplied evidence.\n"
    "3. If information is missing, do not assume it exists.\n"
    "4. Do not convert absence of evidence into a factual negative claim.\n"
    "5. Recommendations may suggest adding, clarifying, quantifying, "
    "or improving information only when the supplied data supports it.\n"
    "6. Never invent measurable results or fabricated achievements.\n"
    "7. Job-specific recommendations must use only supplied matching evidence.\n"
    "8. Recommendations must be actionable and concise.\n"
    "9. Priority is optional and descriptive only: high, medium, or low.\n"
    "10. Return ONLY valid JSON matching the supplied schema.\n"
    "11. EVERY required property MUST be present in the JSON output.\n"
    "12. ALWAYS include all five recommendation arrays, even when empty.\n"
    "13. ALWAYS include recommendations.warnings as an array; use [] when "
    "there are no recommendation-specific warnings.\n"
    "14. ALWAYS include the top-level warnings array; use [] when there "
    "are no top-level warnings."
)


def build_cv_recommendations_prompt(
    cv_analysis=None,
    cv_matching=None,
):
    if cv_analysis is None and cv_matching is None:
        raise ValueError(
            "At least one of cv_analysis or cv_matching must be supplied."
        )

    payload = {
        "cv_analysis": (
            cv_analysis.model_dump(mode="json")
            if hasattr(cv_analysis, "model_dump")
            else cv_analysis
        ),
        "cv_matching": (
            cv_matching.model_dump(mode="json")
            if hasattr(cv_matching, "model_dump")
            else cv_matching
        ),
    }

    return (
        "Generate grounded CV recommendations from the following "
        "structured information.\n\n"
        "The output MUST contain every required property in the schema.\n"
        "If a recommendation category has no grounded recommendation, "
        "return an empty array for that category.\n"
        "The recommendations object MUST contain its warnings array; "
        "return [] when there are no warnings.\n"
        "The top-level warnings array MUST also be present; return [] "
        "when there are no warnings.\n"
        "Do not use information outside this input.\n\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
    )


recommendation_item_schema = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "title": {"type": "string"},
        "description": {"type": "string"},
        "action": {"type": "string"},
        "evidence": {"type": ["string", "null"]},
        "priority": {
            "type": ["string", "null"],
            "enum": ["high", "medium", "low", None],
        },
    },
    "required": [
        "title",
        "description",
        "action",
        "evidence",
        "priority",
    ],
}


CV_RECOMMENDATIONS_JSON_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "success": {
            "type": "boolean",
        },
        "recommendations": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "cv_improvements": {
                    "type": "array",
                    "items": recommendation_item_schema,
                },
                "skill_recommendations": {
                    "type": "array",
                    "items": recommendation_item_schema,
                },
                "experience_recommendations": {
                    "type": "array",
                    "items": recommendation_item_schema,
                },
                "job_match_recommendations": {
                    "type": "array",
                    "items": recommendation_item_schema,
                },
                "profile_recommendations": {
                    "type": "array",
                    "items": recommendation_item_schema,
                },
                "warnings": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": [
                "cv_improvements",
                "skill_recommendations",
                "experience_recommendations",
                "job_match_recommendations",
                "profile_recommendations",
                "warnings",
            ],
        },
        "warnings": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": [
        "success",
        "recommendations",
        "warnings",
    ],
}
