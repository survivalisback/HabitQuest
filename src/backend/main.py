import fastapi, logging
from fastapi.middleware.cors import CORSMiddleware
from api.habit_api import habitRouter

# Logger Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Configuration
app = fastapi.FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(habitRouter)

logger.info("Backend service initialized successfully.")
