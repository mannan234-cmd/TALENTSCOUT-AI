
from typing import Any, Dict, List

from app.models.professional_cv import ProfessionalCV


class ProfessionalCVService:

    @staticmethod
    def _dump(value):
        if hasattr(value, "model_dump"):
            return value.model_dump(mode="json")

        if isinstance(value, dict):
            return dict(value)

        return {}

    @staticmethod
    def _string_list(value, field_name=""):
        """
        Convert structured AI extraction lists into the
        List[str] contract required by ProfessionalCV.

        IMPORTANT:
        This operates on a copy/read value only.
        Original ai_extraction JSON is never modified.
        """

        if value is None:
            return []

        if not isinstance(value, list):
            value = [value]

        result = []
        seen = set()

        for item in value:

            # Already a string.
            if isinstance(item, str):
                text = item.strip()

            # Unexpected scalar.
            elif not isinstance(item, dict):
                text = str(item).strip()

            # Structured AI object.
            else:

                if field_name == "skills":

                    name = str(
                        item.get("name") or ""
                    ).strip()

                    category = str(
                        item.get("category") or ""
                    ).strip()

                    if name:
                        text = name
                    elif item.get("evidence"):
                        text = str(
                            item["evidence"]
                        ).strip()
                    else:
                        text = ""

                elif field_name == "certifications":

                    name = str(
                        item.get("name") or ""
                    ).strip()

                    organization = str(
                        item.get(
                            "issuing_organization"
                        )
                        or item.get(
                            "organization"
                        )
                        or ""
                    ).strip()

                    if name and organization:
                        text = (
                            f"{name} — "
                            f"{organization}"
                        )
                    elif name:
                        text = name
                    elif item.get("evidence"):
                        text = str(
                            item["evidence"]
                        ).strip()
                    else:
                        text = ""

                elif field_name == "achievements":

                    title = str(
                        item.get("title") or ""
                    ).strip()

                    description = str(
                        item.get("description") or ""
                    ).strip()

                    date = str(
                        item.get("date") or ""
                    ).strip()

                    if title and description:
                        text = (
                            f"{title} — "
                            f"{description}"
                        )
                    elif title:
                        text = title
                    elif description:
                        text = description
                    elif item.get("evidence"):
                        text = str(
                            item["evidence"]
                        ).strip()
                    else:
                        text = ""

                    # Date is deliberately not added
                    # to keep CV achievement strings clean.

                elif field_name == "languages":

                    name = str(
                        item.get("name")
                        or item.get("language")
                        or ""
                    ).strip()

                    proficiency = str(
                        item.get("proficiency")
                        or item.get("level")
                        or ""
                    ).strip()

                    if name and proficiency:
                        text = (
                            f"{name} — "
                            f"{proficiency}"
                        )
                    elif name:
                        text = name
                    else:
                        text = ""

                else:

                    text = str(
                        item.get("name")
                        or item.get("title")
                        or item.get("value")
                        or item.get("evidence")
                        or ""
                    ).strip()

            if not text:
                continue

            key = text.casefold()

            if key not in seen:
                seen.add(key)
                result.append(text)

        return result

    @classmethod
    def build(cls, improved_cv, extraction=None):

        data = cls._dump(improved_cv)
        source = cls._dump(extraction)

        contact = (
            source.get("contact")
            or source.get("personal_information")
            or source.get("personal_info")
            or {}
        )

        if not isinstance(contact, dict):
            contact = {}

        full_name = (
            contact.get("full_name")
            or contact.get("name")
            or source.get("full_name")
            or source.get("name")
            or ""
        )

        contact_parts = [
            str(contact[key]).strip()
            for key in (
                "email",
                "phone",
                "location",
            )
            if contact.get(key)
        ]

        # Normalize structured list fields.
        skills = cls._string_list(
            data.get("skills")
            or source.get("skills")
            or [],
            "skills",
        )

        certifications = cls._string_list(
            data.get("certifications")
            or source.get("certifications")
            or [],
            "certifications",
        )

        achievements = cls._string_list(
            data.get("achievements")
            or source.get("achievements")
            or [],
            "achievements",
        )

        languages = cls._string_list(
            data.get("languages")
            or source.get("languages")
            or [],
            "languages",
        )

        return ProfessionalCV(
            full_name=str(full_name),

            contact_line=" | ".join(
                contact_parts
            ),

            professional_summary=str(
                data.get("professional_summary")
                or data.get("summary")
                or source.get(
                    "professional_summary"
                )
                or source.get("summary")
                or ""
            ),

            experience=data.get(
                "experience"
            )
            or source.get("experience")
            or [],

            skills=skills,

            education=data.get(
                "education"
            )
            or source.get("education")
            or [],

            certifications=certifications,

            projects=data.get(
                "projects"
            )
            or source.get("projects")
            or [],

            achievements=achievements,

            languages=languages,

            warnings=data.get(
                "warnings"
            )
            or source.get("warnings")
            or [],
        )


professional_cv_service = (
    ProfessionalCVService()
)
