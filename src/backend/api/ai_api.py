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
    description: str = "",
    service: Service = Depends(get_service),
):
    from models.habit import Habit
    habit = Habit(name, description, frequency, 3, 0)

    # Try AI evaluation if enabled
    if settings.ai_xp_enabled and settings.anthropic_api_key:
        from services.ai_client import AiClient
        ai_client = AiClient(settings.anthropic_api_key, settings.ai_model)
        result = ai_client.evaluate_habit(name, description, frequency)
        if result is not None:
            return {
                "difficulty": result["difficulty"],
                "xp": result["xp"],
                "reasoning": result["reasoning"],
                "is_ai": True,
            }

    # Fallback to static
    evaluation = service.xp_provider.evaluate_habit(habit)
    return {
        "difficulty": evaluation["difficulty"],
        "xp": evaluation["xp"],
        "reasoning": "Static calculation based on default difficulty and frequency",
        "is_ai": False,
    }
