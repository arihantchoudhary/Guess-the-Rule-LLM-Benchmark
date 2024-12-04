import os
 
from lib.domain.common import (
    safe_lowercase, safe_uppercase, safe_int,
    validate_domain, validate_difficulty, validate_num_init_examples, validate_game_gen_type,
    GAMES_SAVE_DIR
)

class GuessTheRuleGame:

    def __init__(self, uuid=None, domain=None, difficulty=None, num_init_examples=None, game_gen_type=None):
        if not os.path.exists(GAMES_SAVE_DIR):
            os.makedirs(GAMES_SAVE_DIR)

        self.uuid = uuid
        self.domain = safe_lowercase(domain)
        self.difficulty = safe_uppercase(difficulty)
        self.num_init_examples = safe_int(num_init_examples)
        self.game_gen_type = safe_lowercase(game_gen_type)
        self.validate_init()

    def validate_init(self):
        assert self.uuid or (self.domain and self.difficulty and self.num_init_examples and self.game_gen_type), \
            f'Must pass either uuid or (domain, difficulty, num_init_examples, game_gen_type)'

        if not self.uuid:
            validate_domain(self.domain)
            validate_difficulty(self.difficulty)
            validate_num_init_examples(self.num_init_examples)
            validate_game_gen_type(self.game_gen_type)

    def load_game(self):
        raise NotImplementedError('Method not implemented for this game')

    def create_game_instance(self):
        raise NotImplementedError('Method not implemented for this game')

    def get_more_examples(self):
        raise NotImplementedError('Method not implemented for this game')

    def validate_guess(self):
        raise NotImplementedError('Method not implemented for this game')
