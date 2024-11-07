import os
import random
import uuid
from openai import OpenAI
from .guessing_game import GuessingGame

# Set your OpenAI API key
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_KEY:
    client = OpenAI(api_key=OPENAI_KEY)

# Dictionary to store active game instances
games = {}

# Function to initialize a new game
def start_new_game(gameType, selectedModels, difficulty, humanModeEnabled):
    """
    Initializes a new GuessingGame instance and stores it in the games dictionary.
    """
    game_id = uuid.uuid4()
    rng_state = random.getstate()
    init_examples = None  # Specify init examples if needed

    # Create a new game instance
    game = GuessingGame(
        rngstate=rng_state,
        domain=gameType,
        difficulty=difficulty,
        init_examples=init_examples,
        use_llm=humanModeEnabled
    )

    # Store the game instance
    games[game_id] = game

    # Return the game ID and a starting message
    return game_id, "Game started! " + game.start_message()

def get_more_examples(game_id, n_examples=5):
    """
    Retrieves more examples for a given game.
    """
    if game_id not in games:
        raise Exception("Invalid game ID!")

    game = games[game_id]
    examples = [game.generate_example() for _ in range(n_examples)]
    return examples

def validate_guess(game_id, guess):
    """
    Validates a guess for a given game.
    """
    if game_id not in games:
        raise Exception("Invalid game ID!")

    game = games[game_id]
    return game.validate_guess(guess)

def end_game(game_id):
    """
    Ends and removes a game instance.
    """
    if game_id in games:
        del games[game_id]
        return "Game ended successfully."
    else:
        raise Exception("Invalid game ID!")
