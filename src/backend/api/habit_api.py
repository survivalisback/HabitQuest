import fastapi

habitRouter = fastapi.APIRouter()

@habitRouter.post("/createTask")
def create_task(name: str, description: str, frequency: str, difficulty: int, xp_reward: int):
    pass

@habitRouter.put("/editTask")
def edit_task(id: int, name: str, description: str, frequency: str, difficulty: int, xp_reward: int):
    pass

@habitRouter.delete("/deleteTask")
def delete_task(id: int):
    pass

@habitRouter.post("/toggleTaskCompletion")
def toggle_task_completion(id: int):
    pass