from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class CVVersionService:

    @staticmethod
    def create_version(
        versions: Optional[List[Dict[str, Any]]],
        professional_cv: Any,
        label: Optional[str] = None,
    ) -> Dict[str, Any]:

        current_versions = list(versions or [])

        cv_data = (
            professional_cv.model_dump(mode="json")
            if hasattr(professional_cv, "model_dump")
            else dict(professional_cv)
        )

        version_number = len(current_versions) + 1

        version = {
            "version": version_number,
            "label": label or f"CV Version {version_number}",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "cv": cv_data,
        }

        current_versions.append(version)

        return version

    @staticmethod
    def list_versions(
        versions: Optional[List[Dict[str, Any]]],
    ) -> List[Dict[str, Any]]:
        return list(versions or [])

    @staticmethod
    def get_version(
        versions: Optional[List[Dict[str, Any]]],
        version_number: int,
    ) -> Optional[Dict[str, Any]]:

        for version in versions or []:
            if version.get("version") == version_number:
                return version

        return None


cv_version_service = CVVersionService()
