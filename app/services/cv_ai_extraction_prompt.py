
from typing import Any, Dict


CV_AI_EXTRACTION_SYSTEM_PROMPT = """
You are the CV Intelligence extraction engine for TalentScout AI.

Your task is to extract structured information from the supplied CV text.

STRICT GROUNDING RULES:
1. Use ONLY information explicitly supported by the supplied CV text.
2. NEVER invent, infer, assume, or complete missing information.
3. If information is missing, return null for optional scalar fields
   or an empty list for collection fields.
4. Preserve the meaning of the original CV.
5. Do not rewrite, improve, exaggerate, or optimize the candidate's claims.
6. Do not create achievements, metrics, employers, job titles, degrees,
   projects, certifications, skills, dates, or technologies that are not
   supported by the CV.
7. Do not convert an implied possibility into a factual claim.
8. If a field is ambiguous, leave it null rather than guessing.
9. Keep extracted dates as they appear in the CV whenever practical.
10. Every extracted item should include concise evidence copied or closely
    grounded from the relevant CV text when an evidence field exists.
11. Evidence must support the extracted value. Do not create evidence.
12. Do not use outside knowledge to fill gaps.
13. Do not treat the CV filename as evidence unless the same information
    is also present in the CV text.
14. Do not treat formatting, section position, or document metadata alone
    as proof of a candidate fact.
15. Return JSON only according to the supplied schema.
"""


CV_AI_EXTRACTION_USER_PROMPT = """
Extract structured candidate information from the CV text below.

Return ONLY a JSON object matching the required schema.

CV TEXT:
--------------------
{cv_text}
--------------------

EXTRACTION REQUIREMENTS:

- full_name:
  Extract only when the candidate's name is supported by the CV.

- professional_title:
  Extract an explicitly stated professional/job title.
  Do not invent a title from the candidate's skills.

- professional_summary:
  Extract the candidate's stated summary/objective/profile.
  Do not generate a new summary.

- skills:
  Extract explicitly stated skills.
  Preserve recognizable skill names.
  Do not infer skills merely because a project or job might normally use them.
  Include evidence where possible.

- education:
  Extract explicitly stated educational qualifications.
  Preserve institution, degree, field, dates, and grade only when supported.

- experience:
  Extract explicitly stated employment, internship, volunteer,
  freelance, or other professional experience when clearly presented
  as experience.
  Do not convert a project into employment.
  Do not invent employer names, titles, dates, or responsibilities.

- projects:
  Extract explicitly stated projects.
  Include technologies only when the CV supports them.
  Do not infer technologies from project descriptions.

- certifications:
  Extract explicitly stated certifications.
  Do not treat ordinary courses, workshops, or skills as certifications
  unless the CV explicitly presents them as such.

- achievements:
  Extract explicitly stated awards, recognitions, accomplishments,
  competitions, honors, or similar achievements.
  Do not invent impact or importance.

- languages:
  Extract explicitly stated languages and proficiency when provided.

- interests:
  Extract explicitly stated interests/hobbies only.
  Do not infer interests from projects, skills, or career goals.

- warnings:
  Add concise warnings only when the CV contains ambiguity,
  incomplete information, or extraction concerns.
  Do not use warnings to invent missing facts.

GROUNDING:
For extracted fields containing evidence, the evidence should identify
the relevant wording or passage from the supplied CV text.

If the CV does not support a value, leave it null or omit it from the
collection rather than guessing.
"""


CV_AI_EXTRACTION_JSON_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "full_name": {
            "type": ["string", "null"]
        },
        "professional_title": {
            "type": ["string", "null"]
        },
        "professional_summary": {
            "type": ["string", "null"]
        },
        "skills": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "category": {
                        "type": ["string", "null"]
                    },
                    "evidence": {
                        "type": ["string", "null"]
                    }
                },
                "required": [
                    "name",
                    "category",
                    "evidence"
                ]
            }
        },
        "education": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "institution": {
                        "type": ["string", "null"]
                    },
                    "degree": {
                        "type": ["string", "null"]
                    },
                    "field_of_study": {
                        "type": ["string", "null"]
                    },
                    "start_date": {
                        "type": ["string", "null"]
                    },
                    "end_date": {
                        "type": ["string", "null"]
                    },
                    "grade": {
                        "type": ["string", "null"]
                    },
                    "evidence": {
                        "type": ["string", "null"]
                    }
                },
                "required": [
                    "institution",
                    "degree",
                    "field_of_study",
                    "start_date",
                    "end_date",
                    "grade",
                    "evidence"
                ]
            }
        },
        "experience": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "employer": {
                        "type": ["string", "null"]
                    },
                    "job_title": {
                        "type": ["string", "null"]
                    },
                    "start_date": {
                        "type": ["string", "null"]
                    },
                    "end_date": {
                        "type": ["string", "null"]
                    },
                    "location": {
                        "type": ["string", "null"]
                    },
                    "description": {
                        "type": ["string", "null"]
                    },
                    "evidence": {
                        "type": ["string", "null"]
                    }
                },
                "required": [
                    "employer",
                    "job_title",
                    "start_date",
                    "end_date",
                    "location",
                    "description",
                    "evidence"
                ]
            }
        },
        "projects": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "description": {
                        "type": ["string", "null"]
                    },
                    "technologies": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "role": {
                        "type": ["string", "null"]
                    },
                    "evidence": {
                        "type": ["string", "null"]
                    }
                },
                "required": [
                    "name",
                    "description",
                    "technologies",
                    "role",
                    "evidence"
                ]
            }
        },
        "certifications": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "issuing_organization": {
                        "type": ["string", "null"]
                    },
                    "issue_date": {
                        "type": ["string", "null"]
                    },
                    "expiry_date": {
                        "type": ["string", "null"]
                    },
                    "credential_id": {
                        "type": ["string", "null"]
                    },
                    "evidence": {
                        "type": ["string", "null"]
                    }
                },
                "required": [
                    "name",
                    "issuing_organization",
                    "issue_date",
                    "expiry_date",
                    "credential_id",
                    "evidence"
                ]
            }
        },
        "achievements": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "title": {
                        "type": "string"
                    },
                    "description": {
                        "type": ["string", "null"]
                    },
                    "date": {
                        "type": ["string", "null"]
                    },
                    "evidence": {
                        "type": ["string", "null"]
                    }
                },
                "required": [
                    "title",
                    "description",
                    "date",
                    "evidence"
                ]
            }
        },
        "languages": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "proficiency": {
                        "type": ["string", "null"]
                    },
                    "evidence": {
                        "type": ["string", "null"]
                    }
                },
                "required": [
                    "name",
                    "proficiency",
                    "evidence"
                ]
            }
        },
        "interests": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "warnings": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    },
    "required": [
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
        "warnings"
    ]
}


def build_cv_ai_extraction_prompt(cv_text: str) -> str:
    """
    Build the user prompt used for CV extraction.

    Validation is intentionally strict here so the extraction layer
    never sends an empty CV to the model.
    """
    if not isinstance(cv_text, str):
        raise TypeError("cv_text must be a string")

    cleaned_text = cv_text.strip()

    if not cleaned_text:
        raise ValueError("cv_text cannot be empty")

    return CV_AI_EXTRACTION_USER_PROMPT.format(cv_text=cleaned_text)
