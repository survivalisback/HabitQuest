import fastapi
from backend.api.habit_api import habitRouter
from services.service import Service

# API Configuration
app = fastapi.FastAPI()
app.include_router(habitRouter)

service = Service()