import os
from datetime import date
from uuid import UUID

import streamlit as st
from pydantic import ValidationError

from app.models.certificate import Certificate
from app.services.certificate_service import certificate_service
from app.services.certificate_ai_service import (
    certificate_ai_service
)
from app.services.certificate_verification_service import (
    certificate_verification_service
)


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="Certificates | TalentScout AI",
    page_icon="🏆",
    layout="wide"
)


# ============================================================
# Authentication Guard
# ============================================================

if not st.session_state.get(
    "auth_authenticated",
    False,
):
    st.switch_page("streamlit_app.py")



# ============================================================
# Active Student Profile
# ============================================================

profile_id = st.session_state.get("profile_id")

if not profile_id:
    st.warning(
        "No student profile is currently loaded. "
        "Please create or load your Student Profile first."
    )
    st.stop()

try:
    PROFILE_ID = UUID(str(profile_id))

except (ValueError, TypeError):
    st.error(
        "The active student profile ID is invalid."
    )
    st.stop()


# ============================================================
# Helper Functions
# ============================================================

def clean_filename(filename: str) -> str:
    """
    Create a safe filename for Supabase Storage.
    """
    filename = os.path.basename(filename)

    allowed_chars = (
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789"
        "._-"
    )

    cleaned = "".join(
        char if char in allowed_chars else "_"
        for char in filename
    )

    return cleaned or "certificate"


def load_certificates():
    """
    Load all certificates belonging to the active profile.
    """
    try:
        return certificate_service.get_profile_certificates(
            PROFILE_ID
        )
    except Exception as error:
        st.error(
            f"Unable to load certificates: {error}"
        )
        return []


def get_signed_url(file_path: str):
    """
    Create a temporary signed URL for a private certificate.
    """
    try:
        return certificate_service.create_signed_url(
            file_path,
            expires_in=3600
        )
    except Exception as error:
        st.error(
            f"Unable to create certificate preview: {error}"
        )
        return None


# ============================================================
# Page Header
# ============================================================


