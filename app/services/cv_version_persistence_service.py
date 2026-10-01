from typing import Any, Dict, List, Optional
from uuid import UUID

from app.services.supabase_service import supabase


class CVVersionPersistenceService:

    TABLE_NAME = "cv_versions"

    @staticmethod
    def _dump(value: Any) -> Dict[str, Any]:
        if hasattr(value, "model_dump"):
            return value.model_dump(mode="json")

        if isinstance(value, dict):
            return dict(value)

        raise ValueError(
            "Professional CV must be a Pydantic model or dictionary."
        )

    def create_version(
        self,
        cv_id: UUID,
        professional_cv: Any,
        label: str = "",
    ) -> dict:

        existing = (
            supabase
            .table(self.TABLE_NAME)
            .select("version_number")
            .eq("cv_id", str(cv_id))
            .order("version_number", desc=True)
            .limit(1)
            .execute()
        )

        latest = 0

        if existing.data:
            latest = int(existing.data[0]["version_number"])

        version_number = latest + 1

        row = {
            "cv_id": str(cv_id),
            "version_number": version_number,
            "label": label or f"CV Version {version_number}",
            "professional_cv": self._dump(professional_cv),
        }

        response = (
            supabase
            .table(self.TABLE_NAME)
            .insert(row)
            .execute()
        )

        if not response.data:
            raise RuntimeError("CV version creation failed.")

        return response.data[0]

    def list_versions(self, cv_id: UUID) -> List[dict]:

        response = (
            supabase
            .table(self.TABLE_NAME)
            .select("*")
            .eq("cv_id", str(cv_id))
            .order("version_number", desc=True)
            .execute()
        )

        return response.data or []

    def get_version(
        self,
        cv_id: UUID,
        version_number: int,
    ) -> Optional[dict]:

        response = (
            supabase
            .table(self.TABLE_NAME)
            .select("*")
            .eq("cv_id", str(cv_id))
            .eq("version_number", version_number)
            .limit(1)
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]

    def restore_version(
        self,
        cv_id: UUID,
        version_number: int,
    ) -> Optional[dict]:

        return self.get_version(
            cv_id,
            version_number,
        )


cv_version_persistence_service = CVVersionPersistenceService()
