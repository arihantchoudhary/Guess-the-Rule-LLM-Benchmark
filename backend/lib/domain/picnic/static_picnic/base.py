import random
import json
import time
import os
import uuid

from openai import OpenAI
from dotenv import load_dotenv

from lib.domain.base import GuessTheRuleGame
from lib.domain.common import GAMES_SAVE_DIR

# Load the .env file
load_dotenv()

# Initialize the OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
assert OPENAI_API_KEY, 'OPENAI_API_KEY not found. Please configure it as an env variable'
openai_client = OpenAI()

# Get the directory of the current file (base.py)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Load items and counts data
with open(os.path.join(current_dir, 'data', 'open_images_combined_items.json'), 'r') as file:
    items = json.load(file)

# Load individual, pair, and triplet counts from JSON files
with open(os.path.join(current_dir, 'data', 'pp_individual_counts.json'), 'r') as file:
    l1_counts = json.load(file)
    l1_counts = {tuple(eval(key)): value for key, value in l1_counts.items()}

with open(os.path.join(current_dir, 'data', 'pp_pairs_counts.json'), 'r') as file:
    l2_counts = json.load(file)
    l2_counts = {tuple(eval(key)): value for key, value in l2_counts.items()}

with open(os.path.join(current_dir, 'data', 'pp_triplets_counts.json'), 'r') as file:
    l3_counts = json.load(file)
    l3_counts = {tuple(eval(key)): value for key, value in l3_counts.items()}

# Categorize individuals, pairs, and triplets based on count thresholds
L1_individuals = [key[0] for key, count in l1_counts.items() if count > 6]
L2_individuals = [key[0] for key, count in l1_counts.items() if 4 <= count <= 6]
L3_individuals = [key[0] for key, count in l1_counts.items() if 3 <= count < 4]

L2_pairs = [pair for pair, count in l2_counts.items() if count > 6]
L3_pairs = [pair for pair, count in l2_counts.items() if 4 <= count < 6]
L3_triplets = [triplet for triplet, count in l3_counts.items() if count > 4]  # Exclude triplets with ≤ 2 examples

