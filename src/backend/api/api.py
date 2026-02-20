import fastapi

router = fastapi.APIRouter()

router.post("/createTask", json={
    "name": str,
    "description": str,
    "frequency": str,
    "difficulty": int,
    "xp_reward": int})
def createTask():
    pass

def editTask():
    pass

def deleteTask():
    pass