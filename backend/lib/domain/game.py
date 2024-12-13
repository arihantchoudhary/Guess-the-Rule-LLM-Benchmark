import os
import random
import json

from lib.domain.base import validate_domain, validate_game_gen_type
from lib.domain.picnic.static_picnic.base import StaticGoingOnAPicnic
from lib.domain.picnic.function_picnic.base import LexicalFunctionGame
from lib.domain.picnic.dynamic_picnic.base import DynamicGoingOnAPicnic
from lib.domain.common import GAMES_SAVE_DIR

def select_natural_language_game(game_gen_type):
    if game_gen_type == 'static':
        return random.choice ([
            StaticGoingOnAPicnic
        ])
    else:
        return random.choice ([
            DynamicGoingOnAPicnic,
            # LexicalFunctionGame
        ])

def select_new_game(domain, game_gen_type):
    validate_domain(domain)
    validate_game_gen_type(game_gen_type)

    if domain == 'natural_language':
        return select_natural_language_game(game_gen_type)


def get_existing_game(uuid):
    filename = os.path.join(GAMES_SAVE_DIR, f"{uuid}.json")
    with open(filename) as f:
        saved_game = json.load(f)
        game_class_name = saved_game['game_class_name']
    
    if game_class_name == 'StaticGoingOnAPicnic':
        return StaticGoingOnAPicnic(uuid=uuid)
