<<<<<<< HEAD
from fastapi import FastAPI, HTTPException
=======
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
>>>>>>> 6dc61c65e62dc10f25ee246d7e3a613bf640d6ad

from lib.models import CreateGame, ValidateGuess
from lib.domain.game import select_new_game, get_existing_game

<<<<<<< HEAD
app = FastAPI()

@app.post("/guess-the-rule/game")
=======
# Initialize logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

app = FastAPI()

# Allow requests from localhost:8080 (your frontend URL)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods like POST, GET, DELETE, OPTIONS
    allow_headers=["*"],  # Allow all headers like Content-Type, Authorization, etc.
)

# Logging Middleware
@app.middleware("http")
def log_request(request: Request, call_next):
    logging.info(f"Request URL: {request.method} {request.url}")

    query_params = dict(request.query_params)
    if query_params:
        logging.info(f"Query Parameters: {query_params}")

    return call_next(request)

@app.post("/guess-the-rule/game")
@app.options("/guess-the-rule/game")
>>>>>>> 6dc61c65e62dc10f25ee246d7e3a613bf640d6ad
def create_game(payload: CreateGame):
    """Create a new game instance."""
    try:
        cls = select_new_game(payload.domain)
<<<<<<< HEAD
        return cls(
=======
        res = cls(
>>>>>>> 6dc61c65e62dc10f25ee246d7e3a613bf640d6ad
            domain=payload.domain,
            difficulty=payload.difficulty,
            num_init_examples=payload.num_init_examples,
            game_gen_type=payload.game_gen_type
        ).create_game_instance()
<<<<<<< HEAD
=======
        logging.info(f"Response: {res}")
        return res
>>>>>>> 6dc61c65e62dc10f25ee246d7e3a613bf640d6ad
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/guess-the-rule/game/{game_id}")
def validate_guess(game_id: str, include_rule=False):
    """Get the summary of a game."""
    try:
        cls = get_existing_game(game_id)
        restored_game = cls.load_game()
<<<<<<< HEAD
        return restored_game.get_game_summary(include_rule=include_rule)
=======
        res = restored_game.get_game_summary(include_rule=include_rule)
        logging.info(f"Response: {res}")
        return res
>>>>>>> 6dc61c65e62dc10f25ee246d7e3a613bf640d6ad
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/guess-the-rule/game/{game_id}/examples")
def get_more_examples(game_id: str, n_examples: int):
    """Get more examples from the game."""
    try:
        cls = get_existing_game(game_id)
        restored_game = cls.load_game()
<<<<<<< HEAD
        return restored_game.get_more_examples(n_examples)
=======
        res = restored_game.get_more_examples(n_examples)
        logging.info(f"Response: {res}")
        return res
>>>>>>> 6dc61c65e62dc10f25ee246d7e3a613bf640d6ad
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/guess-the-rule/game/validate_guess")
def validate_guess(payload: ValidateGuess):
    """Validate a guess against the game instance."""
    try:
        cls = get_existing_game(payload.game_id)
        restored_game = cls.load_game()
<<<<<<< HEAD
        return restored_game.validate_guess(payload.guess)
=======
        res = restored_game.validate_guess(payload.guess)
        logging.info(f"Response: {res}")
        return res
>>>>>>> 6dc61c65e62dc10f25ee246d7e3a613bf640d6ad
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
