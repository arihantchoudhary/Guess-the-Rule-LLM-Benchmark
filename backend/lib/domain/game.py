import os
import json

from lib.domain.picnic.static_picnic.base import StaticGoingOnAPicnic
from lib.domain.picnic.function_picnic.base import CodeFunctionsPicnic
from lib.domain.math_game.base import MathGuessTheRuleGame
from lib.domain.picnic.dynamic_picnic.base import DynamicGoingOnAPicnic
from lib.domain.common import GAMES_SAVE_DIR


def select_new_game(game_name):
    if game_name == 'static_picnic':
        return StaticGoingOnAPicnic
    if game_name == 'dynamic_picnic':
        return DynamicGoingOnAPicnic
    if game_name == 'code_functions_picnic':
        return CodeFunctionsPicnic
    if game_name == 'math':
        return MathGuessTheRuleGame
    assert False, f'Could not find a game with name {game_name}'


def get_existing_game(uuid):
    filename = os.path.join(GAMES_SAVE_DIR, f"{uuid}.json")
    with open(filename) as f:
        saved_game = json.load(f)
        game_class_name = saved_game['game_class_name']
    
    if game_class_name == 'StaticGoingOnAPicnic':
        return StaticGoingOnAPicnic(uuid=uuid)

    if game_class_name == 'DynamicGoingOnAPicnic':
        return DynamicGoingOnAPicnic(uuid=uuid)
    
    if game_class_name == 'MathGuessTheRuleGame':
        return MathGuessTheRuleGame(uuid=uuid)
