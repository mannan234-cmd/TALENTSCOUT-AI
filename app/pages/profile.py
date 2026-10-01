import streamlit as st

from uuid import UUID

from app.models.profile import StudentProfile
from app.services.profile_service import profile_service


st.set_page_config(
    page_title="Student Profile | TalentScout AI",
    page_icon="👤",
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




# TALENTSCOUT_UI8_PROFILE_V1

st.markdown(
    """
    <style>
    /* UI-8 — Profile Page */

    .ts-ui8-hero {
        padding: 0.35rem 0 1.35rem 0;
    }

    .ts-ui8-hero-title {
        font-size: clamp(1.8rem, 4vw, 2.55rem);
        font-weight: 780;
        line-height: 1.12;
        margin-bottom: 0.35rem;
    }

    .ts-ui8-hero-subtitle {
        font-size: 0.98rem;
        line-height: 1.55;
        opacity: 0.68;
        max-width: 760px;
    }

    .ts-ui8-section {
        margin-top: 0.65rem;
        margin-bottom: 0.65rem;
    }

    .ts-ui8-section-kicker {
        font-size: 0.72rem;
        font-weight: 750;
        letter-spacing: 0.09em;
        text-transform: uppercase;
        opacity: 0.58;
        margin-bottom: 0.2rem;
    }

    .ts-ui8-section-title {
        font-size: 1.12rem;
        font-weight: 720;
        line-height: 1.3;
        margin-bottom: 0.2rem;
    }

    .ts-ui8-section-help {
        font-size: 0.88rem;
        line-height: 1.45;
        opacity: 0.66;
        margin-bottom: 0.8rem;
    }

    section.main .stTextInput > div > div,
    section.main .stTextArea > div > div,
    section.main .stSelectbox > div > div,
    section.main .stMultiSelect > div > div {
        border-radius: 0.65rem;
    }

    section.main .stButton > button {
        border-radius: 0.7rem;
        min-height: 2.45rem;
    }

    @media (max-width: 768px) {
        .ts-ui8-hero-title {
            font-size: 1.75rem;
        }

        .ts-ui8-hero-subtitle {
            font-size: 0.9rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class="ts-ui8-hero">
        <div class="ts-ui8-hero-title">
            👤 Student Profile
        </div>
        <div class="ts-ui8-hero-subtitle">
            Keep your professional information organized so TalentScout AI
            can use your profile consistently across your career workspace.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write(
    "Create and manage your master career profile. "
    "This information will be used later for CV analysis, "
    "opportunity matching, skill-gap analysis, career guidance, "
    "and application assistance."
)

st.divider()


# ============================================================
# LOAD EXISTING PROFILE
# ============================================================

profile_id = st.session_state.get("profile_id")

existing_profile = None

if profile_id:

    try:
        existing_profile = profile_service.get_profile(
            UUID(str(profile_id))
        )

    except Exception as error:

        st.error(
            f"Unable to load your profile: {error}"
        )


# ============================================================
# PROFILE STATUS
# ============================================================

if existing_profile:

    st.success(
        "✅ Existing profile loaded. "
        "You can review and edit your information below."
    )

    st.caption(
        f"Profile ID: {existing_profile['id']}"
    )

else:

    st.info(
        "No existing profile is currently loaded. "
        "Fill in the information below to create your profile."
    )


st.divider()


# ============================================================
# PREPARE EXISTING VALUES
# ============================================================

if existing_profile:

    existing_full_name = (
        existing_profile.get("full_name")
        or ""
    )

    existing_email = (
        existing_profile.get("email")
        or ""
    )

    existing_phone = (
        existing_profile.get("phone")
        or ""
    )

    existing_location = (
        existing_profile.get("location")
        or ""
    )

    existing_bio = (
        existing_profile.get("bio")
        or ""
    )

    existing_career_summary = (
        existing_profile.get("career_summary")
        or ""
    )

    existing_interests = existing_profile.get(
        "interests"
    ) or []

    existing_certifications = existing_profile.get(
        "certifications"
    ) or []

    existing_achievements = existing_profile.get(
        "achievements"
    ) or []

    existing_career_level = (
        existing_profile.get("career_level")
        or ""
    )

    existing_years_of_experience = float(
        existing_profile.get(
            "years_of_experience"
        ) or 0
    )

else:

    existing_full_name = ""
    existing_email = ""
    existing_phone = ""
    existing_location = ""
    existing_bio = ""
    existing_career_summary = ""
    existing_interests = []
    existing_certifications = []
    existing_achievements = []
    existing_career_level = ""
    existing_years_of_experience = 0.0


# ============================================================
# FORM
# ============================================================

with st.form("student_profile_form"):

    st.markdown(
    """
    <div class="ts-ui8-section">
        <div class="ts-ui8-section-kicker">Profile</div>
        <div class="ts-ui8-section-title">Personal Information</div>
        <div class="ts-ui8-section-help">
            Tell us about yourself and the information you want to present
            professionally.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

    col1, col2 = st.columns(2)

    with col1:

        full_name = st.text_input(
            "Full Name *",
            value=existing_full_name
        )

        email = st.text_input(
            "Email",
            value=existing_email
        )

        phone = st.text_input(
            "Phone",
            value=existing_phone
        )

    with col2:

        location = st.text_input(
            "Location",
            value=existing_location
        )

        career_levels = [
            "",
            "High School Student",
            "Undergraduate Student",
            "Graduate Student",
            "Fresh Graduate",
            "Entry Level",
            "Junior Professional",
            "Mid-Level Professional"
        ]

        if (
            existing_career_level
            and existing_career_level
            not in career_levels
        ):
            career_levels.append(
                existing_career_level
            )

        career_level = st.selectbox(
            "Career Level",
            career_levels,
            index=career_levels.index(
                existing_career_level
            )
        )

        years_of_experience = st.number_input(
            "Years of Experience",
            min_value=0.0,
            max_value=50.0,
            value=existing_years_of_experience,
            step=0.5
        )

    bio = st.text_area(
        "Short Bio",
        value=existing_bio,
        height=120,
        placeholder="Briefly introduce yourself."
    )

    career_summary = st.text_area(
        "Career Summary",
        value=existing_career_summary,
        height=150,
        placeholder=(
            "Describe your background, interests, "
            "career direction, and professional goals."
        )
    )

    st.markdown(
    """
    <div class="ts-ui8-section">
        <div class="ts-ui8-section-kicker">Career</div>
        <div class="ts-ui8-section-title">Career Information</div>
        <div class="ts-ui8-section-help">
            Add the career details that describe your professional direction,
            experience, and goals.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

    interests_text = st.text_input(
        "Career Interests",
        value=", ".join(existing_interests),
        placeholder=(
            "Example: Artificial Intelligence, "
            "Data Science, Marketing"
        )
    )

    certifications_text = st.text_input(
        "Certifications",
        value=", ".join(existing_certifications),
        placeholder=(
            "Example: Google Data Analytics, "
            "AWS Cloud Practitioner"
        )
    )

    achievements_text = st.text_area(
        "Achievements",
        value="\n".join(existing_achievements),
        height=120,
        placeholder=(
            "Enter one achievement per line."
        )
    )

    st.divider()

    if existing_profile:

        submit_button = st.form_submit_button(
            "✏️ Update Profile",
            width="stretch"
        )

    else:

        submit_button = st.form_submit_button(
            "💾 Create Profile",
            width="stretch"
        )


# ============================================================
# SAVE / UPDATE PROFILE
# ============================================================

if submit_button:

    try:

        # ----------------------------------------------------
        # Basic validation
        # ----------------------------------------------------

        if not full_name.strip():

            st.error(
                "Full Name is required."
            )

            st.stop()


        # ----------------------------------------------------
        # Convert text fields into lists
        # ----------------------------------------------------

        interests = [
            item.strip()
            for item in interests_text.split(",")
            if item.strip()
        ]

        certifications = [
            item.strip()
            for item in certifications_text.split(",")
            if item.strip()
        ]

        achievements = [
            item.strip()
            for item in achievements_text.splitlines()
            if item.strip()
        ]


        # ----------------------------------------------------
        # Create Pydantic profile object
        # ----------------------------------------------------

        profile = StudentProfile(

            full_name=full_name.strip(),

            email=email.strip() or None,

            phone=phone.strip() or None,

            location=location.strip() or None,

            bio=bio.strip() or None,

            career_summary=(
                career_summary.strip()
                or None
            ),

            interests=interests,

            certifications=certifications,

            achievements=achievements,

            career_level=(
                career_level
                or None
            ),

            years_of_experience=(
                years_of_experience
            )
        )


        # ====================================================
        # UPDATE EXISTING PROFILE
        # ====================================================

        if existing_profile:

            updated_profile = (
                profile_service.update_profile(
                    UUID(str(profile_id)),
                    profile
                )
            )

            if not updated_profile:

                raise RuntimeError(
                    "Profile update failed. "
                    "Supabase returned no updated profile."
                )

            st.session_state["profile_id"] = (
                updated_profile["id"]
            )

            st.success(
                "✅ Your profile has been updated successfully."
            )

            st.rerun()


        # ====================================================
        # CREATE NEW PROFILE
        # ====================================================

        else:

            saved_profile = (
                profile_service.create_profile(
                    profile
                )
            )

            if not saved_profile:

                raise RuntimeError(
                    "Profile creation failed."
                )

            st.session_state["profile_id"] = (
                saved_profile["id"]
            )

            st.success(
                "✅ Your profile has been created successfully."
            )

            st.write(
                "Profile ID:",
                saved_profile["id"]
            )

            st.rerun()


    except Exception as error:

        st.error(
            f"Unable to save profile: {error}"
        )