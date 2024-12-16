from pydantic import BaseModel


class CreateGame(BaseModel):
    game_name: str
    difficulty: str
    player: str
    num_init_examples: str

# Model for guess validation
class ValidateGuess(BaseModel):
    game_id: str
    guess: str
