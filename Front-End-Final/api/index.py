# api/index.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

# FastAPI instance
app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")

# Example request model
class GameRequest(BaseModel):
    gameType: str
    selectedModels: List[str]
    difficulty: str
    humanModeEnabled: bool

@app.get("/api/py/helloFastApi")
def hello_fast_api():
    return {"message": "Hello from FastAPI"}

@app.post("/api/start-game")
def start_game(request: GameRequest):
    # Game logic (replace this with actual game functionality)
    return {"message": f"Game started with type {request.gameType} on {request.difficulty} difficulty"}
