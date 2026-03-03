import fastapi, logging
from api.habit_api import habitRouter
from dependencies import service

# Logger Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Configuration
app = fastapi.FastAPI()
app.include_router(habitRouter)

logger.info("Backend service initialized successfully.")
