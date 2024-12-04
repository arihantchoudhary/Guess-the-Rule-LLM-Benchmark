from pydantic import BaseModel


class CreateGame(BaseModel):
    domain: str
    difficulty: str
    num_init_examples: str
    game_gen_type: str

# Model for guess validation
class ValidateGuess(BaseModel):
    game_id: str
    guess: str
