VALID_DOMAINS = ['lexical', 'natural_language', 'math']
VALID_DIFFICULTIES = ['L1', 'L2', 'L3']
VALID_GAME_GEN_TYPE = ['static', 'dynamic']
GAMES_SAVE_DIR = 'saved_games'

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

def validate_domain(domain):
    assert domain in VALID_DOMAINS, f'Invalid domain {domain}. Must be one of {VALID_DOMAINS}'

def validate_difficulty(difficulty):
    assert difficulty in VALID_DIFFICULTIES, f'Invalid difficulty {difficulty}. Must be one of {VALID_DIFFICULTIES}'

def validate_num_init_examples(num_init_examples):
    assert num_init_examples >= 1, f'Invalid num_init_examples. Must be >= 1'

def validate_game_gen_type(game_gen_type):
    assert game_gen_type in VALID_GAME_GEN_TYPE, f'Invalid game_gen_type. Must be one of {VALID_GAME_GEN_TYPE}'
