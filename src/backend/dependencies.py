from collections.abc import Generator
from repository.db_connector import DBConnector
from repository.habitRepository import HabitRepository
from services.service import Service
from models.level import Level
from services.xp_provider import StaticXpProvider

def get_service() -> Generator[Service, None, None]:
    db = DBConnector()
    try:
        repo = HabitRepository(db)
        level = Level()
        xp_provider = StaticXpProvider(level)
        service = Service(repo, xp_provider)
        yield service
    finally:
        db.close()
