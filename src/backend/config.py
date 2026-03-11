from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_path: Path = Path(__file__).resolve().parents[2] / "db" / "habitquest.db"
    jwt_secret: str = "change-me"
    jwt_issuer: str = "habitquest"
    jwt_expires_in_seconds: int = 60 * 60 * 24

settings = Settings()
