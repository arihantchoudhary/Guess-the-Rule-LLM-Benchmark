import os 

VALID_DOMAINS = ['lexical', 'natural_language', 'math']
VALID_DIFFICULTIES = ['L1', 'L2', 'L3']
VALID_GAME_GEN_TYPE = ['static', 'dynamic']

def safe_lowercase(s):
    if isinstance(s, str):
        return s.lower()
    else:
        return s

def safe_uppercase(s):
    if isinstance(s, str):
        return s.upper()
    else:
        return s

def safe_int(i):
    try:
        return int(i)
    except Exception:
        return None

class GuessTheRuleGame:
    SAVE_DIR = 'saved_games'

    def __init__(self, uuid=None, domain=None, difficulty=None, num_init_examples=None, game_gen_type=None):
        if not os.path.exists(self.SAVE_DIR):
            os.makedirs(self.SAVE_DIR)

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
            assert self.domain in VALID_DOMAINS, f'Invalid domain {self.domain}. Must be one of {VALID_DOMAINS}'
            assert self.difficulty in VALID_DIFFICULTIES, f'Invalid difficulty {self.difficulty}. Must be one of {VALID_DIFFICULTIES}'
            assert self.num_init_examples >= 1, f'Invalid num_init_examples. Must be >= 1'
            assert self.game_gen_type in VALID_GAME_GEN_TYPE, f'Invalid game_gen_type. Must be one of {VALID_GAME_GEN_TYPE}'

    @classmethod
    def load_game(self):
        raise NotImplementedError('Method not implemented for this game')

    def create_game_instance(self):
        raise NotImplementedError('Method not implemented for this game')

    def get_more_examples(self):
        raise NotImplementedError('Method not implemented for this game')

    def validate_guess(self):
        raise NotImplementedError('Method not implemented for this game')
