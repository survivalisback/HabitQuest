import fastapi
from fastapi import Depends, HTTPException
from dependencies import get_service
from services.service import Service
from config import settings

aiRouter = fastapi.APIRouter(prefix="/ai")


@aiRouter.post("/preview-xp")
def preview_xp(
    name: str,
    frequency: str,
    difficulty: int,
    description: str = "",
    service: Service = Depends(get_service),
):
    from models.habit import Habit
    habit = Habit(name, description, frequency, difficulty, 0)

    # Try AI evaluation if enabled
    if settings.ai_xp_enabled and settings.anthropic_api_key:
        from services.ai_client import AiClient
        from services.xp_provider import StaticXpProvider
        static_xp = StaticXpProvider().calculate_xp(habit)
        ai_client = AiClient(settings.anthropic_api_key, settings.ai_model)
        result = ai_client.evaluate_habit_xp(name, description, frequency, difficulty, static_xp)
        if result is not None:
            return {"xp": result, "reasoning": "AI-evaluated based on habit details", "is_ai": True}

    # Fallback to static
    xp = service.xp_provider.calculate_xp(habit)
    return {"xp": xp, "reasoning": "Static calculation based on difficulty and frequency", "is_ai": False}