# TALENTSCOUT_UI9_CERTIFICATES_V1
st.markdown(
    """
    <style>
    .ts-ui9-hero {
        padding: 1.45rem 1.6rem;
        border: 1px solid rgba(100, 116, 139, 0.18);
        border-radius: 18px;
        background: linear-gradient(
            135deg,
            rgba(255,255,255,0.98),
            rgba(248,250,252,0.94)
        );
        margin-bottom: 1.35rem;
    }

    .ts-ui9-hero-kicker {
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        opacity: 0.68;
        margin-bottom: 0.35rem;
    }

    .ts-ui9-hero-title {
        font-size: clamp(1.7rem, 3vw, 2.35rem);
        font-weight: 760;
        line-height: 1.15;
        margin: 0;
    }

    .ts-ui9-hero-subtitle {
        margin-top: 0.55rem;
        max-width: 760px;
        font-size: 1rem;
        line-height: 1.55;
        opacity: 0.76;
    }

    .ts-ui9-section {
        padding: 0.2rem 0 0.35rem 0;
        margin: 1.15rem 0 0.65rem 0;
    }

    .ts-ui9-section-kicker {
        font-size: 0.74rem;
        font-weight: 750;
        letter-spacing: 0.07em;
        text-transform: uppercase;
        opacity: 0.62;
        margin-bottom: 0.15rem;
    }

    .ts-ui9-section-title {
        font-size: 1.28rem;
        font-weight: 720;
        line-height: 1.25;
        margin: 0;
    }

    .ts-ui9-section-help {
        margin-top: 0.28rem;
        font-size: 0.9rem;
        line-height: 1.45;
        opacity: 0.7;
        max-width: 760px;
    }

    .ts-ui9-card {
        border: 1px solid rgba(100, 116, 139, 0.16);
        border-radius: 16px;
        padding: 0.15rem;
        background: rgba(255,255,255,0.72);
    }

    @media (max-width: 768px) {
        .ts-ui9-hero {
            padding: 1.1rem 1rem;
            border-radius: 14px;
        }

        .ts-ui9-hero-title {
            font-size: 1.65rem;
        }

        .ts-ui9-section-title {
            font-size: 1.12rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="ts-ui9-hero">
        <div class="ts-ui9-hero-kicker">Professional Credentials</div>
        <div class="ts-ui9-hero-title">🏆 Certificate Intelligence</div>
        <div class="ts-ui9-hero-subtitle">
            Keep your certifications organized, review credential details,
            and maintain a reliable record of your professional achievements.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write(
    "Upload, view, manage, and maintain your professional "
    "certificates. Original certificate files are stored "
    "securely in Supabase Storage."
)

st.caption(
    "Certificate verification is evidence-based and is "
    "not automatically assumed from an uploaded image."
)

st.divider()


# ============================================================
# Add New Certificate
# ============================================================

st.markdown(
    """
    <div class="ts-ui9-section">
        <div class="ts-ui9-section-kicker">Credentials</div>
        <div class="ts-ui9-section-title">➕ Add New Certificate</div>
        <div class="ts-ui9-section-help">
            Add a certification, credential, or course record to your profile.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander(
    "Open certificate upload form",
    expanded=False
):

    with st.form("add_certificate_form"):

        certificate_name = st.text_input(
            "Certificate Name *",
            placeholder="e.g. Certificate of Completion"
        )

        course_name = st.text_input(
            "Course / Training Name",
            placeholder="e.g. AI for Business Professionals",
            help=(
                "Enter the course, training, program, or "
                "learning activity associated with this certificate."
            )
        )

        issuing_organization = st.text_input(
            "Issuing Organization",
            placeholder="e.g. HP LIFE | HP Foundation"
        )

        credential_id = st.text_input(
            "Credential ID",
            placeholder="Enter credential ID if available"
        )

        col1, col2 = st.columns(2)

        with col1:
            issue_date = st.date_input(
                "Issue Date",
                value=None
            )

        with col2:
            expiration_date = st.date_input(
                "Expiration Date",
                value=None
            )

        credential_url = st.text_input(
            "Credential / Verification URL",
            placeholder="https://..."
        )

        uploaded_file = st.file_uploader(
            "Original Certificate Image *",
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp"
            ],
            help="Maximum file size: 10 MB."
        )

        add_certificate_button = st.form_submit_button(
            "💾 Add Certificate",
            use_container_width=True
        )


# ============================================================
# Add Certificate Processing
# ============================================================

if add_certificate_button:

    if not certificate_name.strip():
        st.error(
            "Please enter the certificate name."
        )
        st.stop()

    if uploaded_file is None:
        st.error(
            "Please upload the original certificate image."
        )
        st.stop()

    if uploaded_file.size > 10 * 1024 * 1024:
        st.error(
            "Certificate image must be smaller than 10 MB."
        )
        st.stop()

    if (
        issue_date is not None
        and expiration_date is not None
        and expiration_date < issue_date
    ):
        st.error(
            "Expiration date cannot be earlier than issue date."
        )
        st.stop()

    if credential_url.strip():
        normalized_credential_url = (
            credential_url.strip()
        )
    else:
        normalized_credential_url = None

    try:

        certificate = Certificate(
            profile_id=PROFILE_ID,
            certificate_name=certificate_name.strip(),
            course_name=(
                course_name.strip()
                or None
            ),
            issuing_organization=(
                issuing_organization.strip()
                or None
            ),
            issue_date=issue_date,
            expiration_date=expiration_date,
            credential_id=(
                credential_id.strip()
                or None
            ),
            credential_url=normalized_credential_url,
            certificate_file_name=(
                uploaded_file.name
            ),
            certificate_file_type=(
                uploaded_file.type
            ),
            verification_status="Not Verified"
        )

    except ValidationError as error:

        st.error(
            f"Certificate validation failed: {error}"
        )

        st.stop()

    safe_filename = clean_filename(
        uploaded_file.name
    )

    storage_path = (
        f"certificates/"
        f"{PROFILE_ID}/"
        f"{safe_filename}"
    )

    try:

        # ----------------------------------------------------
        # Upload original certificate image
        # ----------------------------------------------------

        certificate_service.upload_certificate_file(
            file_path=storage_path,
            file_bytes=uploaded_file.getvalue(),
            content_type=uploaded_file.type
        )

        # ----------------------------------------------------
        # Add storage information to certificate model
        # ----------------------------------------------------

        certificate.certificate_file_path = (
            storage_path
        )

        # ----------------------------------------------------
        # Save certificate metadata
        # ----------------------------------------------------

        saved_certificate = (
            certificate_service.create_certificate(
                certificate
            )
        )

        st.success(
            "🎉 Certificate added successfully!"
        )

        st.write(
            f"**Certificate ID:** "
            f"`{saved_certificate['id']}`"
        )

        st.rerun()

    except Exception as error:

        # ----------------------------------------------------
        # If database save fails after upload,
        # remove uploaded file to avoid orphaned storage.
        # ----------------------------------------------------

        try:
            certificate_service.delete_certificate_file(
                storage_path
            )
        except Exception:
            pass

        st.error(
            f"Unable to save certificate: {error}"
        )


