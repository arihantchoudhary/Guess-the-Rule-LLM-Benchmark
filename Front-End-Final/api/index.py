from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
# import game_logic
import random
import json
import string
import os
from openai import OpenAI
from dotenv import load_dotenv

# FastAPI instance
app = FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow requests from your frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (POST, GET, etc.)
    allow_headers=["*"],  # Allow all headers
)
os.chdir("api")

# Load items and counts data
with open('open_images_combined_items.json', 'r') as file:
    items = json.load(file)

# Load individual, pair, and triplet counts from JSON files
with open('pp_individual_counts.json', 'r') as file:
    l1_counts = json.load(file)
    l1_counts = {tuple(eval(key)): value for key, value in l1_counts.items()}

with open('pp_pairs_counts.json', 'r') as file:
    l2_counts = json.load(file)
    l2_counts = {tuple(eval(key)): value for key, value in l2_counts.items()}

with open('pp_triplets_counts.json', 'r') as file:
    l3_counts = json.load(file)
    l3_counts = {tuple(eval(key)): value for key, value in l3_counts.items()}

# Categorize individuals, pairs, and triplets based on count thresholds
L1_individuals = [key[0] for key, count in l1_counts.items() if count > 6]
L2_individuals = [key[0] for key, count in l1_counts.items() if 4 <= count <= 6]
L3_individuals = [key[0] for key, count in l1_counts.items() if 2 <= count < 4]

L2_pairs = [pair for pair, count in l2_counts.items() if count > 6]
L3_pairs = [pair for pair, count in l2_counts.items() if 2 <= count < 6]
L3_triplets = [triplet for triplet, count in l3_counts.items() if count > 2]  # Exclude triplets with ≤ 2 examples


# Example request model
class GameRequest(BaseModel):
    gameType: str
    selectedModels: List[str]
    difficulty: str
    humanModeEnabled: bool

@app.get("/")
@app.get("/api/py/helloFastApi")
def hello_fast_api():
    return {"message": "Hello from FastAPI"}

@app.post("/api/start-game")
def start_game(request: GameRequest):
    # Game logic (replace this with actual game functionality)
    print(f"GameType: {request.gameType}, Difficulty: {request.difficulty}, Models: {request.selectedModels}")
    difficulty = request.difficulty
    def pick_rule(difficulty):
        if difficulty == "Easy":
            return random.choice(L1_individuals)
        elif difficulty == "Medium":
            return random.choice([random.choice(L2_pairs), random.choice(L2_individuals)]) 
        else:
            return random.choice([random.choice(L3_triplets), random.choice(L3_pairs), random.choice(L3_individuals)])
    
    rule = pick_rule(difficulty)

    return {"message": f"Game started with type {request.gameType} on {request.difficulty} difficulty"}

