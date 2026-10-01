"""
TalentScout AI — Reusable UI Design System

This module contains presentation-only Streamlit UI primitives.
Business logic and service calls must remain outside this module.
"""

from __future__ import annotations

from typing import Optional

import streamlit as st


# ============================================================
# DESIGN TOKENS
# ============================================================

COLORS = {
    "primary": "#2563EB",
    "primary_hover": "#1D4ED8",
    "accent": "#7C3AED",
    "success": "#16A34A",
    "warning": "#D97706",
    "danger": "#DC2626",
    "text": "#111827",
    "muted": "#6B7280",
    "surface": "#FFFFFF",
    "surface_soft": "#F8FAFC",
    "border": "#E5E7EB",
    "background": "#F6F8FC",
}

SPACING = {
    "xs": "0.35rem",
    "sm": "0.65rem",
    "md": "1rem",
    "lg": "1.5rem",
    "xl": "2rem",
}

RADIUS = {
    "sm": "8px",
    "md": "12px",
    "lg": "16px",
}

SHADOW = {
    "card": "0 1px 3px rgba(15, 23, 42, 0.08), "
             "0 6px 18px rgba(15, 23, 42, 0.05)",
}


# ============================================================
# GLOBAL DESIGN SYSTEM
# ============================================================

def inject_design_system() -> None:
    """Inject the shared TalentScout visual system."""

    st.markdown(
        f"""
        <style>
        :root {{
            --ts-primary: {COLORS["primary"]};
            --ts-primary-hover: {COLORS["primary_hover"]};
            --ts-accent: {COLORS["accent"]};
            --ts-success: {COLORS["success"]};
            --ts-warning: {COLORS["warning"]};
            --ts-danger: {COLORS["danger"]};
            --ts-text: {COLORS["text"]};
            --ts-muted: {COLORS["muted"]};
            --ts-surface: {COLORS["surface"]};
            --ts-surface-soft: {COLORS["surface_soft"]};
            --ts-border: {COLORS["border"]};
            --ts-background: {COLORS["background"]};
        }}

        /* Page background */
        .stApp {{
            background: var(--ts-background);
        }}

        /* Main content width / breathing room */
        .block-container {{
            padding-top: 2rem;
            padding-bottom: 3rem;
        }}

        /* Typography */
        h1, h2, h3, h4 {{
            color: var(--ts-text);
            letter-spacing: -0.02em;
        }}

        /* Buttons */
        .stButton > button {{
            border-radius: 10px;
            min-height: 2.6rem;
            font-weight: 600;
            transition: all 0.15s ease;
        }}

        .stButton > button:hover {{
            transform: translateY(-1px);
        }}

        /* Inputs */
        .stTextInput input,
        .stTextArea textarea {{
            border-radius: 10px;
        }}

        /* Select controls */
        div[data-baseweb="select"] > div {{
            border-radius: 10px;
        }}

        /* File uploader */
        section[data-testid="stFileUploaderDropzone"] {{
            border-radius: 12px;
        }}

        /* Reduce excessive divider contrast */
        hr {{
            border-color: var(--ts-border);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# LAYOUT PRIMITIVES
# ============================================================

def page_header(
    title: str,
    subtitle: Optional[str] = None,
    icon: Optional[str] = None,
) -> None:
    """Render a consistent page-level heading."""

    display_title = f"{icon} {title}" if icon else title

    st.markdown(
        f"""
        <div style="
            margin-bottom: 1.5rem;
        ">
            <h1 style="
                margin-bottom: 0.35rem;
                color: {COLORS["text"]};
            ">
                {display_title}
            </h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if subtitle:
        st.caption(subtitle)


def section_header(
    title: str,
    subtitle: Optional[str] = None,
    icon: Optional[str] = None,
) -> None:
    """Render a consistent section heading."""

    display_title = f"{icon} {title}" if icon else title

    st.markdown(
        f"""
        <div style="
            margin-top: 1rem;
            margin-bottom: 0.8rem;
        ">
            <h2 style="
                margin: 0;
                font-size: 1.35rem;
                color: {COLORS["text"]};
            ">
                {display_title}
            </h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if subtitle:
        st.caption(subtitle)


def card_start(
    title: Optional[str] = None,
    icon: Optional[str] = None,
) -> None:
    """Render the opening visual shell for a reusable card."""

    st.markdown(
        f"""
        <div style="
            background: {COLORS["surface"]};
            border: 1px solid {COLORS["border"]};
            border-radius: {RADIUS["md"]};
            padding: 1.15rem;
            margin-bottom: 1rem;
            box-shadow: {SHADOW["card"]};
        ">
            {
                f'<div style="font-size:1.05rem;font-weight:700;color:{COLORS["text"]};margin-bottom:0.65rem;">'
                f'{icon + " " if icon else ""}{title}</div>'
                if title
                else ""
            }
        """,
        unsafe_allow_html=True,
    )


def card_end() -> None:
    """Close a reusable visual card shell."""

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# ============================================================
# STATUS / FEEDBACK
# ============================================================

def status_message(
    message: str,
    kind: str = "info",
) -> None:
    """Render a consistent status message."""

    colors = {
        "info": COLORS["primary"],
        "success": COLORS["success"],
        "warning": COLORS["warning"],
        "error": COLORS["danger"],
    }

    color = colors.get(kind, colors["primary"])

    st.markdown(
        f"""
        <div style="
            border-left: 4px solid {color};
            background: {COLORS["surface"]};
            border-radius: 8px;
            padding: 0.75rem 1rem;
            margin: 0.6rem 0;
        ">
            <span style="
                color: {COLORS["text"]};
                font-weight: 500;
            ">
                {message}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def empty_state(
    title: str,
    message: str,
    icon: str = "📭",
) -> None:
    """Render a consistent empty state."""

    st.markdown(
        f"""
        <div style="
            text-align: center;
            padding: 2.5rem 1.5rem;
            background: {COLORS["surface"]};
            border: 1px solid {COLORS["border"]};
            border-radius: {RADIUS["lg"]};
            margin: 1rem 0;
        ">
            <div style="font-size: 2rem;">{icon}</div>
            <div style="
                margin-top: 0.65rem;
                font-size: 1.15rem;
                font-weight: 700;
                color: {COLORS["text"]};
            ">
                {title}
            </div>
            <div style="
                margin-top: 0.35rem;
                color: {COLORS["muted"]};
            ">
                {message}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SPACING
# ============================================================

def spacer(size: str = "md") -> None:
    """Add controlled vertical spacing."""

    value = SPACING.get(size, SPACING["md"])

    st.markdown(
        f'<div style="height:{value};"></div>',
        unsafe_allow_html=True,
    )
