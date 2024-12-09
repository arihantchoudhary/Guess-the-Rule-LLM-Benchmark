from pydantic import BaseModel


class CreateGame(BaseModel):
    domain: str
    difficulty: str
<<<<<<< HEAD
=======
    player: str
>>>>>>> 6dc61c65e62dc10f25ee246d7e3a613bf640d6ad
    num_init_examples: str
    game_gen_type: str

# Model for guess validation
class ValidateGuess(BaseModel):
    game_id: str
    guess: str
