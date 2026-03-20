import asyncio, fastapi, logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from api.habit_api import habitRouter
from api.ai_api import aiRouter

# Logger Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def _midnight_reset_loop():
    """Background task that runs cleanup at midnight every day."""
    while True:
        now = datetime.now()
        tomorrow_midnight = (now + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        seconds_until_midnight = (tomorrow_midnight - now).total_seconds()
        await asyncio.sleep(seconds_until_midnight)

        try:
            from repository.db_connector import DBConnector
            db = DBConnector()
            try:
                deleted = db.cleanup_expired_completions()
                logger.info("Midnight reset: cleaned up %d stale completion records.", deleted)
            finally:
                db.close()
        except Exception:
            logger.exception("Midnight reset failed.")


@asynccontextmanager
async def lifespan(app):
    task = asyncio.create_task(_midnight_reset_loop())
    logger.info("Midnight reset scheduler started.")
    yield
    task.cancel()


# API Configuration
app = fastapi.FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(habitRouter)
app.include_router(aiRouter)

logger.info("Backend service initialized successfully.")
