import fastapi
from fastapi import Depends, HTTPException
from dependencies import get_service
from services.service import Service

habitRouter = fastapi.APIRouter()

@habitRouter.post("/login")
def login(username: str, password: str, service: Service = Depends(get_service)):
    try:
        return service.login_user(username, password)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

@habitRouter.post("/register")
def register(username: str, password: str, service: Service = Depends(get_service)):
    try:
        return service.register_user(username, password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

def _get_user_id_from_token(token: str, service: Service) -> int:
    try:
        return service.get_user_id_from_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

@habitRouter.get("/habits")
def get_habits(
    authorization: str = fastapi.Header(..., alias="Authorization"),
    service: Service = Depends(get_service),
):
    user_id = _get_user_id_from_token(authorization, service)
    habits = service.get_habits(user_id)
    return [
        {
            "id": habit.id,
            "user_id": habit.user_id,
            "name": habit.name,
            "description": habit.description,
            "frequency": habit.frequency,
            "difficulty": habit.difficulty,
            "xp_reward": habit.xp_reward,
        }
        for habit in habits
    ]

@habitRouter.post("/createTask")
def create_task(
    name: str,
    description: str,
    frequency: str,
    difficulty: int,
    authorization: str = fastapi.Header(..., alias="Authorization"),
    service: Service = Depends(get_service),
):
    user_id = _get_user_id_from_token(authorization, service)
    service.create_habit(user_id, name, description, frequency, difficulty)

@habitRouter.put("/editTask")
def edit_task(
    id: int,
    name: str,
    description: str,
    frequency: str,
    difficulty: int,
    authorization: str = fastapi.Header(..., alias="Authorization"),
    service: Service = Depends(get_service),
):
    user_id = _get_user_id_from_token(authorization, service)
    service.edit_habit(user_id, id, name, description, frequency, difficulty)

@habitRouter.delete("/deleteTask")
def delete_task(
    id: int,
    authorization: str = fastapi.Header(..., alias="Authorization"),
    service: Service = Depends(get_service),
):
    user_id = _get_user_id_from_token(authorization, service)
    service.delete_habit(user_id, id)

@habitRouter.post("/toggleTaskCompletion")
def toggle_habit_completion(
    id: int,
    authorization: str = fastapi.Header(..., alias="Authorization"),
    service: Service = Depends(get_service),
):
    user_id = _get_user_id_from_token(authorization, service)
    completed = service.toggle_habit_completion(user_id, id)
    return {"habit_id": id, "completed": completed}

# TODO: Get habit_id in frontend or does it come with the habit object?
