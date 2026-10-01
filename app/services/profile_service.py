from typing import Optional
from uuid import UUID

from app.models.profile import StudentProfile
from app.services.supabase_service import supabase


class ProfileService:

    TABLE_NAME = "profiles"

    # ========================================================
    # CREATE PROFILE
    # ========================================================

    def create_profile(
        self,
        profile: StudentProfile
    ) -> dict:

        profile_data = (
            profile
            .model_dump(
                exclude_none=True,
                mode="json"
            )
        )

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

    # ========================================================
    # GET PROFILE
    # ========================================================

    def get_profile(
        self,
        profile_id: UUID
    ) -> Optional[dict]:

        response = (
            supabase
            .table(self.TABLE_NAME)
            .select("*")
            .eq(
                "id",
                str(profile_id)
            )
            .limit(1)
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    # ========================================================
    # UPDATE PROFILE
    # ========================================================

    def update_profile(
        self,
        profile_id: UUID,
        profile: StudentProfile
    ) -> Optional[dict]:

        profile_data = (
            profile
            .model_dump(
                exclude_none=True,
                mode="json"
            )
        )

        response = (
            supabase
            .table(self.TABLE_NAME)
            .update(profile_data)
            .eq(
                "id",
                str(profile_id)
            )
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    # ========================================================
    # DELETE PROFILE
    # ========================================================

    def delete_profile(
        self,
        profile_id: UUID
    ) -> bool:

        response = (
            supabase
            .table(self.TABLE_NAME)
            .delete()
            .eq(
                "id",
                str(profile_id)
            )
            .execute()
        )

        return bool(response.data)


# ============================================================
# SERVICE INSTANCE
# ============================================================

profile_service = ProfileService()
