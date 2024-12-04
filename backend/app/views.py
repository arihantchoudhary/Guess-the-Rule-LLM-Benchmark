from fastapi import FastAPI, HTTPException

from lib.models import CreateGame, ValidateGuess
from lib.domain.game import select_new_game, get_existing_game

app = FastAPI()

@app.post("/guess-the-rule/game")
def create_game(payload: CreateGame):
    """Create a new game instance."""
    try:
        cls = select_new_game(payload.domain)
        return cls(
            domain=payload.domain,
            difficulty=payload.difficulty,
            num_init_examples=payload.num_init_examples,
            game_gen_type=payload.game_gen_type
        ).create_game_instance()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/guess-the-rule/game/{game_id}")
def validate_guess(game_id: str, include_rule=False):
    """Get the summary of a game."""
    try:
        cls = get_existing_game(game_id)
        restored_game = cls.load_game()
        return restored_game.get_game_summary(include_rule=include_rule)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/guess-the-rule/game/{game_id}/examples")
def get_more_examples(game_id: str, n_examples: int):
    """Get more examples from the game."""
    try:
        cls = get_existing_game(game_id)
        restored_game = cls.load_game()
        return restored_game.get_more_examples(n_examples)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/guess-the-rule/game/validate_guess")
def validate_guess(payload: ValidateGuess):
    """Validate a guess against the game instance."""
    try:
        cls = get_existing_game(payload.game_id)
        restored_game = cls.load_game()
        return restored_game.validate_guess(payload.guess)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
