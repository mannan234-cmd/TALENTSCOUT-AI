from __future__ import annotations

import os

from supabase import Client, create_client

from app.config.settings import settings


class SupabaseService:
    """Supabase clients with an explicit security boundary."""

    def __init__(self):
        if not settings.SUPABASE_URL:
            raise ValueError("SUPABASE_URL is not configured.")

        if not settings.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY is not configured.")

        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY,
        )

    @property
    def supabase(self) -> Client:
        """Normal application client using Auth + RLS."""
        return self.client

    @property
    def admin_client(self) -> Client:
        """
        Service-role client.

        Use ONLY for trusted backend/admin operations.
        Never use this for normal user-facing CRUD.
        """
        service_role_key = getattr(
            settings,
            "SUPABASE_SERVICE_ROLE_KEY",
            None,
        ) or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not service_role_key:
            raise ValueError(
                "SUPABASE_SERVICE_ROLE_KEY is required "
                "for admin operations."
            )

        return create_client(
            settings.SUPABASE_URL,
            service_role_key,
        )


supabase_service = SupabaseService()

supabase = supabase_service.client
