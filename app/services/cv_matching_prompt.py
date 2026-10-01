from typing import Any, Dict, Union


MATCH_STATUS_VALUES = [
    "Matched",
    "Partial",
    "Not Matched",
    "Unknown",
]


CV_JOB_MATCHING_SYSTEM_PROMPT = """
You are a CV-to-job matching analysis system.

Your task is to compare the supplied structured CV information
against the supplied job description.

GROUNDING RULES:
1. Use only information explicitly present in the supplied CV
   and job description.
2. Do not invent skills, experience, education, certifications,
   projects, achievements, responsibilities, technologies,
   employers, dates, or results.
3. Do not infer experience solely from a job title.
4. Do not assume a skill exists because it is related to another skill.
5. If the CV does not provide enough evidence to determine a match,
   use "Unknown".
6. Every substantive CV-side observation must be supported by
   CV evidence when available.
7. Every substantive job-side requirement must be supported by
   job evidence when available.
8. Distinguish clearly between matched, partially matched,
   not matched, and unknown requirements.
9. Do not create measurable achievements or outcomes that are not
   explicitly present in the supplied information.
10. Do not invent missing education, experience, skills, or
    qualifications.
11. Do not use external knowledge to fill missing CV information.
12. Do not assign a numeric score unless explicitly requested.
13. Keep explanations evidence-based and concise.
14. If information is missing, say that it is missing rather than
    guessing.

MATCH STATUS VALUES:
- Matched: the supplied CV evidence clearly satisfies the requirement.
- Partial: the supplied CV evidence partially satisfies the requirement.
- Not Matched: the supplied CV evidence conflicts with or does not
  satisfy the requirement where enough evidence exists.
- Unknown: there is insufficient CV evidence to determine the match.

OUTPUT RULES:
1. Return only valid JSON matching the supplied JSON schema.
2. Do not return Markdown.
3. Do not add fields outside the schema.
4. The top-level response must contain:
   - success
   - matching
   - warnings
5. The "matching" object must contain:
   - overall_summary
   - strengths
   - weaknesses
   - skills_match
   - experience_match
   - education_match
   - gaps
   - warnings
6. Keep the response grounded strictly in the supplied CV and job
   description.
"""


CV_JOB_MATCHING_JSON_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "success",
        "matching",
        "warnings",
    ],
    "properties": {
        "success": {
            "type": "boolean",
        },
        "matching": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "overall_summary",
                "strengths",
                "weaknesses",
                "skills_match",
                "experience_match",
                "education_match",
                "gaps",
                "warnings",
            ],
            "properties": {
                "overall_summary": {
                    "type": "string",
                    "minLength": 1,
                },
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
                            "title": {
                                "type": "string",
                                "minLength": 1,
                            },
                            "description": {
                                "type": "string",
                                "minLength": 1,
                            },
                            "evidence": {
                                "type": [
                                    "string",
                                    "null",
                                ],
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
                            "title": {
                                "type": "string",
                                "minLength": 1,
                            },
                            "description": {
                                "type": "string",
                                "minLength": 1,
                            },
                            "evidence": {
                                "type": [
                                    "string",
                                    "null",
                                ],
                            },
                        },
                    },
                },
                "skills_match": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": [
                            "skill",
                            "match_status",
                            "cv_evidence",
                            "job_evidence",
                            "explanation",
                        ],
                        "properties": {
                            "skill": {
                                "type": "string",
                                "minLength": 1,
                            },
                            "match_status": {
                                "type": "string",
                                "enum": MATCH_STATUS_VALUES,
                            },
                            "cv_evidence": {
                                "type": [
                                    "string",
                                    "null",
                                ],
                            },
                            "job_evidence": {
                                "type": [
                                    "string",
                                    "null",
                                ],
                            },
                            "explanation": {
                                "type": "string",
                                "minLength": 1,
                            },
                        },
                    },
                },
                "experience_match": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": [
                            "requirement",
                            "match_status",
                            "cv_evidence",
                            "job_evidence",
                            "explanation",
                        ],
                        "properties": {
                            "requirement": {
                                "type": "string",
                                "minLength": 1,
                            },
                            "match_status": {
                                "type": "string",
                                "enum": MATCH_STATUS_VALUES,
                            },
                            "cv_evidence": {
                                "type": [
                                    "string",
                                    "null",
                                ],
                            },
                            "job_evidence": {
                                "type": [
                                    "string",
                                    "null",
                                ],
                            },
                            "explanation": {
                                "type": "string",
                                "minLength": 1,
                            },
                        },
                    },
                },
                "education_match": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": [
                            "requirement",
                            "match_status",
                            "cv_evidence",
                            "job_evidence",
                            "explanation",
                        ],
                        "properties": {
                            "requirement": {
                                "type": "string",
                                "minLength": 1,
                            },
                            "match_status": {
                                "type": "string",
                                "enum": MATCH_STATUS_VALUES,
                            },
                            "cv_evidence": {
                                "type": [
                                    "string",
                                    "null",
                                ],
                            },
                            "job_evidence": {
                                "type": [
                                    "string",
                                    "null",
                                ],
                            },
                            "explanation": {
                                "type": "string",
                                "minLength": 1,
                            },
                        },
                    },
                },
                "gaps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": [
                            "title",
                            "description",
                            "cv_evidence",
                            "job_evidence",
                        ],
                        "properties": {
                            "title": {
                                "type": "string",
                                "minLength": 1,
                            },
                            "description": {
                                "type": "string",
                                "minLength": 1,
                            },
                            "cv_evidence": {
                                "type": [
                                    "string",
                                    "null",
                                ],
                            },
                            "job_evidence": {
                                "type": [
                                    "string",
                                    "null",
                                ],
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
        },
        "warnings": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
    },
}


def build_cv_job_matching_prompt(
    cv_extraction: Dict[str, Any],
    job_description: Union[str, Dict[str, Any]],
) -> str:
    """
    Build the user prompt for CV-to-job matching.

    The CV must be supplied as structured extracted information.
    The job description may be plain text or structured data.
    """

    if not isinstance(cv_extraction, dict):
        raise TypeError(
            "cv_extraction must be a dictionary."
        )

    if not isinstance(job_description, (str, dict)):
        raise TypeError(
            "job_description must be a string or dictionary."
        )

    if isinstance(job_description, str):
        job_content = job_description.strip()

        if not job_content:
            raise ValueError(
                "job_description cannot be empty."
            )
    else:
        job_content = job_description

    return (
        "STRUCTURED CV INFORMATION:\n"
        f"{cv_extraction}\n\n"
        "JOB DESCRIPTION:\n"
        f"{job_content}\n\n"
        "Compare the CV against the job description and return "
        "the structured CV-to-job matching result."
    )