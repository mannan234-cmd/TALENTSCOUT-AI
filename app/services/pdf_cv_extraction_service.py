
from pathlib import Path
from typing import Union

from pypdf import PdfReader


class PDFCVExtractionService:
    """Extract text from CV PDF files."""

    @staticmethod
    def extract_text(pdf_source: Union[str, Path, bytes]) -> str:
        """
        Extract text from a PDF supplied as a path or raw bytes.

        Raises:
            ValueError: if the PDF cannot be read or contains no extractable text.
        """

        try:
            if isinstance(pdf_source, (str, Path)):
                reader = PdfReader(str(pdf_source))
            elif isinstance(pdf_source, bytes):
                import io
                reader = PdfReader(io.BytesIO(pdf_source))
            else:
                raise ValueError("Unsupported PDF source type.")

            pages = []

            for page in reader.pages:
                text = page.extract_text() or ""
                if text.strip():
                    pages.append(text.strip())

            extracted_text = "\n\n".join(pages).strip()

            if not extracted_text:
                raise ValueError(
                    "No extractable text was found in the PDF. "
                    "The CV may be image/scanned-only."
                )

            return extracted_text

        except ValueError:
            raise
        except Exception as exc:
            raise ValueError(
                f"Unable to extract text from PDF: {exc}"
            ) from exc
