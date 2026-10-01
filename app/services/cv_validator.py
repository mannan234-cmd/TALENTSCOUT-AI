
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
import zipfile


class CVValidationError(Exception):
    """Raised when an uploaded CV fails validation."""


@dataclass
class CVValidationResult:
    is_valid: bool
    file_type: Optional[str] = None
    mime_type: Optional[str] = None
    file_size_bytes: int = 0
    message: str = ""


class CVValidator:
    """
    Validates uploaded CV files before storage.

    Supported formats:
    - PDF
    - DOCX

    Maximum file size:
    - 5 MB
    """

    MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024

    ALLOWED_EXTENSIONS = {
        ".pdf": "PDF",
        ".docx": "DOCX",
    }

    ALLOWED_MIME_TYPES = {
        ".pdf": {
            "application/pdf",
        },
        ".docx": {
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/zip",
        },
    }

    def validate(
        self,
        file_name: str,
        file_bytes: bytes,
        mime_type: Optional[str] = None,
    ) -> CVValidationResult:

        if not file_name or not file_name.strip():
            return CVValidationResult(
                is_valid=False,
                message="CV filename is required.",
            )

        file_name = file_name.strip()
        extension = Path(file_name).suffix.lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            return CVValidationResult(
                is_valid=False,
                mime_type=mime_type,
                message=(
                    "Unsupported CV format. "
                    "Only PDF and DOCX files are allowed."
                ),
            )

        file_type = self.ALLOWED_EXTENSIONS[extension]

        if not file_bytes:
            return CVValidationResult(
                is_valid=False,
                file_type=file_type,
                mime_type=mime_type,
                file_size_bytes=0,
                message="The uploaded CV file is empty.",
            )

        file_size = len(file_bytes)

        if file_size > self.MAX_FILE_SIZE_BYTES:
            max_size_mb = self.MAX_FILE_SIZE_BYTES / (1024 * 1024)

            return CVValidationResult(
                is_valid=False,
                file_type=file_type,
                mime_type=mime_type,
                file_size_bytes=file_size,
                message=(
                    f"CV file is too large. "
                    f"Maximum allowed size is "
                    f"{max_size_mb:g} MB."
                ),
            )

        if mime_type:
            allowed_mimes = self.ALLOWED_MIME_TYPES[extension]

            if mime_type not in allowed_mimes:
                return CVValidationResult(
                    is_valid=False,
                    file_type=file_type,
                    mime_type=mime_type,
                    file_size_bytes=file_size,
                    message=(
                        f"File type mismatch. "
                        f"The selected extension {extension} "
                        f"does not match MIME type "
                        f"{mime_type}."
                    ),
                )

        if extension == ".pdf":
            return self._validate_pdf(
                file_bytes=file_bytes,
                file_type=file_type,
                mime_type=mime_type,
                file_size=file_size,
            )

        if extension == ".docx":
            return self._validate_docx(
                file_bytes=file_bytes,
                file_type=file_type,
                mime_type=mime_type,
                file_size=file_size,
            )

        return CVValidationResult(
            is_valid=False,
            message="Unable to validate CV file.",
        )

    def _validate_pdf(
        self,
        file_bytes: bytes,
        file_type: str,
        mime_type: Optional[str],
        file_size: int,
    ) -> CVValidationResult:

        if not file_bytes.startswith(b"%PDF-"):
            return CVValidationResult(
                is_valid=False,
                file_type=file_type,
                mime_type=mime_type,
                file_size_bytes=file_size,
                message=(
                    "The file has a PDF extension but does "
                    "not contain a valid PDF signature."
                ),
            )

        return CVValidationResult(
            is_valid=True,
            file_type=file_type,
            mime_type=mime_type,
            file_size_bytes=file_size,
            message="PDF CV validation successful.",
        )

    def _validate_docx(
        self,
        file_bytes: bytes,
        file_type: str,
        mime_type: Optional[str],
        file_size: int,
    ) -> CVValidationResult:

        if not file_bytes.startswith(b"PK"):
            return CVValidationResult(
                is_valid=False,
                file_type=file_type,
                mime_type=mime_type,
                file_size_bytes=file_size,
                message=(
                    "The file has a DOCX extension but "
                    "does not contain a valid Office document "
                    "signature."
                ),
            )

        try:
            from io import BytesIO

            with zipfile.ZipFile(
                BytesIO(file_bytes),
                "r",
            ) as archive:

                names = set(archive.namelist())

                required_files = {
                    "[Content_Types].xml",
                    "word/document.xml",
                }

                missing_files = required_files - names

                if missing_files:
                    return CVValidationResult(
                        is_valid=False,
                        file_type=file_type,
                        mime_type=mime_type,
                        file_size_bytes=file_size,
                        message=(
                            "The file has a DOCX extension but "
                            "does not contain the required "
                            "Word document structure."
                        ),
                    )

        except (zipfile.BadZipFile, OSError):
            return CVValidationResult(
                is_valid=False,
                file_type=file_type,
                mime_type=mime_type,
                file_size_bytes=file_size,
                message=(
                    "The uploaded DOCX file is corrupted "
                    "or is not a valid Office document."
                ),
            )

        return CVValidationResult(
            is_valid=True,
            file_type=file_type,
            mime_type=mime_type,
            file_size_bytes=file_size,
            message="DOCX CV validation successful.",
        )


cv_validator = CVValidator()
