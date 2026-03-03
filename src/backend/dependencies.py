from repository.db_connector import DBConnector
from repository.habitRepository import HabitRepository
from services.service import Service

db = DBConnector()
repo = HabitRepository(db)
service = Service(repo)
