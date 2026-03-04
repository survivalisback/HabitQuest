from repository.db_connector import DBConnector
from repository.habitRepository import HabitRepository
from services.service import Service
from models.level import Level
from services.xp_provider import StaticXpProvider, DynamicXpProvider

db = DBConnector()
repo = HabitRepository(db)
level = Level()
xp_provider = StaticXpProvider(level)
service = Service(repo)
