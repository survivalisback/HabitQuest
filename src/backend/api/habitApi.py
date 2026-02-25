import fastapi

habitRouter = fastapi.APIRouter()

@habitRouter.post("/createTask")
def createTask(name: str, description: str, frequency: str, difficulty: int, xp_reward: int):
    pass

@habitRouter.put("/editTask")
def editTask(id: int, name: str, description: str, frequency: str, difficulty: int, xp_reward: int):
    pass

@habitRouter.delete("/deleteTask")
def deleteTask(id: int):
    pass

@habitRouter.post("/toggleTaskCompletion")
def toggleTaskCompletion(id: int):
    pass