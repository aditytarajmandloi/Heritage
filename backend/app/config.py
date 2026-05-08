import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file from backend root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    groq_api_key: str = ""

    # Paths
    static_dir: str = str(Path(__file__).resolve().parent.parent / "static")
    data_dir: str = str(Path(__file__).resolve().parent.parent / "data")
    chroma_persist_dir: str = str(Path(__file__).resolve().parent.parent / "chroma_data")

    # Server
    app_name: str = "Bengaluru Heritage Explorer"
    debug: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"


# Singleton settings instance
settings = Settings()
