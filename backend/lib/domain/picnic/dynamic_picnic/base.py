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

logging.basicConfig(
    level=logging.INFO,  
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  
    handlers=[
        logging.StreamHandler() 
    ]
)

logger = logging.getLogger(__name__)

from lib.domain.base import GuessTheRuleGame
from lib.domain.common import GAMES_SAVE_DIR

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
assert OPENAI_API_KEY, 'OPENAI_API_KEY not found. Please configure it as an env variable'
openai_client = OpenAI()

class DynamicGoingOnAPicnic(GuessTheRuleGame):

    def make_game_history_system_message(self):
        if self.status == 'ongoing':
            current_conversation = "\n".join([
                f"{msg['role'].capitalize()}: {msg['content']}"
                for msg in self.history["conversation"]
            ])

            msg = (
                f"Welcome back to the game 'Going on a Picnic'.\n\n"
                f"Here is the conversation from before:\n"
                f"{current_conversation}\n\n"
                f"What would you like to do next?"
            )
            return msg
        else:
            return (
                f"Game is over. You {self.status}. The rule was \"{self.rule}\".\n"
                f"Check your stats in the top panel."
            )
        
    def get_game_summary(self, include_rule=False):
        system_message = self.make_game_history_system_message()
        
        response = {
            'game_uuid': str(self.uuid),
            'game_class_name': self.__class__.__name__,
            'domain': self.domain,
            'difficulty': self.difficulty,
            'game_gen_type': self.game_gen_type,
            'start_time': time.ctime(int(self.start_time)),
            'game_end_time': time.ctime(int(self.game_end_time)) if self.game_end_time else None,
            'total_game_time': self.total_game_time if self.total_game_time else time.time() - self.start_time,
            'turns_taken': self.turns,
            'game_history': {
                'positives': list(self.history['positives']),
                'negatives': list(self.history['negatives'])
            },
            'total_examples_available': self.total_examples_available,
            'total_pos_examples_shown': self.total_pos_examples_shown,
            'total_neg_examples_shown': self.total_neg_examples_shown,
            'status': self.status,
            'system_message': system_message,
            'generated_examples': list(self.generated_examples) if hasattr(self, 'generated_examples') else [],
            'player_guesses': list(self.player_guesses) if hasattr(self, 'player_guesses') else []
        }
        if include_rule or self.status in ['won', 'lost']:
            response['rule'] = self.rule

        return response
    
    def create_game_instance(self):
        assert not self.uuid, 'Cannot create a new game with an already generated UUID'
        self.uuid = uuid.uuid4()
        self.game_class_name = self.__class__.__name__
        self.rule_type = random.choice(['attribute_based', 'categorical', 'logical', 'relational', 'semantic'])
        self.rule = self.load_secret_rule()

        self.judge_model = 'gpt-4o'

        self.start_time = time.time()
        self.game_end_time = None
        self.total_game_time = None
        self.turns = 0
        self.history = {"conversation": []}
        self.status = 'ongoing'

        self.generated_examples = set()
        self.player_guesses = set()

        genned_examples = self.generate_examples()
        self.generated_examples.update(example.lower() for example in genned_examples)
        
        system_message = self.make_init_system_message(genned_examples)
        self.add_to_conversation("assistant", system_message)
        
        self.save_game()
        return {
            'game_uuid': str(self.uuid), # FE IN
            'domain': self.domain, # FE IN
            'difficulty': self.difficulty, # FE IN
            'game_gen_type': self.game_gen_type, # FE IN
            'start_time': time.ctime(int(self.start_time)), # FE IN
            'turns_taken': self.turns, # FE IN
            'status': self.status, # FE IN
            'system_message': system_message, # FE IN
        }

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

        game = DynamicGoingOnAPicnic(uuid=state['uuid'])
        game.__dict__.update(state)
        game.uuid = uuid.UUID(game.uuid)

        game.generated_examples = set(example.lower() for example in state.get('generated_examples', []))
        game.player_guesses = set(guess.lower() for guess in state.get('player_guesses', []))

        return game
    
    def save_game(self):
        state = self.__dict__.copy()

        state['uuid'] = str(self.uuid)
        state['start_time'] = self.start_time
        state['game_end_time'] = self.game_end_time

        state['generated_examples'] = list(self.generated_examples)
        state['player_guesses'] = list(self.player_guesses)

        filename = os.path.join(GAMES_SAVE_DIR, f"{self.uuid}.json")
        temp_filename = filename + '.tmp'

        try:
            with open(temp_filename, 'w') as f:
                json.dump(state, f, indent=4)
            # Atomically replace the old file
            os.replace(temp_filename, filename)
        except Exception as e:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
            print(f"Error saving game state: {e}")
            raise

    def add_to_conversation(self, role, content):
        self.history["conversation"].append({
            "role": role,
            "content": content
        })

    def get_more_examples(self, n):
        if self.status != 'ongoing':
            return {
                'game_uuid': str(self.uuid),
                'status': self.status,
                'system_message': 'Cannot provide more examples after the game is finished.'
            }
        generated_examples = self.generate_examples(n)
        self.generated_examples.update(example.lower() for example in generated_examples)

        system_message = self.make_more_examples_system_message(generated_examples)
        self.add_to_conversation("assistant", system_message)

        self.save_game()
        return {
            'game_uuid': str(self.uuid),
            'status': self.status,
            'system_message': system_message
        }
    
    def validate_guess(self, guess):
        if self.status != 'ongoing':
            return {
                'game_uuid': str(self.uuid),
                'status': self.status,
                'guess_result': False,
                'system_message': 'Cannot validate guess after the game is finished.'
            }
        result = self.check_guess(guess)
        system_message = self.make_validate_guess_system_message(result, guess)
        self.add_to_conversation("assistant", system_message)
        
        self.save_game()
        return {
            'game_uuid': str(self.uuid),
            'status': self.status,
            'guess_result': result,
            'system_message': system_message
        }

    def make_validate_guess_system_message(self, guess_result, guess):
        if guess_result is True:
            game_master_msg = f'You guessed the rule correctly! The rule was: {self.rule} \n\nCheck your performance stats in the panel above. Thanks for playing!'
            return game_master_msg
        elif guess_result == "give up":
            return f"You gave up, the correct rule was: {self.rule}"
        elif isinstance(guess_result, str):
            return guess_result
        else:
            game_master_msg = "Incorrect guess. What would you like to do next?"
            return game_master_msg

    def check_guess(self, guess):
        self.turns += 1
        self.add_to_conversation("user", guess)

        is_guess_rule = self.is_rule_guess(guess)
        if is_guess_rule == "actual":
            result = self.check_rule_guess(guess)
            if result == "yes":
                self.status = 'won'
                self.game_end_time = time.time()
                self.total_game_time = self.game_end_time - self.start_time
                return True
        elif is_guess_rule == "example":
            self.player_guesses.add(guess.strip().lower())
            result = self.check_example_guess(guess)
            return result
        elif is_guess_rule == "give up":
            self.status = 'lost'
            self.game_end_time = time.time()
            self.total_game_time = self.game_end_time - self.start_time
            return "give up"
        return False
    
    def check_rule_guess(self, rule_guess):
        sys_prompt = (
            f"You are an expert at identifying semantic equivalency in natural language. "
            f"Your task is to evaluate whether a proposed rule guess semantically matches a predefined rule. "
            f"Consider variations in phrasing, synonyms, or minor rewording as valid matches, but disregard guesses that significantly deviate "
            f"from the intended meaning. Provide a precise and accurate evaluation."
        )

        prompt = (
            f"The predefined rule is: \"{self.rule}\".\n"
            f"The player's rule guess is: \"{rule_guess}\".\n\n"
            f"Determine if the player's guess semantically matches the predefined rule. "
            f"Respond with either \"yes\" if the guess matches, or \"no\" if it does not match. "
            f"Do not provide any additional explanation or commentary.\n\n"
            f"Format:\n"
            f"[your final answer: yes or no]"
        )

        messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": prompt}
                ]
        
        max_retries = 3
        for attempt in range(max_retries):
            response = self.get_llm_model_response(messages).strip().lower()
            
            if "yes" in response:
                return "yes"
            elif "no" in response:
                return "no"
            else:
                logger.warning(f"Unexpected response from model on attempt {attempt + 1}: {response}")
        logger.error(f"Model failed to return a valid response after {max_retries} retries: {response}")
        raise ValueError(f"Model failed to return a valid response after {max_retries} retries.")

    def check_example_guess(self, example_guess):
        sys_prompt = (
            "You are an expert at evaluating whether specific examples satisfy a given rule. "
            "Your task is to determine if the provided example strictly adheres to the predefined rule. "
            "Use precise logic to evaluate the example, and consider only the information given in the predefined rule. "
            "Provide an accurate evaluation without additional explanation or commentary."
        )

        prompt = (
            f"The predefined rule is: \"{self.rule}\".\n"
            f"The player's example guess is: \"{example_guess}\".\n\n"
            "Determine if the player's example satisfies the predefined rule. "
            "Respond with only one of the following formats exactly:\n\n"
            "   Correct! You can bring <player's example guess>\n"
            "   Incorrect. You cannot bring <player's example guess>\n\n"
            "Do not provide any additional explanation or commentary.\n\n"
            "For example:"
            "   Player example guess: Can I bring a potato?"
            "   Example final answer: Incorrect. You cannot bring a potato.\n\n"
            "Format:\n"
            "[your final answer: \"Correct!\" or \"Incorrect.\" and the corresponding message]"
        )

        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": prompt}
        ]
        
        max_retries = 3
        for attempt in range(max_retries):
            response = self.get_llm_model_response(messages).strip()
            
            if "correct" in response.lower() or "incorrect" in response.lower():
                return response
            else:
                logger.warning(f"Unexpected response from model on attempt {attempt + 1}: {response}")
        
        logger.error(f"Model failed to return a valid response after {max_retries} retries: {response}")
        raise ValueError(f"Model failed to return a valid response after {max_retries} retries.")

    def is_rule_guess(self, user_input):
        prompt = (
            f"You are currently playing a Guess The Rule Game. It is a game where there is a game master and players. "
            f"In order to win the game, players must correctly figure out the underlying rule of the game.\n\n"
            f"The players can make guesses to the game master.\n"
            f"The players can give the game master three different kinds of guesses:\n"
            f"    1. Giving an example (or examples) that fit the rule\n"
            f"    2. Giving their guess of the actual rule\n"
            f"    3. Indicating that they want to 'give up' by explicitly stating so\n\n"
            f"Take a look at the player's guess: \"{user_input}\".\n\n"
            f"Your task is to classify if the player's guess is:\n"
            f"    - \"example\" for an example guess (or guesses),\n"
            f"    - \"actual\" for a guess of the actual rule, or\n"
            f"    - \"give up\" if the player indicates they want to give up.\n\n"
            f"Do not provide any additional explanation or text.\n\n"
            f"Format:\n\n"
            f"[your final answer: example, actual, or give up]"
        )
        
        message_history = [{"role": "user", "content": prompt}]
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            response = self.get_llm_model_response(message_history).strip().lower()

            if "actual" in response:
                return "actual"
            elif "example" in response:
                return "example"
            elif "give up" in response:
                return "give up"
            else:
                retry_count += 1
                logger.warning(f"Unexpected response from model: {response}. Retrying... ({retry_count}/{max_retries})")
        logger.error(f"Model failed to return a valid response after {max_retries} retries: {response}")
        raise ValueError(f"Model failed to return a valid response after {max_retries} retries.")

    def make_more_examples_system_message(self, generated_examples):
        generated_examples_str = ', '.join(generated_examples)
        return (
            f"You can bring: {generated_examples_str}.\n\n"
            f"Now given this information, do one of the following:\n"
            f"1. Make a new guess that hasn't been mentioned before.\n"
            f"2. Request more examples.\n"
            f"3. Type the rule if you think you've guessed it.\n\n"
            f"What would you like to do?"
        )
    
    def generate_examples(self, num_examples=2):
        self.turns += 1

        existing_generated = ', '.join(self.generated_examples) if self.generated_examples else 'none'
        existing_guesses = ', '.join(self.player_guesses) if self.player_guesses else 'none'

        prompt = (
            f"You are an assistant helping to generate examples for a game called \"Guess the Rule Games.\".\n\n"
            f"The secret rule is: {self.rule}\n\n"
            f"Here are the examples that have already been provided by the game master: {existing_generated}.\n"
            f"Here are the examples that the player has already guessed: {existing_guesses}.\n\n"
            f"Your task is to provide {num_examples} new and unique examples of items that satisfy the secret rule.\n\n"
            f"- Only provide the items in a simple, comma-separated list.\n"
            f"- Do not mention the secret rule.\n"
            f"- Do not repeat any examples already provided by the game master or guessed by the player.\n"
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
        
    def make_init_system_message(self, generated_examples):
        generated_examples_str = ', '.join(generated_examples)
        return (
            f"Let's play the game 'going on a picnic'.\n\n"
            f"I will give you some examples in each turn and you have to guess the underlying rule of the game. "
            f"The rule will be common for all the examples.\n"
            f"Your score will be based on the number of turns taken, number of examples seen, "
            f"and overall time elapsed playing the game. The highest score will be for the fewest turns taken, "
            f"fewest examples seen, and shortest game played.\n\n"
            f"The game master has given examples of items that fit the rule: {generated_examples_str}.\n\n"
            f"Now given this information, do one of the following:\n"
            f"1. Make a new guess that hasn't been mentioned before.\n"
            f"2. Request more examples.\n"
            f"3. Type the rule if you think you've guessed it.\n\n"
            f"What would you like to do?"
        )
    
    def load_secret_rule(self):
        """
        Load a secret rule from a JSON file containing a list of rules.
        Filters rules based on rule_type and level_difficulty, then picks a random rule.
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        rules_directory = os.path.join(script_dir, 'rules', self.rule_type)
        filename = os.path.join(rules_directory, f"{self.rule_type}_rules.json")
        with open(filename, 'r') as f:
            rules = json.load(f)
        
        filtered_rules = [rule for rule in rules if rule.get('level') == self.difficulty]
        
        if not filtered_rules:
            raise ValueError(f"No rules found for rule_type {self.rule_type} of level {self.difficulty}.")
        
        secret_rule = random.choice(filtered_rules)
        return secret_rule['rule']