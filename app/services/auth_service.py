from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from app.services.supabase_service import SupabaseService


class AuthServiceError(Exception):
    """Raised when an authentication operation fails."""


@dataclass(frozen=True)
class AuthUser:
    """Minimal authenticated-user representation."""

    id: str
    email: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class AuthService:
    """Supabase authentication service for the Streamlit application."""

    @staticmethod
    def _client():
        return SupabaseService().supabase

    @classmethod
    def register(
        cls,
        email: str,
        password: str,
    ) -> AuthUser:
        """Register a new user with Supabase Auth."""

        email = email.strip()

        if not email:
            raise AuthServiceError("Email is required.")

        if not password:
            raise AuthServiceError("Password is required.")

        if len(password) < 6:
            raise AuthServiceError(
                "Password must be at least 6 characters long."
            )

        try:
            response = cls._client().auth.sign_up(
                {
                    "email": email,
                    "password": password,
                }
            )
        except Exception as exc:
            raise AuthServiceError(str(exc)) from exc

        user = getattr(response, "user", None)

        if user is None:
            raise AuthServiceError(
                "Registration did not return a user."
            )

        return AuthUser(
            id=str(user.id),
            email=getattr(user, "email", None),
            metadata=getattr(user, "user_metadata", None),
        )

    @classmethod
    def login(
        cls,
        email: str,
        password: str,
    ) -> AuthUser:
        """Authenticate an existing user."""

        email = email.strip()

        if not email:
            raise AuthServiceError("Email is required.")

        if not password:
            raise AuthServiceError("Password is required.")

        try:
            response = cls._client().auth.sign_in_with_password(
                {
                    "email": email,
                    "password": password,
                }
            )
        except Exception as exc:
            raise AuthServiceError(str(exc)) from exc

        user = getattr(response, "user", None)

        if user is None:
            raise AuthServiceError(
                "Login did not return an authenticated user."
            )

        return AuthUser(
            id=str(user.id),
            email=getattr(user, "email", None),
            metadata=getattr(user, "user_metadata", None),
        )

    @classmethod
    def logout(cls) -> None:
        """Sign out the current Supabase Auth session."""

        try:
            cls._client().auth.sign_out()
        except Exception as exc:
            raise AuthServiceError(str(exc)) from exc

    @classmethod
    def get_session(cls):
        """Return the current Supabase Auth session, if available."""

        try:
            return cls._client().auth.get_session()
        except Exception as exc:
            raise AuthServiceError(str(exc)) from exc

    @classmethod
    def get_current_user(cls) -> Optional[AuthUser]:
        """Return the current authenticated user, or None."""

        try:
            response = cls._client().auth.get_user()
        except Exception:
            return None

        user = getattr(response, "user", None)

        if user is None:
            return None

        return AuthUser(
            id=str(user.id),
            email=getattr(user, "email", None),
            metadata=getattr(user, "user_metadata", None),
        )
