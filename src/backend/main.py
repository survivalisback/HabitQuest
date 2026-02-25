import fastapi, logging
from backend.api.habit_api import habitRouter
from services.service import Service
from repository.db_connector import DBConnector
from repository.habitRepository import HabitRepository

# Logger Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Configuration
app = fastapi.FastAPI()
app.include_router(habitRouter)

db = DBConnector()
repo = HabitRepository(db)
service = Service(repo)

logger.info("Backend service initialized successfully.")