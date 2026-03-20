from collections.abc import Generator
from repository.db_connector import DBConnector
from repository.habitRepository import HabitRepository
from repository.user_repository import UserRepository
from services.service import Service
from services.xp_provider import StaticXpProvider, DynamicXpProvider
from services.streak_service import StreakService
from config import settings


def get_service() -> Generator[Service, None, None]:
    db = DBConnector()
    try:
        habit_repo = HabitRepository(db)
        user_repo = UserRepository(db)
        streak_service = StreakService(db)

        static_provider = StaticXpProvider()
        if settings.ai_xp_enabled and settings.anthropic_api_key:
            from services.ai_client import AiClient
            ai_client = AiClient(settings.anthropic_api_key, settings.ai_model)
            xp_provider = DynamicXpProvider(ai_client, static_provider)
        else:
            xp_provider = static_provider

        service = Service(habit_repo, user_repo, xp_provider, streak_service)
        yield service
    finally:
        db.close()
