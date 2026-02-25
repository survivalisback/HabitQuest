import fastapi
from backend.api.habit_api import habitRouter
from services.service import Service
from repository.db_connector import DBConnector
from repository.habitRepository import HabitRepository

# API Configuration
app = fastapi.FastAPI()
app.include_router(habitRouter)

db = DBConnector()
repo = HabitRepository(db)
service = Service(repo)