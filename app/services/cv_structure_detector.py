
import re
from typing import Dict, List, Optional, Tuple

from app.models.cv_structure import (
    CVSection,
    CVStructure,
    CVStructureResult,
)


class CVStructureDetectionError(Exception):
    """
    Raised when CV structure detection fails.
    """


class CVStructureDetector:
    """
    Deterministic CV section detector.

    This detector does not use an LLM.

    It identifies common CV section headings,
    determines section boundaries, and preserves
    the original heading and section content.
    """

    SECTION_ALIASES: Dict[str, List[str]] = {

        "contact_information": [
            "contact",
            "contact information",
            "personal information",
            "personal details",
            "contact details",
        ],

        "summary": [
            "summary",
            "professional summary",
            "profile",
            "professional profile",
            "career summary",
            "career objective",
            "objective",
            "professional objective",
            "about me",
        ],

        "skills": [
            "skills",
            "technical skills",
            "core skills",
            "key skills",
            "technical expertise",
            "core competencies",
            "competencies",
            "areas of expertise",
            "skills & expertise",
            "skills and expertise",
        ],

        "experience": [
            "experience",
            "work experience",
            "professional experience",
            "employment history",
            "work history",
            "career history",
            "internship",
            "internships",
            "internship experience",
            "professional experience",
        ],

        "education": [
            "education",
            "educational background",
            "academic background",
            "academic qualifications",
            "qualifications",
            "education & qualifications",
            "education and qualifications",
        ],

        "projects": [
            "projects",
            "personal projects",
            "academic projects",
            "academic projects",
            "selected projects",
            "key projects",
            "project experience",
        ],

        "certifications": [
            "certifications",
            "certificates",
            "professional certifications",
            "licenses & certifications",
            "licenses and certifications",
        ],

        "achievements": [
            "achievements",
            "accomplishments",
            "awards",
            "honors",
            "honours",
            "awards & achievements",
            "awards and achievements",
        ],

        "languages": [
            "languages",
            "language skills",
            "language proficiency",
        ],

        "interests": [
            "interests",
            "hobbies",
            "hobbies & interests",
            "hobbies and interests",
        ],

        "references": [
            "references",
            "professional references",
        ],
    }

    def __init__(self):
        self._normalized_aliases = (
            self._build_normalized_aliases()
        )

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------

    def detect(
        self,
        text: str,
    ) -> CVStructureResult:

        if text is None:
            raise CVStructureDetectionError(
                "CV text is required."
            )

        if not isinstance(text, str):
            raise CVStructureDetectionError(
                "CV text must be a string."
            )

        cleaned_text = text.strip()

        if not cleaned_text:
            raise CVStructureDetectionError(
                "CV text is empty."
            )

        try:

            lines = cleaned_text.splitlines()

            sections, warnings = (
                self._detect_sections(lines)
            )

            structure = (
                self._build_structure(
                    sections
                )
            )

            return CVStructureResult(
                success=True,
                structure=structure,
                warnings=warnings,
            )

        except CVStructureDetectionError:
            raise

        except Exception as error:
            raise CVStructureDetectionError(
                f"CV structure detection failed: {error}"
            ) from error

    # --------------------------------------------------------
    # Heading normalization
    # --------------------------------------------------------

    def normalize_heading(
        self,
        heading: str,
    ) -> str:

        if not heading:
            return ""

        normalized = heading.strip().lower()

        normalized = (
            normalized
            .replace("&", " and ")
        )

        normalized = re.sub(
            r"[^a-z0-9\s]",
            " ",
            normalized,
        )

        normalized = re.sub(
            r"\s+",
            " ",
            normalized,
        )

        return normalized.strip()

    # --------------------------------------------------------
    # Section detection
    # --------------------------------------------------------

    def _detect_sections(
        self,
        lines: List[str],
    ) -> Tuple[
        List[CVSection],
        List[str],
    ]:

        detected_headings = []

        warnings = []

        for index, line in enumerate(lines):

            if not line.strip():
                continue

            section_type = (
                self._classify_heading(line)
            )

            if section_type:

                detected_headings.append(
                    (
                        index,
                        line.strip(),
                        section_type,
                    )
                )

        if not detected_headings:

            warnings.append(
                "No recognized CV section headings were detected."
            )

            return [], warnings

        sections = []

        for position, (
            start_line,
            heading,
            section_type,
        ) in enumerate(detected_headings):

            if position + 1 < len(
                detected_headings
            ):

                next_start_line = (
                    detected_headings[
                        position + 1
                    ][0]
                )

                end_line = (
                    next_start_line - 1
                )

            else:

                end_line = (
                    len(lines) - 1
                )

            content_lines = lines[
                start_line + 1:
                end_line + 1
            ]

            content = self._clean_content(
                content_lines
            )

            sections.append(
                CVSection(
                    section_type=section_type,
                    heading=heading,
                    content=content,
                    start_line=start_line,
                    end_line=end_line,
                )
            )

        return sections, warnings

    # --------------------------------------------------------
    # Heading classification
    # --------------------------------------------------------

    def _classify_heading(
        self,
        line: str,
    ) -> Optional[str]:

        if not self._looks_like_heading(
            line
        ):
            return None

        normalized = (
            self.normalize_heading(line)
        )

        if not normalized:
            return None

        return self._normalized_aliases.get(
            normalized
        )

    # --------------------------------------------------------
    # Heading heuristics
    # --------------------------------------------------------

    def _looks_like_heading(
        self,
        line: str,
    ) -> bool:

        value = line.strip()

        if not value:
            return False

        if len(value) > 80:
            return False

        normalized = (
            self.normalize_heading(value)
        )

        if not normalized:
            return False

        # Exact known heading
        if normalized in self._normalized_aliases:
            return True

        # Common visual heading patterns
        if value.isupper():
            return True

        # Title-case short heading
        words = value.split()

        if (
            1 <= len(words) <= 6
            and all(
                self._is_reasonable_heading_word(
                    word
                )
                for word in words
            )
        ):
            return True

        return False

    def _is_reasonable_heading_word(
        self,
        word: str,
    ) -> bool:

        cleaned = re.sub(
            r"[^A-Za-z0-9]",
            "",
            word,
        )

        if not cleaned:
            return False

        return (
            cleaned[0].isupper()
            or cleaned.isupper()
        )

    # --------------------------------------------------------
    # Content cleanup
    # --------------------------------------------------------

    def _clean_content(
        self,
        lines: List[str],
    ) -> str:

        cleaned_lines = []

        for line in lines:

            cleaned = (
                " ".join(
                    line.strip().split()
                )
            )

            if cleaned:
                cleaned_lines.append(
                    cleaned
                )

        return "\n".join(
            cleaned_lines
        )

    # --------------------------------------------------------
    # Build final structure
    # --------------------------------------------------------

    def _build_structure(
        self,
        sections: List[CVSection],
    ) -> CVStructure:

        return CVStructure(
            sections=sections,
            total_sections=len(sections),
            has_contact_information=(
                self._has_section(
                    sections,
                    "contact_information",
                )
            ),
            has_summary=(
                self._has_section(
                    sections,
                    "summary",
                )
            ),
            has_skills=(
                self._has_section(
                    sections,
                    "skills",
                )
            ),
            has_experience=(
                self._has_section(
                    sections,
                    "experience",
                )
            ),
            has_education=(
                self._has_section(
                    sections,
                    "education",
                )
            ),
            has_projects=(
                self._has_section(
                    sections,
                    "projects",
                )
            ),
            has_certifications=(
                self._has_section(
                    sections,
                    "certifications",
                )
            ),
            has_achievements=(
                self._has_section(
                    sections,
                    "achievements",
                )
            ),
        )

    def _has_section(
        self,
        sections: List[CVSection],
        section_type: str,
    ) -> bool:

        return any(
            section.section_type
            == section_type
            for section in sections
        )

    # --------------------------------------------------------
    # Alias preparation
    # --------------------------------------------------------

    def _build_normalized_aliases(
        self,
    ) -> Dict[str, str]:

        aliases = {}

        for section_type, headings in (
            self.SECTION_ALIASES.items()
        ):

            for heading in headings:

                normalized = (
                    self.normalize_heading(
                        heading
                    )
                )

                aliases[normalized] = (
                    section_type
                )

        return aliases


cv_structure_detector = (
    CVStructureDetector()
)
