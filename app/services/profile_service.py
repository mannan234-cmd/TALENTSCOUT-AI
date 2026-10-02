from __future__ import annotations

from typing import Optional
from uuid import UUID

from app.models.profile import StudentProfile
from app.services.supabase_service import supabase


class ProfileService:
    """Ownership-aware CRUD for the authenticated user's profile."""

    TABLE_NAME = "profiles"

    @staticmethod
    def _current_user_id() -> str:
        try:
            response = supabase.auth.get_user()
        except Exception as exc:
            raise RuntimeError(
                "Unable to determine the authenticated user."
            ) from exc

        user = getattr(response, "user", None)

        if user is None or not getattr(user, "id", None):
            raise PermissionError(
                "An authenticated user is required."
            )

        return str(user.id)

    @staticmethod
    def _profile_payload(profile: StudentProfile) -> dict:
        return profile.model_dump(
            exclude_none=True,
            mode="json",
        )

    def get_current_profile(self) -> Optional[dict]:
        user_id = self._current_user_id()

        response = (
            supabase
            .table(self.TABLE_NAME)
            .select("*")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )

        return response.data[0] if response.data else None

    def create_profile(
        self,
        profile: StudentProfile,
    ) -> dict:

        user_id = self._current_user_id()

        profile_data = self._profile_payload(profile)

        # Always attach the authenticated user.
        profile_data["user_id"] = user_id

        response = (
            supabase
            .table(self.TABLE_NAME)
            .insert(profile_data)
            .execute()
        )

        if not response.data:
            raise RuntimeError(
                "Profile creation failed: "
                "Supabase returned no data."
            )

        return response.data[0]

    def get_profile(
        self,
        profile_id: UUID,
    ) -> Optional[dict]:

        user_id = self._current_user_id()

        response = (
            supabase
            .table(self.TABLE_NAME)
            .select("*")
            .eq("id", str(profile_id))
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )

        return response.data[0] if response.data else None

    def update_profile(
        self,
        profile_id: UUID,
        profile: StudentProfile,
    ) -> Optional[dict]:

        user_id = self._current_user_id()

        profile_data = self._profile_payload(profile)

        # Never allow ownership transfer.
        profile_data.pop("user_id", None)

        response = (
            supabase
            .table(self.TABLE_NAME)
            .update(profile_data)
            .eq("id", str(profile_id))
            .eq("user_id", user_id)
            .execute()
        )

        return response.data[0] if response.data else None

    def delete_profile(
        self,
        profile_id: UUID,
    ) -> bool:

        user_id = self._current_user_id()

        response = (
            supabase
            .table(self.TABLE_NAME)
            .delete()
            .eq("id", str(profile_id))
            .eq("user_id", user_id)
            .execute()
        )

        return bool(response.data)


profile_service = ProfileService()
