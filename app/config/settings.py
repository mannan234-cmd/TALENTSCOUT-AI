import os

from dotenv import load_dotenv


# ============================================================
# TalentScout AI - Application Settings
# ============================================================

PROJECT_ROOT = "/content/drive/MyDrive/TalentScout_AI"

ENV_PATH = os.path.join(
    PROJECT_ROOT,
    ".env"
)

# Load environment variables
load_dotenv(
    dotenv_path=ENV_PATH,
    override=True
)


class Settings:
    """
    Central application configuration.
    """

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    SUPABASE_URL = os.getenv("SUPABASE_URL")

    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    GROQ_MODEL = "openai/gpt-oss-120b"


settings = Settings()
