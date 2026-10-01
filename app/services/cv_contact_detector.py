
import re
from typing import List, Optional

from pydantic import BaseModel, Field


class CVContactDetectionError(Exception):
    """Raised when CV contact detection fails."""


class CVContactInfo(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    emails: List[str] = Field(default_factory=list)
    phone_numbers: List[str] = Field(default_factory=list)
    linkedin_urls: List[str] = Field(default_factory=list)
    github_urls: List[str] = Field(default_factory=list)
    locations: List[str] = Field(default_factory=list)


class CVContactDetectionResult(BaseModel):
    success: bool = True
    contact_information: CVContactInfo = Field(
        default_factory=CVContactInfo
    )
    detected_lines: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class CVContactDetector:
    """
    Deterministic detector for contact/header information
    commonly found near the beginning of a CV.

    This service does not use an LLM.
    """

    PAKISTANI_LANDLINE_PATTERN = re.compile(
        r"(?<!\d)"
        r"(?:\+92[\s.-]?)?"
        r"\(?0\d{2,3}\)?"
        r"[\s.-]?"
        r"\d{6,8}"
        r"(?!\d)"
    )

    EMAIL_PATTERN = re.compile(
        r"\b[A-Za-z0-9._%+-]+@"
        r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    )

    YEAR_RANGE_PATTERN = re.compile(
        r"(?<!\d)"
        r"(?:19|20)\d{2}"
        r"\s*[-–—]"
        r"\s*"
        r"(?:19|20)\d{2}"
        r"(?!\d)"
    )

    PHONE_PATTERN = re.compile(
        r"(?<!\d)"
        r"(?:\+?\d{1,3}[\s.-]?)?"
        r"(?:\(\d{2,4}\)[\s.-]?)?"
        r"(?:\d[\s.-]?){6,14}"
        r"\d"
        r"(?!\d)"
    )

    LINKEDIN_PATTERN = re.compile(
        r"(?:https?://)?"
        r"(?:www\.)?"
        r"linkedin\.com/"
        r"(?:in|pub)/[A-Za-z0-9._~:/?#@!$&'()*+,;=%-]+",
        re.IGNORECASE,
    )

    GITHUB_PATTERN = re.compile(
        r"(?:https?://)?"
        r"(?:www\.)?"
        r"github\.com/"
        r"[A-Za-z0-9._-]+",
        re.IGNORECASE,
    )

    LOCATION_HINTS = {
        "lahore",
        "karachi",
        "islamabad",
        "rawalpindi",
        "peshawar",
        "quetta",
        "multan",
        "faisalabad",
        "pakistan",
        "india",
        "united states",
        "usa",
        "united kingdom",
        "uk",
        "canada",
        "australia",
        "dubai",
        "uae",
    }

    TITLE_HINTS = {
        "developer",
        "engineer",
        "designer",
        "analyst",
        "student",
        "intern",
        "manager",
        "consultant",
        "scientist",
        "researcher",
        "specialist",
        "administrator",
        "architect",
        "developer",
    }

    MAX_HEADER_LINES = 15

    def detect(self, text: str) -> CVContactDetectionResult:
        if text is None:
            raise CVContactDetectionError(
                "CV text is required."
            )

        if not isinstance(text, str):
            raise CVContactDetectionError(
                "CV text must be a string."
            )

        cleaned_text = text.strip()

        if not cleaned_text:
            raise CVContactDetectionError(
                "CV text is empty."
            )

        try:
            lines = cleaned_text.splitlines()

            header_lines = self._get_header_lines(
                lines
            )

            emails = self._extract_unique(
                header_lines,
                self.EMAIL_PATTERN,
            )

            phones = self._extract_phone_numbers(
                header_lines
            )

            linkedin_urls = self._extract_unique(
                header_lines,
                self.LINKEDIN_PATTERN,
            )

            github_urls = self._extract_unique(
                header_lines,
                self.GITHUB_PATTERN,
            )

            locations = self._detect_locations(
                header_lines
            )

            name = self._detect_name(
                header_lines
            )

            title = self._detect_title(
                header_lines,
                name=name,
            )

            detected_lines = self._build_detected_lines(
                header_lines,
                emails,
                phones,
                linkedin_urls,
                github_urls,
                locations,
            )

            warnings = []

            if not emails:
                warnings.append(
                    "No email address detected in the CV header."
                )

            if not phones:
                warnings.append(
                    "No phone number detected in the CV header."
                )

            if not name:
                warnings.append(
                    "Candidate name could not be confidently "
                    "detected from the CV header."
                )

            contact_information = CVContactInfo(
                name=name,
                title=title,
                emails=emails,
                phone_numbers=phones,
                linkedin_urls=linkedin_urls,
                github_urls=github_urls,
                locations=locations,
            )

            return CVContactDetectionResult(
                success=True,
                contact_information=contact_information,
                detected_lines=detected_lines,
                warnings=warnings,
            )

        except CVContactDetectionError:
            raise

        except Exception as error:
            raise CVContactDetectionError(
                f"CV contact detection failed: {error}"
            ) from error

    def _get_header_lines(
        self,
        lines: List[str],
    ) -> List[str]:

        header_lines = []

        for line in lines[:self.MAX_HEADER_LINES]:

            cleaned = " ".join(
                line.strip().split()
            )

            if cleaned:
                header_lines.append(cleaned)

        return header_lines

    def _extract_unique(
        self,
        lines: List[str],
        pattern: re.Pattern,
    ) -> List[str]:

        results = []

        for line in lines:

            matches = pattern.findall(line)

            for match in matches:

                if isinstance(match, tuple):
                    value = "".join(match)
                else:
                    value = match

                value = value.strip()

                if value and value not in results:
                    results.append(value)

        return results

    def _extract_phone_numbers(
        self,
        lines: List[str],
    ) -> List[str]:

        results = []

        for line in lines:

            # ------------------------------------------------
            # Dedicated Pakistani landline detection
            # ------------------------------------------------

            landline_matches = (
                self.PAKISTANI_LANDLINE_PATTERN.findall(
                    line
                )
            )

            for match in landline_matches:

                value = match.strip()

                digits = re.sub(
                    r"\D",
                    "",
                    value,
                )

                if len(digits) < 7:
                    continue

                if len(digits) > 15:
                    continue

                if value not in results:
                    results.append(value)

            # ------------------------------------------------
            # Generic phone detection
            # ------------------------------------------------

            matches = self.PHONE_PATTERN.findall(
                line
            )

            for match in matches:

                value = match.strip()

                # ------------------------------------------------
                # Exclude academic/date year ranges such as:
                # 2021-2025
                # 2020 - 2024
                # 2019–2023
                #
                # These can otherwise match the generic phone
                # pattern because they contain 8 digits.
                # ------------------------------------------------

                if self.YEAR_RANGE_PATTERN.fullmatch(
                    value
                ):
                    continue

                digits = re.sub(
                    r"\D",
                    "",
                    value,
                )

                if len(digits) < 7:
                    continue

                if len(digits) > 15:
                    continue

                if value not in results:
                    results.append(value)

        return results

    def _detect_locations(
        self,
        lines: List[str],
    ) -> List[str]:

        results = []

        for line in lines:

            # ------------------------------------------------
            # Build candidate segments
            #
            # This supports:
            #
            # Lahore, Pakistan
            # Location: Lahore, Pakistan
            # Email | Phone | Lahore, Pakistan
            # Email • Phone • Lahore, Pakistan
            # ------------------------------------------------

            segments = [
                line
            ]

            for separator in ["|", "•", "·"]:

                expanded_segments = []

                for segment in segments:

                    expanded_segments.extend(
                        segment.split(separator)
                    )

                segments = expanded_segments

            for segment in segments:

                candidate = segment.strip()

                if not candidate:
                    continue

                # ------------------------------------------------
                # Remove common location labels
                # ------------------------------------------------

                cleaned_candidate = re.sub(
                    r"^(location|address|based in|based at)\s*[:\-]\s*",
                    "",
                    candidate,
                    flags=re.IGNORECASE,
                ).strip()

                if not cleaned_candidate:
                    continue

                # ------------------------------------------------
                # Ignore segments that are clearly contact data
                # ------------------------------------------------

                if self.EMAIL_PATTERN.search(
                    cleaned_candidate
                ):
                    continue

                if self.LINKEDIN_PATTERN.search(
                    cleaned_candidate
                ):
                    continue

                if self.GITHUB_PATTERN.search(
                    cleaned_candidate
                ):
                    continue

                # ------------------------------------------------
                # Ignore phone-only segments
                # ------------------------------------------------

                phone_matches = (
                    self.PAKISTANI_LANDLINE_PATTERN.findall(
                        cleaned_candidate
                    )
                )

                generic_phone_matches = (
                    self.PHONE_PATTERN.findall(
                        cleaned_candidate
                    )
                )

                if (
                    phone_matches
                    or generic_phone_matches
                ):
                    digits = re.sub(
                        r"\D",
                        "",
                        cleaned_candidate,
                    )

                    if (
                        len(digits) >= 7
                        and len(digits) <= 15
                    ):
                        continue

                # ------------------------------------------------
                # Existing location recognition
                # ------------------------------------------------

                if self._looks_like_location(
                    cleaned_candidate
                ):

                    value = cleaned_candidate

                    if value not in results:
                        results.append(value)

        return results

    def _looks_like_location(
        self,
        value: str,
    ) -> bool:

        if not value:
            return False

        candidate = " ".join(
            value.strip().split()
        )

        if not candidate:
            return False

        normalized = candidate.lower()

        # ------------------------------------------------
        # Remove common labels before checking hints
        # ------------------------------------------------

        normalized = re.sub(
            r"^(location|address|based in|based at)\s*[:\-]\s*",
            "",
            normalized,
            flags=re.IGNORECASE,
        ).strip()

        # ------------------------------------------------
        # A location should contain at least one known
        # geographic hint.
        # ------------------------------------------------

        matched_hints = []

        for hint in self.LOCATION_HINTS:

            if re.search(
                rf"(?<![a-z]){re.escape(hint)}(?![a-z])",
                normalized,
            ):
                matched_hints.append(hint)

        if not matched_hints:
            return False

        # ------------------------------------------------
        # Reject obvious contact-data values
        # ------------------------------------------------

        if self.EMAIL_PATTERN.search(
            candidate
        ):
            return False

        if self.LINKEDIN_PATTERN.search(
            candidate
        ):
            return False

        if self.GITHUB_PATTERN.search(
            candidate
        ):
            return False

        # ------------------------------------------------
        # Reject phone-only values
        # ------------------------------------------------

        phone_digits = re.sub(
            r"\D",
            "",
            candidate,
        )

        if (
            phone_digits
            and len(phone_digits) >= 7
            and len(phone_digits) <= 15
        ):

            stripped_for_phone = re.sub(
                r"[^0-9+()\-\.\s]",
                "",
                candidate,
            ).strip()

            if stripped_for_phone == candidate:
                return False

        return True

    def _detect_name(
        self,
        lines: List[str],
    ) -> Optional[str]:

        for line in lines[:5]:

            if self.EMAIL_PATTERN.search(line):
                continue

            if self.LINKEDIN_PATTERN.search(line):
                continue

            if self.GITHUB_PATTERN.search(line):
                continue

            if self.PHONE_PATTERN.search(line):
                continue

            if self._looks_like_location(line):
                continue

            words = line.split()

            if not 2 <= len(words) <= 5:
                continue

            cleaned_words = [
                re.sub(
                    r"[^A-Za-z'-]",
                    "",
                    word,
                )
                for word in words
            ]

            if not all(cleaned_words):
                continue

            if all(
                word[0].isupper()
                for word in cleaned_words
                if word
            ):
                return line

        return None

    def _detect_title(
        self,
        lines: List[str],
        name: Optional[str],
    ) -> Optional[str]:

        for line in lines[:6]:

            if name and line == name:
                continue

            normalized = line.lower()

            if self.EMAIL_PATTERN.search(line):
                continue

            if self.PHONE_PATTERN.search(line):
                continue

            if self.LINKEDIN_PATTERN.search(line):
                continue

            if self.GITHUB_PATTERN.search(line):
                continue

            if self._looks_like_location(line):
                continue

            if any(
                hint in normalized
                for hint in self.TITLE_HINTS
            ):
                return line

        return None

    def _build_detected_lines(
        self,
        header_lines: List[str],
        emails: List[str],
        phones: List[str],
        linkedin_urls: List[str],
        github_urls: List[str],
        locations: List[str],
    ) -> List[str]:

        detected = []

        patterns = [
            self.EMAIL_PATTERN,
            self.PHONE_PATTERN,
            self.LINKEDIN_PATTERN,
            self.GITHUB_PATTERN,
        ]

        for line in header_lines:

            is_detected = any(
                pattern.search(line)
                for pattern in patterns
            )

            if not is_detected:
                is_detected = (
                    line in locations
                )

            if is_detected and line not in detected:
                detected.append(line)

        return detected


cv_contact_detector = CVContactDetector()