class StaticGoingOnAPicnic(GuessTheRuleGame):

    def save_game(self):
        # Create a serializable copy of the instance's __dict__
        state = self.__dict__.copy()

        # Convert sets to lists for JSON serialization
        state['history']['positives'] = list(state['history']['positives'])
        state['history']['negatives'] = list(state['history']['negatives'])

        state['uuid'] = str(self.uuid)

        # Convert any time-related objects to timestamps
        state['start_time'] = self.start_time
        state['game_end_time'] = self.game_end_time

        # Build the file path using the save directory
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
        game = StaticGoingOnAPicnic(uuid=state['uuid'])
        # Update the instance's __dict__ with the loaded state
        game.__dict__.update(state)

        # Convert lists back to sets
        game.history['positives'] = set(game.history['positives'])
        game.history['negatives'] = set(game.history['negatives'])

        # Convert UUID string back to UUID object
        game.uuid = uuid.UUID(game.uuid)

        return game

    def make_system_message(self, positive_examples, negative_examples):
        positives_string = ', '.join(positive_examples)
        negatives_string = ', '.join(negative_examples)
        return (
            f"Let's play the game 'going on a picnic'.\n"
            f"I will give you some examples in each turn and you have to guess the underlying rule of the game. The rule will be common for all the examples.\n"
            f"Your score will be based on the number of turns taken, number of examples seen, and overall time elapsed playing the game. The highest score will be for the fewest turns taken, fewest examples seen, and shortest game played.\n"
            f"The rule you will guess should only encompass the positive examples. The negative examples are only for additional guidance and they do not form the underlying rule itself.\n"
            f"To play the game you can only do one of the following actions in a turn:\n"
            f"1. type 'more N' to request N more examples for that rule.\n"
            f"2. type the rule if you think you've guessed it. The format must be 'Items from the category/categories <category>'.\n"
            f"3. type 'give up' if you want to end the game and see the rule.\n\n"
            f"I can bring: {positives_string}\n"
            f"I cannot bring: {negatives_string}\n\n"
            f"What would you like to do?"
        )


    def create_game_instance(self):
        assert not self.uuid, 'Cannot create a new game with an already generated UUID'
        self.uuid = uuid.uuid4()
        self.game_class_name = self.__class__.__name__
        self.rule = self.pick_rule()

        self.judge_model = 'gpt-4o-mini'
        self.judge_prompt = self.get_judge_prompt()

        self.start_time = time.time()
        self.game_end_time = None
        self.total_game_time = None
        self.turns = 0
        self.history = {'positives': set(), 'negatives': set()}
        self.total_examples_available = 0
        self.total_pos_examples_shown = 0
        self.total_neg_examples_shown = 0
        self.status = 'ongoing'

        positives, negatives = self.generate_examples(self.num_init_examples, is_init=True)
        self.save_game()  # Save the game after creation
        return {
            'game_uuid': str(self.uuid),
            'domain': self.domain,
            'difficulty': self.difficulty,
            'game_gen_type': self.game_gen_type,
            'start_time': time.ctime(int(self.start_time)),
            'turns_taken': self.turns,
            'status': self.status,
            'total_examples_available': self.total_examples_available,
            'system_message': self.make_system_message(positives, negatives),
            'positive_examples': positives,
            'negative_examples': negatives
        }

    def get_more_examples(self, n, is_init=False):
        assert self.status == 'ongoing', f'Cannot provide more examples after the game is finished.'
        positives, negatives = self.generate_examples(n, is_init)
        self.save_game()  # Save the game after getting more examples
        return {
            'game_uuid': str(self.uuid),
            'positive_examples': positives,
            'negative_examples': negatives
        }

    def generate_examples(self, n, is_init=False):
        assert self.status == 'ongoing', f'Cannot provide more examples after the game is finished.'
        self.turns += 1
        rule_tags = self.rule["categories"] if "categories" in self.rule else [self.rule["category"]]
        available_positives = [
            item for item, tags in items.items() if all(tag in tags for tag in rule_tags) and item not in self.history["positives"]
        ]
        available_negatives = [
            item for item, tags in items.items() if not all(tag in tags for tag in rule_tags) and item not in self.history["negatives"]
        ]

        # Compute available_count based on current history
        available_count = min(len(available_positives), len(available_negatives))

        assert n <= available_count, f'Request number of examples n={n} exceeds available number of examples {available_count}'

        if is_init:
            self.total_examples_available = available_count

        positives = random.sample(available_positives, n)
        negatives = random.sample(available_negatives, n)

        # Update history
        self.history["positives"].update(positives)
        self.history["negatives"].update(negatives)
        self.total_pos_examples_shown += len(positives)
        self.total_neg_examples_shown += len(negatives)

        return positives, negatives

    def validate_guess(self, guess):
        assert self.status == 'ongoing', f'Cannot validate guess after the game is finished.'
        result = self.check_guess(guess)
        self.save_game()  # Save the game after validating the guess
        return {
            'game_uuid': str(self.uuid),
            'guess_result': result
        }

    def check_guess(self, guess):
        assert self.status == 'ongoing', f'Cannot validate guess after the game is finished.'
        # Enhanced prompt to consider synonyms and semantic similarity
        self.turns += 1
        prompt = self.judge_prompt.format(guess=guess, rule=self.rule['rule'], positive_examples=list(self.history['positives']))

        print(f"\n*** Prompt for JUDGE ***\n{prompt}\n\n")
        try:
            response = openai_client.chat.completions.create(
                model=self.judge_model,
                messages=[
                    {"role": "system", "content": "You are an expert at identifying semantic equivalency in a game called 'Going on a Picnic'."},
                    {"role": "user", "content": prompt}
                ],
            )
            answer = response.choices[0].message.content.strip().lower()
            print(f"Judge model {self.judge_model} response: {answer}")
            if answer == "yes":
                self.status = 'won'
                self.game_end_time = time.time()
                self.total_game_time = self.game_end_time - self.start_time
                return True
            else:
                return False
        except Exception as e:
            print(f"Error while calling OpenAI API for check guess. Error: {e}")
            raise e

    def pick_rule(self):
        if self.difficulty == "L1":
            category = random.choice(L1_individuals)
            return {"type": "category", "rule": f"Items from the category '{category}'", "category": category}

        elif self.difficulty == "L2":
            if random.choice(["individual", "pair"]) == "individual":
                category = random.choice(L2_individuals)
                return {"type": "category", "rule": f"Items from the category '{category}'", "category": category}
            else:
                pair = random.choice(L2_pairs)
                return {"type": "pair", "rule": f"Items from the categories '{pair[0]}' and '{pair[1]}'", "categories": pair}

        elif self.difficulty == "L3":
            rule_type = random.choice(["individual", "pair", "triplet"])
            if rule_type == "individual":
                category = random.choice(L3_individuals)
                return {"type": "category", "rule": f"Items from the category '{category}'", "category": category}
            elif rule_type == "pair":
                pair = random.choice(L3_pairs)
                return {"type": "pair", "rule": f"Items from the categories '{pair[0]}' and '{pair[1]}'", "categories": pair}
            else:
                triplet = random.choice(L3_triplets)
                return {
                    "type": "triplet",
                    "rule": f"Items from the categories '{triplet[0]}', '{triplet[1]}', and '{triplet[2]}'",
                    "categories": triplet
                }

    def get_judge_prompt(self):
        return '''
        Determine if the following user guess is semantically equivalent or reasonably close in meaning to the actual rule.
        Consider synonyms, related terms, and general concepts.

        The user was also provided some examples. If the user's answer is correct according to the examples but deviates from the rule a little bit (only a little), it can still be marked as correct.
        User Guess: "{guess}"
        Actual Rule: "{rule}"
        Examples Shown: {positive_examples}

        Respond with 'yes' if they are equivalent or similar, otherwise respond with 'no'.
        '''

    def get_game_summary(self, include_rule=False):
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
            'status': self.status
        }
        if include_rule:
            response['rule'] = self.rule

        return response
