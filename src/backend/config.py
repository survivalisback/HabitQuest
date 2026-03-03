from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_path: Path = Path(__file__).resolve().parents[2] / "db" / "habitquest.db"

settings = Settings()