# ============================================================
# Load Existing Certificates
# ============================================================

certificates = load_certificates()


# ============================================================
# Certificate Summary
# ============================================================

st.divider()

st.markdown(
    """
    <div class="ts-ui9-section">
        <div class="ts-ui9-section-kicker">Your Credentials</div>
        <div class="ts-ui9-section-title">📚 My Certificates</div>
        <div class="ts-ui9-section-help">
            Review the certificates currently stored in your profile.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if certificates:

    st.caption(
        f"{len(certificates)} certificate(s) found."
    )

else:

    st.info(
        "No certificates have been added yet. "
        "Use the upload form above to add your first certificate."
    )


# ============================================================
# Certificate Gallery
# ============================================================

for certificate_record in certificates:

    certificate_id = certificate_record.get(
        "id"
    )

    certificate_name = (
        certificate_record.get(
            "certificate_name"
        )
        or "Unnamed Certificate"
    )

    issuing_organization = (
        certificate_record.get(
            "issuing_organization"
        )
        or "Not provided"
    )

    verification_status = (
        certificate_record.get(
            "verification_status"
        )
        or "Not Verified"
    )

    issue_date_value = certificate_record.get(
        "issue_date"
    )

    expiration_date_value = certificate_record.get(
        "expiration_date"
    )

    credential_id_value = certificate_record.get(
        "credential_id"
    )

    credential_url_value = certificate_record.get(
        "credential_url"
    )

    file_path = certificate_record.get(
        "certificate_file_path"
    )

    file_name = certificate_record.get(
        "certificate_file_name"
    )


    # ========================================================
    # Certificate Card
    # ========================================================

    with st.container(border=True):

        st.markdown(
            f"### 🏆 {certificate_name}"
        )

        col1, col2 = st.columns(
            [2, 1]
        )

        # ----------------------------------------------------
        # Certificate Information
        # ----------------------------------------------------

        with col1:

            st.write(
                f"**Issuing Organization:** "
                f"{issuing_organization}"
            )

            if issue_date_value:
                st.write(
                    f"**Issue Date:** "
                    f"{issue_date_value}"
                )

            if expiration_date_value:
                st.write(
                    f"**Expiration Date:** "
                    f"{expiration_date_value}"
                )

            if credential_id_value:
                st.write(
                    f"**Credential ID:** "
                    f"{credential_id_value}"
                )

            if credential_url_value:

                st.write(
                    "**Credential URL:**"
                )

                st.write(
                    credential_url_value
                )

            st.write(
                f"**Verification Status:** "
                f"`{verification_status}`"
            )

            if file_name:

                st.caption(
                    f"Original file: {file_name}"
                )


        # ----------------------------------------------------
        # Certificate Preview
        # ----------------------------------------------------

        with col2:

            if file_path:

                signed_url = get_signed_url(
                    file_path
                )

                if signed_url:

                    st.image(
                        signed_url,
                        caption="Original Certificate",
                        use_container_width=True
                    )

                    st.link_button(
                        "🔍 View Full Certificate",
                        signed_url,
                        use_container_width=True
                    )

                else:

                    st.warning(
                        "Certificate preview unavailable."
                    )

            else:

                st.info(
                    "No original certificate file stored."
                )


        # ====================================================
        # Evidence-Based Certificate Verification
        # ====================================================

        st.divider()

        st.subheader(
            "🔎 Evidence-Based Verification"
        )

        st.caption(
            "This review compares visible certificate "
            "evidence with the stored profile and "
            "certificate information. It does not "
            "independently prove certificate authenticity."
        )

        verification_button_key = (
            f"verify_certificate_"
            f"{certificate_id}"
        )

        if st.button(
            "🔎 Run Evidence Review",
            key=verification_button_key,
            use_container_width=True
        ):

            if not file_path:
                st.error(
                    "No original certificate image is "
                    "available for evidence review."
                )

            else:

                with st.spinner(
                    "Analyzing certificate evidence..."
                ):

                    try:

                        # --------------------------------------------
                        # Load active student profile
                        # --------------------------------------------

                        from app.services.profile_service import (
                            profile_service
                        )

                        active_profile = (
                            profile_service.get_profile(
                                PROFILE_ID
                            )
                        )

                        if not active_profile:
                            raise RuntimeError(
                                "Student profile could not "
                                "be loaded."
                            )

                        # --------------------------------------------
                        # Create temporary signed URL
                        # --------------------------------------------

                        verification_signed_url = (
                            certificate_service
                            .create_signed_url(
                                file_path,
                                expires_in=300
                            )
                        )

                        # --------------------------------------------
                        # Download original certificate image
                        # --------------------------------------------

                        import requests

                        verification_response = (
                            requests.get(
                                verification_signed_url,
                                timeout=30
                            )
                        )

                        verification_response.raise_for_status()

                        verification_image_bytes = (
                            verification_response.content
                        )

                        if not verification_image_bytes:
                            raise RuntimeError(
                                "Downloaded certificate "
                                "image is empty."
                            )

                        # --------------------------------------------
                        # Determine image content type
                        # --------------------------------------------

                        verification_content_type = (
                            certificate_record.get(
                                "certificate_file_type"
                            )
                            or "image/png"
                        )

                        # --------------------------------------------
                        # AI certificate extraction
                        # --------------------------------------------

                        extracted_certificate_data = (
                            certificate_ai_service
                            .extract_certificate_information(
                                image_bytes=(
                                    verification_image_bytes
                                ),
                                content_type=(
                                    verification_content_type
                                )
                            )
                        )

                        # --------------------------------------------
                        # Evidence-based comparison
                        # --------------------------------------------

                        verification_result = (
                            certificate_verification_service
                            .verify_certificate(
                                certificate=(
                                    certificate_record
                                ),
                                profile=(
                                    active_profile
                                ),
                                extracted_data=(
                                    extracted_certificate_data
                                )
                            )
                        )

                        # --------------------------------------------
                        # Save overall verification status
                        # --------------------------------------------

                        saved_verification = (
                            certificate_service
                            .update_verification_result(
                                certificate_id=(
                                    UUID(
                                        str(certificate_id)
                                    )
                                ),
                                verification_status=(
                                    verification_result
                                    .verification_status
                                ),
                                verification_notes=(
                                    verification_result
                                    .verification_notes
                                )
                            )
                        )

                        if not saved_verification:
                            raise RuntimeError(
                                "Verification result could "
                                "not be saved."
                            )

                        # --------------------------------------------
                        # Save detailed result in session state
                        # --------------------------------------------

                        st.session_state[
                            f"verification_result_{certificate_id}"
                        ] = verification_result.model_dump()

                        st.session_state[
                            f"verification_extracted_{certificate_id}"
                        ] = extracted_certificate_data

                        st.success(
                            "Evidence review completed and "
                            "verification status saved."
                        )

                    except Exception as error:

                        st.error(
                            "Certificate evidence review "
                            f"failed: {error}"
                        )

        # --------------------------------------------------------
        # Display latest verification result
        # --------------------------------------------------------

        saved_verification_result = (
            st.session_state.get(
                f"verification_result_{certificate_id}"
            )
        )

        saved_extracted_data = (
            st.session_state.get(
                f"verification_extracted_{certificate_id}"
            )
        )

        if saved_verification_result:

            st.markdown(
                "#### 📊 Latest Evidence Review"
            )

            current_status = (
                saved_verification_result.get(
                    "verification_status",
                    "Not Verified"
                )
            )

            st.write(
                f"**Overall Status:** "
                f"`{current_status}`"
            )

            st.write(
                "**Comparison Results**"
            )

            result_col1, result_col2 = (
                st.columns(2)
            )

            with result_col1:

                st.write(
                    "Holder Name:",
                    saved_verification_result.get(
                        "holder_name_result",
                        "NOT AVAILABLE"
                    )
                )

                st.write(
                    "Certificate Name:",
                    saved_verification_result.get(
                        "certificate_name_result",
                        "NOT AVAILABLE"
                    )
                )

                st.write(
                    "Course Name:",
                    saved_verification_result.get(
                        "course_name_result",
                        "NOT AVAILABLE"
                    )
                )

            with result_col2:

                st.write(
                    "Issuer:",
                    saved_verification_result.get(
                        "issuer_result",
                        "NOT AVAILABLE"
                    )
                )

                st.write(
                    "Issue Date:",
                    saved_verification_result.get(
                        "issue_date_result",
                        "NOT AVAILABLE"
                    )
                )

                st.write(
                    "Original Image:",
                    (
                        "AVAILABLE"
                        if saved_verification_result.get(
                            "original_image_available"
                        )
                        else "NOT AVAILABLE"
                    )
                )

            # ----------------------------------------------------
            # Evidence points
            # ----------------------------------------------------

            evidence = (
                saved_verification_result.get(
                    "evidence_points",
                    []
                )
            )

            if evidence:

                st.write(
                    "**Evidence Supporting Review**"
                )

                for evidence_item in evidence:
                    st.success(
                        f"✓ {evidence_item}"
                    )

            # ----------------------------------------------------
            # Review flags
            # ----------------------------------------------------

            review_flags = (
                saved_verification_result.get(
                    "review_flags",
                    []
                )
            )

            if review_flags:

                st.write(
                    "**Review Flags**"
                )

                for review_flag in review_flags:
                    st.warning(
                        f"⚠️ {review_flag}"
                    )

            # ----------------------------------------------------
            # Verification notes
            # ----------------------------------------------------

            verification_notes = (
                saved_verification_result.get(
                    "verification_notes"
                )
            )

            if verification_notes:

                st.info(
                    verification_notes
                )

            # ----------------------------------------------------
            # Extracted information
            # ----------------------------------------------------

            if saved_extracted_data:

                with st.expander(
                    "🤖 Review AI-Extracted Certificate Information",
                    expanded=True
                ):

                    st.caption(
                        "Review the information extracted "
                        "from the original certificate image. "
                        "AI extraction does not automatically "
                        "overwrite your saved certificate data."
                    )

                    review_certificate_name = st.text_input(
                        "Certificate Name",
                        value=(
                            saved_extracted_data.get(
                                "certificate_name"
                            )
                            or certificate_name
                            or ""
                        ),
                        key=(
                            f"review_certificate_name_"
                            f"{certificate_id}"
                        )
                    )

                    review_course_name = st.text_input(
                        "Course / Training Name",
                        value=(
                            saved_extracted_data.get(
                                "course_name"
                            )
                            or certificate_record.get(
                                "course_name"
                            )
                            or ""
                        ),
                        key=(
                            f"review_course_name_"
                            f"{certificate_id}"
                        )
                    )

                    review_issuer = st.text_input(
                        "Issuing Organization",
                        value=(
                            saved_extracted_data.get(
                                "issuing_organization"
                            )
                            or certificate_record.get(
                                "issuing_organization"
                            )
                            or ""
                        ),
                        key=(
                            f"review_issuer_"
                            f"{certificate_id}"
                        )
                    )

                    review_issue_date = st.text_input(
                        "Issue Date",
                        value=(
                            saved_extracted_data.get(
                                "issue_date"
                            )
                            or str(
                                certificate_record.get(
                                    "issue_date"
                                )
                                or ""
                            )
                        ),
                        key=(
                            f"review_issue_date_"
                            f"{certificate_id}"
                        )
                    )

                    review_expiration_date = st.text_input(
                        "Expiration Date",
                        value=(
                            saved_extracted_data.get(
                                "expiration_date"
                            )
                            or str(
                                certificate_record.get(
                                    "expiration_date"
                                )
                                or ""
                            )
                        ),
                        key=(
                            f"review_expiration_date_"
                            f"{certificate_id}"
                        )
                    )

                    review_credential_id = st.text_input(
                        "Credential ID",
                        value=(
                            saved_extracted_data.get(
                                "credential_id"
                            )
                            or certificate_record.get(
                                "credential_id"
                            )
                            or ""
                        ),
                        key=(
                            f"review_credential_id_"
                            f"{certificate_id}"
                        )
                    )

                    review_credential_url = st.text_input(
                        "Credential / Verification URL",
                        value=(
                            saved_extracted_data.get(
                                "credential_url"
                            )
                            or certificate_record.get(
                                "credential_url"
                            )
                            or ""
                        ),
                        key=(
                            f"review_credential_url_"
                            f"{certificate_id}"
                        )
                    )

                    review_holder_name = st.text_input(
                        "Certificate Holder Name",
                        value=(
                            saved_extracted_data.get(
                                "certificate_holder_name"
                            )
                            or ""
                        ),
                        key=(
                            f"review_holder_name_"
                            f"{certificate_id}"
                        )
                    )

                    extraction_notes = (
                        saved_extracted_data.get(
                            "extraction_notes"
                        )
                    )

                    if extraction_notes:
                        st.info(
                            "AI Extraction Notes: "
                            f"{extraction_notes}"
                        )

                    st.warning(
                        "Review these values carefully before "
                        "saving. AI extraction is evidence for "
                        "review and does not establish certificate "
                        "authenticity by itself."
                    )

                    save_reviewed_key = (
                        f"save_reviewed_certificate_"
                        f"{certificate_id}"
                    )

                    if st.button(
                        "💾 Save Reviewed Information",
                        key=save_reviewed_key,
                        use_container_width=True
                    ):

                        try:

                            reviewed_issue_date = (
                                date.fromisoformat(
                                    review_issue_date.strip()
                                )
                                if review_issue_date.strip()
                                else None
                            )

                            reviewed_expiration_date = (
                                date.fromisoformat(
                                    review_expiration_date.strip()
                                )
                                if review_expiration_date.strip()
                                else None
                            )

                            normalized_reviewed_url = (
                                review_credential_url.strip()
                                or None
                            )

                            updated_certificate = Certificate(
                                profile_id=PROFILE_ID,
                                certificate_name=(
                                    review_certificate_name.strip()
                                ),
                                course_name=(
                                    review_course_name.strip()
                                    or None
                                ),
                                issuing_organization=(
                                    review_issuer.strip()
                                    or None
                                ),
                                issue_date=(
                                    reviewed_issue_date
                                ),
                                expiration_date=(
                                    reviewed_expiration_date
                                ),
                                credential_id=(
                                    review_credential_id.strip()
                                    or None
                                ),
                                credential_url=(
                                    normalized_reviewed_url
                                ),
                                certificate_file_path=(
                                    certificate_record.get(
                                        "certificate_file_path"
                                    )
                                ),
                                certificate_file_name=(
                                    certificate_record.get(
                                        "certificate_file_name"
                                    )
                                ),
                                certificate_file_type=(
                                    certificate_record.get(
                                        "certificate_file_type"
                                    )
                                ),
                                verification_status=(
                                    certificate_record.get(
                                        "verification_status"
                                    )
                                    or "Not Verified"
                                ),
                                verification_notes=(
                                    certificate_record.get(
                                        "verification_notes"
                                    )
                                )
                            )

                            saved_reviewed_certificate = (
                                certificate_service
                                .update_certificate(
                                    UUID(
                                        str(certificate_id)
                                    ),
                                    updated_certificate
                                )
                            )

                            if not saved_reviewed_certificate:
                                raise RuntimeError(
                                    "Reviewed certificate "
                                    "information could not be saved."
                                )

                            st.success(
                                "✅ Reviewed certificate "
                                "information saved successfully."
                            )

                            st.rerun()

                        except ValueError:
                            st.error(
                                "Please enter Issue Date and "
                                "Expiration Date in YYYY-MM-DD format."
                            )

                        except Exception as error:
                            st.error(
                                "Saving reviewed certificate "
                                f"information failed: {error}"
                            )

        # ====================================================
        # Management Controls
        # ====================================================

        st.divider()

        action_col1, action_col2 = st.columns(2)

        with action_col1:

            edit_key = (
                f"edit_certificate_"
                f"{certificate_id}"
            )

            if st.button(
                "✏️ Edit Certificate",
                key=edit_key,
                use_container_width=True
            ):

                st.session_state[
                    "editing_certificate_id"
                ] = str(certificate_id)

                st.rerun()


        with action_col2:

            delete_key = (
                f"delete_certificate_"
                f"{certificate_id}"
            )

            if st.button(
                "🗑️ Delete Certificate",
                key=delete_key,
                use_container_width=True
            ):

                st.session_state[
                    "deleting_certificate_id"
                ] = str(certificate_id)

                st.rerun()


# ============================================================
# Edit Certificate
# ============================================================

editing_certificate_id = st.session_state.get(
    "editing_certificate_id"
)

if editing_certificate_id:

    st.divider()

    st.markdown(
    """
    <div class="ts-ui9-section">
        <div class="ts-ui9-section-kicker">Manage Credential</div>
        <div class="ts-ui9-section-title">✏️ Edit Certificate</div>
        <div class="ts-ui9-section-help">
            Update the selected certificate details while keeping your record current.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

    editing_certificate = (
        certificate_service.get_certificate(
            UUID(editing_certificate_id)
        )
    )

    if editing_certificate is None:

        st.error(
            "The selected certificate could not be found."
        )

        st.session_state.pop(
            "editing_certificate_id",
            None
        )

    else:

        current_issue_date = (
            editing_certificate.get(
                "issue_date"
            )
        )

        current_expiration_date = (
            editing_certificate.get(
                "expiration_date"
            )
        )

        if current_issue_date:
            current_issue_date = date.fromisoformat(
                str(current_issue_date)
            )

        if current_expiration_date:
            current_expiration_date = date.fromisoformat(
                str(current_expiration_date)
            )

        with st.form(
            "edit_certificate_form"
        ):

            edited_name = st.text_input(
                "Certificate Name *",
                value=(
                    editing_certificate.get(
                        "certificate_name"
                    )
                    or ""
                )
            )

            edited_course_name = st.text_input(
                "Course / Training Name",
                value=(
                    editing_certificate.get(
                        "course_name"
                    )
                    or ""
                ),
                help=(
                    "Course, training, program, or "
                    "learning activity associated "
                    "with this certificate."
                )
            )

            edited_organization = st.text_input(
                "Issuing Organization",
                value=(
                    editing_certificate.get(
                        "issuing_organization"
                    )
                    or ""
                )
            )

            edited_credential_id = st.text_input(
                "Credential ID",
                value=(
                    editing_certificate.get(
                        "credential_id"
                    )
                    or ""
                )
            )

            edit_col1, edit_col2 = st.columns(2)

            with edit_col1:

                edited_issue_date = st.date_input(
                    "Issue Date",
                    value=current_issue_date
                )

            with edit_col2:

                edited_expiration_date = st.date_input(
                    "Expiration Date",
                    value=current_expiration_date
                )

            edited_credential_url = st.text_input(
                "Credential / Verification URL",
                value=(
                    editing_certificate.get(
                        "credential_url"
                    )
                    or ""
                )
            )

            save_edit = st.form_submit_button(
                "💾 Save Changes",
                use_container_width=True
            )

            cancel_edit = st.form_submit_button(
                "Cancel",
                use_container_width=True
            )


        if cancel_edit:

            st.session_state.pop(
                "editing_certificate_id",
                None
            )

            st.rerun()


        if save_edit:

            if not edited_name.strip():

                st.error(
                    "Certificate name is required."
                )

                st.stop()

            if (
                edited_issue_date is not None
                and edited_expiration_date is not None
                and edited_expiration_date
                < edited_issue_date
            ):

                st.error(
                    "Expiration date cannot be earlier than issue date."
                )

                st.stop()

            try:

                updated_certificate = Certificate(
                    profile_id=PROFILE_ID,
                    certificate_name=(
                        edited_name.strip()
                    ),
                    course_name=(
                        edited_course_name.strip()
                        or None
                    ),
                    issuing_organization=(
                        edited_organization.strip()
                        or None
                    ),
                    issue_date=edited_issue_date,
                    expiration_date=(
                        edited_expiration_date
                    ),
                    credential_id=(
                        edited_credential_id.strip()
                        or None
                    ),
                    credential_url=(
                        edited_credential_url.strip()
                        or None
                    ),
                    certificate_file_path=(
                        editing_certificate.get(
                            "certificate_file_path"
                        )
                    ),
                    certificate_file_name=(
                        editing_certificate.get(
                            "certificate_file_name"
                        )
                    ),
                    certificate_file_type=(
                        editing_certificate.get(
                            "certificate_file_type"
                        )
                    ),
                    verification_status=(
                        editing_certificate.get(
                            "verification_status"
                        )
                        or "Not Verified"
                    ),
                    verification_notes=(
                        editing_certificate.get(
                            "verification_notes"
                        )
                    )
                )

                certificate_service.update_certificate(
                    UUID(editing_certificate_id),
                    updated_certificate
                )

                st.success(
                    "Certificate updated successfully!"
                )

                st.session_state.pop(
                    "editing_certificate_id",
                    None
                )

                st.rerun()

            except Exception as error:

                st.error(
                    f"Unable to update certificate: {error}"
                )


# ============================================================
# Delete Certificate Confirmation
# ============================================================

deleting_certificate_id = st.session_state.get(
    "deleting_certificate_id"
)

if deleting_certificate_id:

    st.divider()

    st.markdown(
    """
    <div class="ts-ui9-section">
        <div class="ts-ui9-section-kicker">Manage Credential</div>
        <div class="ts-ui9-section-title">🗑️ Delete Certificate</div>
        <div class="ts-ui9-section-help">
            Remove a certificate from your profile after confirming the action.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

    certificate_to_delete = (
        certificate_service.get_certificate(
            UUID(deleting_certificate_id)
        )
    )

    if certificate_to_delete is None:

        st.error(
            "The selected certificate could not be found."
        )

        st.session_state.pop(
            "deleting_certificate_id",
            None
        )

    else:

        st.warning(
            "Deleting this certificate will remove its "
            "database record and stored original file."
        )

        st.write(
            f"**Certificate:** "
            f"{certificate_to_delete.get('certificate_name', 'Unnamed Certificate')}"
        )

        confirm_col1, confirm_col2 = st.columns(2)

        with confirm_col1:

            confirm_delete = st.button(
                "⚠️ Yes, Delete Permanently",
                key="confirm_delete_certificate",
                use_container_width=True
            )

        with confirm_col2:

            cancel_delete = st.button(
                "Cancel",
                key="cancel_delete_certificate",
                use_container_width=True
            )


        if cancel_delete:

            st.session_state.pop(
                "deleting_certificate_id",
                None
            )

            st.rerun()


        if confirm_delete:

            file_path_to_delete = (
                certificate_to_delete.get(
                    "certificate_file_path"
                )
            )

            try:

                # --------------------------------------------
                # Delete database record first
                # --------------------------------------------

                deleted = (
                    certificate_service.delete_certificate(
                        UUID(deleting_certificate_id)
                    )
                )

                if not deleted:

                    raise RuntimeError(
                        "Certificate database record could not be deleted."
                    )

                # --------------------------------------------
                # Delete original file
                # --------------------------------------------

                if file_path_to_delete:

                    try:

                        certificate_service.delete_certificate_file(
                            file_path_to_delete
                        )

                    except Exception as storage_error:

                        st.warning(
                            "Certificate record was deleted, "
                            "but the original storage file "
                            f"could not be removed: {storage_error}"
                        )

                st.success(
                    "Certificate deleted successfully."
                )

                st.session_state.pop(
                    "deleting_certificate_id",
                    None
                )

                st.rerun()

            except Exception as error:

                st.error(
                    f"Unable to delete certificate: {error}"
                )