
from typing import Optional

from app.models.cv_contact_integration import (
    CVIntegratedContactResult,
)
from app.services.cv_contact_detector import (
    CVContactDetector,
)
from app.services.cv_structure_detector import (
    CVStructureDetector,
)


class CVContactIntegrationError(Exception):
    """Raised when CV contact integration fails."""


class CVContactIntegrationService:
    """
    Integrates deterministic CV structure detection
    with deterministic contact information detection.

    No AI/API/database operations are performed here.
    """

    def __init__(
        self,
        contact_detector: Optional[CVContactDetector] = None,
        structure_detector: Optional[CVStructureDetector] = None,
    ):
        self.contact_detector = (
            contact_detector
            or CVContactDetector()
        )

        self.structure_detector = (
            structure_detector
            or CVStructureDetector()
        )

    def analyze(
        self,
        text: str,
    ) -> CVIntegratedContactResult:
        """
        Detect CV structure and contact information,
        then combine both results.
        """

        if not isinstance(text, str):
            raise CVContactIntegrationError(
                "CV text must be a string."
            )

        if not text.strip():
            raise CVContactIntegrationError(
                "CV text cannot be empty."
            )

        try:

            # ------------------------------------------------
            # Structure detection
            # ------------------------------------------------

            structure_result = (
                self.structure_detector.detect(text)
            )

            # ------------------------------------------------
            # Contact detection
            # ------------------------------------------------

            contact_result = (
                self.contact_detector.detect(text)
            )

            # ------------------------------------------------
            # Combine warnings
            # ------------------------------------------------

            warnings = []

            warnings.extend(
                structure_result.warnings
            )

            warnings.extend(
                contact_result.warnings
            )

            # ------------------------------------------------
            # Remove duplicate warnings while preserving order
            # ------------------------------------------------

            unique_warnings = []

            for warning in warnings:

                if warning not in unique_warnings:
                    unique_warnings.append(warning)

            # ------------------------------------------------
            # Combine detected lines
            # ------------------------------------------------

            detected_lines = []

            for line in contact_result.detected_lines:

                if line not in detected_lines:
                    detected_lines.append(line)

            # ------------------------------------------------
            # Final integrated result
            # ------------------------------------------------

            return CVIntegratedContactResult(
                success=(
                    structure_result.success
                    and contact_result.success
                ),
                structure=(
                    structure_result.structure
                ),
                contact_information=(
                    contact_result.contact_information
                ),
                detected_lines=detected_lines,
                warnings=unique_warnings,
            )

        except CVContactIntegrationError:
            raise

        except Exception as exc:

            raise CVContactIntegrationError(
                f"CV contact integration failed: {exc}"
            ) from exc
