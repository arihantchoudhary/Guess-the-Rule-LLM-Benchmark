from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid

# Import your existing functions
from dynamic_rule_generator import (
    request_game_instance,
    request_more_examples,
    request_guess_validation,
)

app = FastAPI()

# Model for creating a game instance
class GameRequest(BaseModel):
    domain: str = None
    difficulty: str = None
    init_examples: str = None
    use_llm: bool = False

# Model for guess validation
class GuessRequest(BaseModel):
    game_id: uuid.UUID
    guess: str

@app.post("/create_game/")
async def create_game(game_request: GameRequest):
    """Create a new game instance."""
    try:
        game_id = request_game_instance(
            domain=game_request.domain,
            difficulty=game_request.difficulty,
            init_examples=game_request.init_examples,
            use_llm=game_request.use_llm
        )
        return {"game_id": game_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/examples/{game_id}")
async def get_more_examples(game_id: uuid.UUID, n_examples: int = 5):
    """Get more examples from the game."""
    try:
        examples = request_more_examples(game_id, n_examples=n_examples)
        return {"examples": examples}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/validate_guess/")
async def validate_guess(guess_request: GuessRequest):
    """Validate a guess against the game instance."""
    try:
        is_correct = request_guess_validation(guess_request.game_id, guess_request.guess)
        return {"is_correct": is_correct}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Run the application (only if running directly, otherwise use Uvicorn from CLI)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)