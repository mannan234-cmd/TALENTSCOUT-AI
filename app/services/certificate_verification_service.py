from datetime import date
from typing import Any, Dict, Optional
from uuid import UUID

from app.models.certificate_verification import (
    CertificateVerification
)


class CertificateVerificationService:
    """
    Evidence-based certificate verification service.

    Comparisons are deterministic and based only on
    available certificate, profile, and extracted data.

    AI extraction alone does not establish authenticity.
    """

    VALID_STATUSES = {
        "Not Verified",
        "AI Review",
        "Verified",
        "Needs Review"
    }

    MATCH = "MATCH"
    MISMATCH = "MISMATCH"
    NOT_AVAILABLE = "NOT AVAILABLE"

    @staticmethod
    def normalize_text(
        value: Optional[str]
    ) -> Optional[str]:
        """
        Normalize text for comparison.
        """
        if value is None:
            return None

        normalized = " ".join(
            str(value)
            .strip()
            .lower()
            .split()
        )

        return normalized or None

    @classmethod
    def compare_text(
        cls,
        first: Optional[str],
        second: Optional[str]
    ) -> Optional[bool]:
        """
        Compare two text values.

        True  = MATCH
        False = MISMATCH
        None  = NOT AVAILABLE
        """
        first_normalized = cls.normalize_text(first)
        second_normalized = cls.normalize_text(second)

        if not first_normalized or not second_normalized:
            return None

        return (
            first_normalized ==
            second_normalized
        )

    @staticmethod
    def compare_dates(
        first: Optional[Any],
        second: Optional[Any]
    ) -> Optional[bool]:
        """
        Compare two dates.

        True  = MATCH
        False = MISMATCH
        None  = NOT AVAILABLE
        """
        if first is None or second is None:
            return None

        try:
            if isinstance(first, str):
                first = date.fromisoformat(first)

            if isinstance(second, str):
                second = date.fromisoformat(second)

            return first == second

        except (TypeError, ValueError):
            return None

    @classmethod
    def result_from_match(
        cls,
        match: Optional[bool]
    ) -> str:
        """
        Convert a boolean comparison into a
        human-readable comparison result.
        """
        if match is True:
            return cls.MATCH

        if match is False:
            return cls.MISMATCH

        return cls.NOT_AVAILABLE

    @staticmethod
    def _add_evidence(
        evidence_points: list,
        message: str
    ) -> None:
        """
        Add an evidence point without duplication.
        """
        if message not in evidence_points:
            evidence_points.append(message)

    @staticmethod
    def _add_review_flag(
        review_flags: list,
        message: str
    ) -> None:
        """
        Add a review flag without duplication.
        """
        if message not in review_flags:
            review_flags.append(message)

    def verify_certificate(
        self,
        certificate: Dict[str, Any],
        profile: Dict[str, Any],
        extracted_data: Dict[str, Any]
    ) -> CertificateVerification:
        """
        Evaluate available certificate evidence.

        Parameters
        ----------
        certificate:
            Stored certificate database record.

        profile:
            Stored student profile record.

        extracted_data:
            AI-extracted certificate information.

        Returns
        -------
        CertificateVerification
            Structured evidence comparison result.
        """

        certificate_id = UUID(
            str(certificate["id"])
        )

        profile_id = UUID(
            str(certificate["profile_id"])
        )

        evidence_points = []
        review_flags = []

        # --------------------------------------------------
        # Original certificate image
        # --------------------------------------------------

        original_image_available = bool(
            certificate.get(
                "certificate_file_path"
            )
        )

        if original_image_available:
            self._add_evidence(
                evidence_points,
                "Original certificate image is available."
            )
        else:
            self._add_review_flag(
                review_flags,
                "Original certificate image is not available."
            )

        # --------------------------------------------------
        # Holder name
        # --------------------------------------------------

        holder_name_match = self.compare_text(
            extracted_data.get(
                "certificate_holder_name"
            ),
            profile.get("full_name")
        )

        holder_name_result = (
            self.result_from_match(
                holder_name_match
            )
        )

        if holder_name_result == self.MATCH:
            self._add_evidence(
                evidence_points,
                "Certificate holder name matches the student profile."
            )

        elif holder_name_result == self.MISMATCH:
            self._add_review_flag(
                review_flags,
                "Certificate holder name does not match the student profile."
            )

        # --------------------------------------------------
        # Certificate name
        # --------------------------------------------------

        certificate_name_match = self.compare_text(
            extracted_data.get(
                "certificate_name"
            ),
            certificate.get(
                "certificate_name"
            )
        )

        certificate_name_result = (
            self.result_from_match(
                certificate_name_match
            )
        )

        if certificate_name_result == self.MATCH:
            self._add_evidence(
                evidence_points,
                "Extracted certificate name matches stored certificate information."
            )

        elif certificate_name_result == self.MISMATCH:
            self._add_review_flag(
                review_flags,
                "Extracted certificate name differs from stored certificate information."
            )

        # --------------------------------------------------
        # Course name
        # --------------------------------------------------

        course_name_match = self.compare_text(
            extracted_data.get(
                "course_name"
            ),
            certificate.get(
                "course_name"
            )
        )

        course_name_result = (
            self.result_from_match(
                course_name_match
            )
        )

        if course_name_result == self.MATCH:
            self._add_evidence(
                evidence_points,
                "Extracted course name matches stored course information."
            )

        elif course_name_result == self.MISMATCH:
            self._add_review_flag(
                review_flags,
                "Extracted course name differs from stored course information."
            )

        # --------------------------------------------------
        # Issuing organization
        # --------------------------------------------------

        issuer_match = self.compare_text(
            extracted_data.get(
                "issuing_organization"
            ),
            certificate.get(
                "issuing_organization"
            )
        )

        issuer_result = (
            self.result_from_match(
                issuer_match
            )
        )

        if issuer_result == self.MATCH:
            self._add_evidence(
                evidence_points,
                "Extracted issuing organization matches stored issuer information."
            )

        elif issuer_result == self.MISMATCH:
            self._add_review_flag(
                review_flags,
                "Extracted issuing organization differs from stored issuer information."
            )

        # --------------------------------------------------
        # Issue date
        # --------------------------------------------------

        issue_date_match = self.compare_dates(
            extracted_data.get(
                "issue_date"
            ),
            certificate.get(
                "issue_date"
            )
        )

        issue_date_result = (
            self.result_from_match(
                issue_date_match
            )
        )

        if issue_date_result == self.MATCH:
            self._add_evidence(
                evidence_points,
                "Extracted issue date matches the stored issue date."
            )

        elif issue_date_result == self.MISMATCH:
            self._add_review_flag(
                review_flags,
                "Extracted issue date differs from the stored issue date."
            )

        # --------------------------------------------------
        # Credential ID
        # --------------------------------------------------

        credential_id_present = bool(
            extracted_data.get(
                "credential_id"
            )
        )

        if credential_id_present:
            self._add_evidence(
                evidence_points,
                "A credential ID is visible in the extracted certificate information."
            )

        # Missing credential ID is not treated as a conflict.

        # --------------------------------------------------
        # Credential URL
        # --------------------------------------------------

        credential_url_present = bool(
            extracted_data.get(
                "credential_url"
            )
        )

        if credential_url_present:
            self._add_evidence(
                evidence_points,
                "A credential or verification URL is visible in the extracted certificate information."
            )

        # Missing credential URL is not treated as a conflict.

        # --------------------------------------------------
        # Determine overall status
        # --------------------------------------------------

        comparison_results = [
            holder_name_result,
            certificate_name_result,
            course_name_result,
            issuer_result,
            issue_date_result
        ]

        has_mismatch = (
            self.MISMATCH
            in comparison_results
        )

        available_matches = sum(
            result == self.MATCH
            for result in comparison_results
        )

        all_available_comparisons_match = (
            available_matches > 0
            and not has_mismatch
        )

        if has_mismatch:
            verification_status = "Needs Review"

        elif (
            original_image_available
            and all_available_comparisons_match
        ):
            verification_status = "AI Review"

        elif original_image_available:
            verification_status = "AI Review"

        else:
            verification_status = "Not Verified"

        # --------------------------------------------------
        # Verification notes
        # --------------------------------------------------

        if verification_status == "Needs Review":
            verification_notes = (
                "One or more available evidence fields "
                "conflict with stored certificate or "
                "profile information. Human review is "
                "required."
            )

        elif verification_status == "AI Review":
            verification_notes = (
                "Available certificate evidence is "
                "consistent where comparisons were possible. "
                "This is an AI-assisted evidence review and "
                "does not independently prove certificate "
                "authenticity."
            )

        else:
            verification_notes = (
                "Insufficient evidence is currently "
                "available for an evidence-based review."
            )

        return CertificateVerification(
            certificate_id=certificate_id,
            profile_id=profile_id,
            verification_status=verification_status,

            holder_name_match=holder_name_match,
            holder_name_result=holder_name_result,

            certificate_name_match=certificate_name_match,
            certificate_name_result=certificate_name_result,

            course_name_match=course_name_match,
            course_name_result=course_name_result,

            issuer_match=issuer_match,
            issuer_result=issuer_result,

            issue_date_match=issue_date_match,
            issue_date_result=issue_date_result,

            credential_id_present=credential_id_present,
            credential_url_present=credential_url_present,
            original_image_available=original_image_available,

            evidence_points=evidence_points,
            review_flags=review_flags,
            verification_notes=verification_notes
        )


certificate_verification_service = (
    CertificateVerificationService()
)
