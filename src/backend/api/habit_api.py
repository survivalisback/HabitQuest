import fastapi
from ..main import service

habitRouter = fastapi.APIRouter()

@habitRouter.post("/createTask")
def create_task(name: str, description: str, frequency: str, difficulty: int):
    service.create_habit(name, description, frequency, difficulty)

@habitRouter.put("/editTask")
def edit_task(id: int, name: str, description: str, frequency: str, difficulty: int):
    pass

@habitRouter.delete("/deleteTask")
def delete_task(id: int):
    pass

@habitRouter.post("/toggleTaskCompletion")
def toggle_task_completion(id: int):
    pass

# TODO: Get habit_id in frontend or does it come with the habit object?