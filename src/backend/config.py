from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_config = {"env_file": Path(__file__).resolve().parent / ".env"}

    database_path: Path = Path(__file__).resolve().parents[2] / "db" / "habitquest.db"
    jwt_secret: str = "change-me"
    jwt_issuer: str = "habitquest"
    jwt_expires_in_seconds: int = 60 * 60 * 24
    anthropic_api_key: str
    ai_xp_enabled: bool = False
    ai_model: str = "claude-haiku-4-5-20251001"

settings = Settings()
