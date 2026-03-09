import fastapi
from dependencies import service

habitRouter = fastapi.APIRouter()

@habitRouter.post("/createTask")
def create_task(name: str, description: str, frequency: str, difficulty: int):
    service.create_habit(name, description, frequency, difficulty)

@habitRouter.put("/editTask")
def edit_task(id: int, name: str, description: str, frequency: str, difficulty: int):
    service.edit_habit(id, name, description, frequency, difficulty)

@habitRouter.delete("/deleteTask")
def delete_task(id: int):
    service.delete_habit(id)

@habitRouter.post("/toggleTaskCompletion")
def toggle_habit_completion(id: int):
    completed = service.toggle_habit_completion(id)
    return {"habit_id": id, "completed": completed}

# TODO: Get habit_id in frontend or does it come with the habit object?
