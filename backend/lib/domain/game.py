import os
import random
import json

from lib.domain.base import validate_domain
from lib.domain.picnic.static_picnic.base import StaticGoingOnAPicnic
from lib.domain.picnic.function_picnic.base import LexicalFunctionGame
from lib.domain.common import GAMES_SAVE_DIR

def select_natural_language_game():
    natural_language_games = [
        StaticGoingOnAPicnic,
        LexicalFunctionGame
    ]
    return random.choice(natural_language_games)

def select_new_game(domain):
    validate_domain(domain)

    if domain == 'natural_language':
        return select_natural_language_game()
    
    # TODO: add the other games from @Juno and @Michael

def get_existing_game(uuid):
    filename = os.path.join(GAMES_SAVE_DIR, f"{uuid}.json")
    with open(filename) as f:
        saved_game = json.load(f)
        game_class_name = saved_game['game_class_name']
    
    if game_class_name == 'StaticGoingOnAPicnic':
        return StaticGoingOnAPicnic(uuid=uuid)
