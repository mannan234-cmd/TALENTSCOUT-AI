
import os

from supabase import create_client, Client

from app.config.settings import settings


class SupabaseService:
    def __init__(self):
        if not settings.SUPABASE_URL:
            raise ValueError(
                "SUPABASE_URL is not configured."
            )

        # Backend/server-side Supabase secret.
        # Never hard-code this into the project.
        server_key = os.getenv(
            "SUPABASE_SERVICE_ROLE_KEY"
        )

        # Backward-compatible fallback.
        #
        # Existing local development can continue using
        # SUPABASE_KEY when no server-side secret is present.
        if server_key:
            key = server_key
            self.key_source = "server_secret"
        else:
            if not settings.SUPABASE_KEY:
                raise ValueError(
                    "SUPABASE_KEY is not configured."
                )

            key = settings.SUPABASE_KEY
            self.key_source = "configured_key"

        self.client: Client = create_client(
            settings.SUPABASE_URL,
            key,
        )

    @property
    def supabase(self) -> Client:
        return self.client


supabase_service = SupabaseService()
supabase = supabase_service.client
