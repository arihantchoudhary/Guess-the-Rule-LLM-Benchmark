import os
import json
import uuid
import random
import time

from openai import OpenAI
import openai
import anthropic
from retry import retry
import logging

from lib.domain.base import GuessTheRuleGame
from lib.domain.common import GAMES_SAVE_DIR

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
assert OPENAI_API_KEY, 'OPENAI_API_KEY not found. Please configure it as an env variable'
openai_client = OpenAI()

class DynamicGoingOnAPicnic(GuessTheRuleGame):

    def load_game(self, uuid_str=None):
        assert self.uuid or uuid_str, f'Could not find a uuid to load the game.'
        uuid_to_load = self.uuid or uuid_str
        filename = os.path.join(GAMES_SAVE_DIR, f"{uuid_to_load}.json")
        if not os.path.exists(filename):
            raise FileNotFoundError(f"No saved game found with UUID: {uuid_to_load}")

        try:
            with open(filename, 'r') as f:
                state = json.load(f)
        except Exception as e:
            print(f"Error loading game state: {e}")
            raise

        # Create a new instance of the class
        game = DynamicGoingOnAPicnic(uuid=state['uuid'])
        # Update the instance's __dict__ with the loaded state
        game.__dict__.update(state)

        # Convert lists back to sets
        # game.history['positives'] = set(game.history['positives'])
        # game.history['negatives'] = set(game.history['negatives'])
        # this section is copied from ali's code. your game doesn't have this, what you do need is to be able to recover the history (this in your case would be done through )

        # Convert UUID string back to UUID object
        game.uuid = uuid.UUID(game.uuid)

        return game

    def create_game_instance(self):
        assert not self.uuid, 'Cannot create a new game with an already generated UUID'
        self.uuid = uuid.uuid4()
        self.game_class_name = self.__class__.__name__
        self.rule_type = random.choice(['attribute_based', 'categorical', 'logical', 'relational', 'semantic'])
        self.rule = self.load_secret_rule(self.rule_type)

        self.judge_model = 'gpt-4o'

        self.start_time = time.time()
        self.game_end_time = None
        self.total_game_time = None
        self.status = 'ongoing'

        generated_examples = self.generate_examples()
        system_message = self.make_init_system_message(generated_examples)
        
        return {
            'game_uuid': str(self.uuid), # FE
            'domain': self.domain, # FE
            'difficulty': self.difficulty, # FE
            'game_gen_type': self.game_gen_type, # FE
            'start_time': time.ctime(int(self.start_time)), # FE
            'turns_taken': self.turns, # FE
            'status': self.status, # FE
            'system_message': system_message, # FE, need to return the message that gets displayed to the user
        }

    def get_more_examples(self, n):
        if self.status != 'ongoing':
            return {
                'game_uuid': str(self.uuid),
                'status': self.status,
                'system_message': 'Cannot provide more examples after the game is finished.'
            }
        generated_examples = self.generate_examples(n)
        system_message = self.make_more_examples_system_message(generated_examples)
        
        self.save_game()
        return {
            'game_uuid': str(self.uuid),
            'status': self.status,
            'system_message': system_message
        }

    def validate_guess(self):
        raise NotImplementedError('Method not implemented for this game')
    
    def is_rule_guess(self, user_input):
        prompt = (
            f"You are currently playing a Guess The Rule Game. It is a game where there is a game master and players. "
            f"In order to win the game, players must correctly figure out the underlying rule of the game.\n\n"
            f"The players can make guesses to the game master.\n"
            f"The players can give the game master two different kinds of guesses:\n"
            f"    1. giving an example (or examples) fit the rule\n"
            f"    2. giving their guess of the actual rule.\n\n"
            f"Take a look at the player's guess: \"{user_input}\".\n\n"
            f"Your task is to classify if the player's guess is an example or a guess of the rule itself.\n\n"
            f"Please respond with either \"example\" for an example guess (or guesses), or \"actual\" for a guess of the actual rule.\n"
            f"Do not provide any additional explanation or text.\n\n"
            f"Format:\n\n"
            f"[your final answer]"
        )
        
        message_history = [{"role": "user", "content": prompt}]
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            response = self.get_llm_model_response(message_history).strip().lower()

            if "actual" in response:
                return True
            elif "example" in response:
                return False
            else:
                retry_count += 1
        raise ValueError(f"Model failed to return a valid response after {max_retries} retries.")
    
    # finished / implemented below

    def make_more_examples_system_message(generated_examples):
        return (
            f"You can bring: {generated_examples}.\n\n"
            f"Now given this information, do one of the following:\n"
            f"1. Make a new guess that hasn't been mentioned before.\n"
            f"2. Request more examples.\n"
            f"3. Type the rule if you think you've guessed it.\n\n"
            f"What would you like to do?"
        )
    
    def generate_examples(self, num_examples=2):
        prompt = (
            f"You are an assistant helping to generate examples for a game called \"Guess the Rule Games.\"\n\n"
            f"The secret rule is: {self.rule}\n\n"
            f"Your task is to provide {num_examples} examples of items that satisfy the secret rule.\n\n"
            f"- Only provide the items in a simple, comma-separated list.\n"
            f"- Do not mention the secret rule.\n"
            f"- Do not provide any additional explanation or text.\n\n"
            f"Format:\n\n"
            f"[item1], [item2], ..., [item{num_examples}]"
        )
        
        message_history = [{"role": "user", "content": prompt}]
        examples_text = self.get_llm_model_response(message_history)
        examples_text = examples_text.strip().strip('"\'')
        examples = [item.strip() for item in examples_text.split(',') if item.strip()]
        return examples
    
    @retry(tries=3, delay=1, exceptions=(anthropic.InternalServerError, openai.InternalServerError))
    def get_llm_model_response(self, message_history, platform='openai'):
        try:
            response = openai_client.chat.completions.create(
                model=self.judge_model,
                messages=message_history
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise
        
    def make_init_system_message(generated_examples):
        return (
            f"Let's play the game 'going on a picnic'.\n\n"
            f"I will give you some examples in each turn and you have to guess the underlying rule of the game. "
            f"The rule will be common for all the examples.\n"
            f"Your score will be based on the number of turns taken, number of examples seen, "
            f"and overall time elapsed playing the game. The highest score will be for the fewest turns taken, "
            f"fewest examples seen, and shortest game played.\n\n"
            f"The game master has given examples of items that fit the rule: generated_examples.\n\n"
            f"Now given this information, do one of the following:\n"
            f"1. Make a new guess that hasn't been mentioned before.\n"
            f"2. Request more examples.\n"
            f"3. Type the rule if you think you've guessed it.\n\n"
            f"What would you like to do?"
        )
    
    def load_secret_rule(rule_type, self):
        """
        Load a secret rule from a JSON file containing a list of rules.
        Filters rules based on rule_type and level_difficulty, then picks a random rule.
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        rules_directory = os.path.join(script_dir, 'rules', rule_type)
        filename = os.path.join(rules_directory, f"{rule_type}_rules.json")
        with open(filename, 'r') as f:
            rules = json.load(f)
        
        filtered_rules = [rule for rule in rules if rule.get('level') == self.difficulty]
        
        if not filtered_rules:
            raise ValueError(f"No rules found for rule_type {rule_type} of level {self.difficulty}.")
        
        secret_rule = random.choice(filtered_rules)
        return secret_rule['rule']