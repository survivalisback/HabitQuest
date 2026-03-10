import fastapi
from dependencies import service

habitRouter = fastapi.APIRouter()

@habitRouter.post("/login")
def login(user_id: int, username: str | None = None):
    service.login_user(user_id, username)
    return {"user_id": user_id, "username": username}

@habitRouter.get("/habits")
def get_habits(user_id: int):
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
def create_task(user_id: int, name: str, description: str, frequency: str, difficulty: int):
    service.create_habit(user_id, name, description, frequency, difficulty)

@habitRouter.put("/editTask")
def edit_task(user_id: int, id: int, name: str, description: str, frequency: str, difficulty: int):
    service.edit_habit(user_id, id, name, description, frequency, difficulty)

@habitRouter.delete("/deleteTask")
def delete_task(user_id: int, id: int):
    service.delete_habit(user_id, id)

@habitRouter.post("/toggleTaskCompletion")
def toggle_habit_completion(user_id: int, id: int):
    completed = service.toggle_habit_completion(user_id, id)
    return {"habit_id": id, "completed": completed}

# TODO: Get habit_id in frontend or does it come with the habit object?
