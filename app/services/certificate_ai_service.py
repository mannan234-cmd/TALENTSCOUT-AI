import base64
import json

from groq import Groq

from app.config.settings import settings


class CertificateAIService:
    """
    AI service responsible for extracting structured
    information from certificate images.
    """

    VISION_MODEL = "qwen/qwen3.8-27b"

    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(
            api_key=settings.GROQ_API_KEY
        )

    @staticmethod
    def encode_image(
        image_bytes: bytes
    ) -> str:
        """
        Convert image bytes to base64.
        """
        return base64.b64encode(
            image_bytes
        ).decode("utf-8")

    def extract_certificate_information(
        self,
        image_bytes: bytes,
        content_type: str
    ) -> dict:
        """
        Analyze a certificate image and extract
        structured certificate information.
        """

        if not image_bytes:
            raise ValueError(
                "Certificate image is empty."
            )

        if not content_type:
            raise ValueError(
                "Certificate image content type is required."
            )

        encoded_image = self.encode_image(
            image_bytes
        )

        prompt = """
You are an AI certificate information extraction
assistant.

Analyze the uploaded certificate image carefully.

Extract ONLY information that is visibly supported
by the certificate image.

Do not invent, guess, infer, or complete missing
information from general knowledge.

Return a JSON object with exactly these fields:

{
    "certificate_name": null,
    "course_name": null,
    "issuing_organization": null,
    "issue_date": null,
    "expiration_date": null,
    "credential_id": null,
    "credential_url": null,
    "certificate_holder_name": null,
    "extraction_notes": null
}

Rules:

1. certificate_name:
   Extract the certificate, award, completion,
   achievement, or credential title.

   Examples:
   - "Certificate of Completion"
   - "Professional Certificate"
   - "Certificate of Achievement"

2. course_name:
   Extract the name of the course, training,
   program, class, or learning activity associated
   with the certificate.

   IMPORTANT:
   Keep this separate from certificate_name.

   For example, if the certificate says:
   "Certificate of Completion"
   and the course is:
   "AI for Business Professionals"

   return:

   "certificate_name": "Certificate of Completion"
   "course_name": "AI for Business Professionals"

   If no course, training, program, or learning
   title is visibly present, return null.

3. issuing_organization:
   Extract the organization that issued
   the certificate.

4. issue_date:
   Extract the issue or completion date only
   if clearly visible.

   Prefer ISO format YYYY-MM-DD when the date
   is unambiguous.

   If the date is ambiguous, return null and
   explain the uncertainty in extraction_notes.

5. expiration_date:
   Extract an expiration date only if it is
   explicitly visible.

   Never calculate or assume an expiration date.

6. credential_id:
   Extract a credential ID, certificate ID,
   verification ID, or similar identifier only
   if visibly present.

7. credential_url:
   Extract a verification or credential URL
   only if visibly present.

   Never construct or guess a URL.

8. certificate_holder_name:
   Extract the person's name appearing as
   the certificate recipient.

9. extraction_notes:
   Briefly describe uncertainty, unreadable text,
   ambiguous dates, partially visible information,
   or fields that could not be confidently
   extracted.

IMPORTANT:

- Never fabricate information.
- Never guess missing information.
- Never claim that the certificate is genuine.
- Never claim that the issuer has verified it.
- Never perform external verification.
- If a field is not visible, return null.
- Preserve information as it appears on the
  certificate.
- Keep certificate_name and course_name separate.
"""

        try:
            response = (
                self.client.chat.completions.create(
                    model=self.VISION_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You extract certificate "
                                "information accurately "
                                "from images. "
                                "Only return information "
                                "supported by visible "
                                "evidence in the image."
                            )
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": (
                                            f"data:"
                                            f"{content_type};"
                                            f"base64,"
                                            f"{encoded_image}"
                                        )
                                    }
                                }
                            ]
                        }
                    ],
                    temperature=0,
                    response_format={
                        "type": "json_object"
                    }
                )
            )

            content = (
                response
                .choices[0]
                .message
                .content
            )

            if not content:
                raise RuntimeError(
                    "AI returned an empty response."
                )

            extracted_data = json.loads(
                content
            )

            if not isinstance(
                extracted_data,
                dict
            ):
                raise RuntimeError(
                    "AI returned an invalid "
                    "certificate extraction object."
                )

            expected_fields = [
                "certificate_name",
                "course_name",
                "issuing_organization",
                "issue_date",
                "expiration_date",
                "credential_id",
                "credential_url",
                "certificate_holder_name",
                "extraction_notes"
            ]

            for field in expected_fields:
                if field not in extracted_data:
                    extracted_data[field] = None

            return extracted_data

        except json.JSONDecodeError as error:
            raise RuntimeError(
                "AI returned invalid JSON."
            ) from error

        except Exception as error:
            raise RuntimeError(
                "Certificate AI extraction failed: "
                f"{error}"
            ) from error


certificate_ai_service = CertificateAIService()