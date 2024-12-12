import os
import pickle
import random
from openai import OpenAI
import string
import nltk
import sys
import uuid
import __main__ as main
import time
import json
from lib.domain.base import GuessTheRuleGame
from lib.domain.common import GAMES_SAVE_DIR

import pdb

# Set your OpenAI API key (or any other LLM provider's key)
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# juno : for testing purposes
if not OPENAI_KEY and os.path.exists('/mnt/c/Users/juno/Desktop/llmstuff/secretkey'):
    with open('/mnt/c/Users/juno/Desktop/llmstuff/secretkey', 'r') as f:
        OPENAI_KEY = f.read().strip()
        OpenAI.api_key = OPENAI_KEY

client = OpenAI(api_key=OPENAI_KEY)

# Function to send a prompt to the LLM and get the response
def get_llm_response(prompt, sysprompt=None):
    response = client.chat.completions.create(model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": sysprompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7)
    return response.choices[0].message.content.strip()

def get_std_corpus():
        try:
            words = set(nltk.corpus.words.words())
        except LookupError:
            nltk.download('words')
            words = set(nltk.corpus.words.words())
        return words

def read_promptstring(filename):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_dir, 'promptstrings', filename), 'r') as f:
        promptstring = f.read()
    return promptstring

def write_history(filename, txt):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_dir, 'promptstrings', filename), 'a') as f:
        f.write(txt)
    return
class GuessingGame:

    def __init__(self, rngstate, domain=None, difficulty=None, init_examples=None, use_llm=False):
        self.rngstate = rngstate
        self.domain = domain
        self.difficulty = difficulty
        self.init_examples = init_examples
        self.use_llm = use_llm

        self.wordgen_fn = self.word_generator_from_corpus # self.make_word_generator(k=5)
        genrule = self.generate_rule_chatgpt # if self.use_llm else self.generate_rule
        self.rule_code, self.rule_fn = genrule()
        
    def generate_rule_chatgpt(self):
        random.setstate(self.rngstate)  # unused
        prompt = "Generate a rule based on the following criteria:\n"
        if self.domain:
            prompt += f"Domain: {self.domain}\n"
        if self.difficulty:
            prompt += f"Difficulty: {self.difficulty}\n"
        if self.init_examples:
            prompt += f"Examples: {self.init_examples}\n\n"
        # don't repeat
        prompt += read_promptstring(f'history_{self.difficulty}.txt')
        prompt += "Generated code:"

        sysprompt = read_promptstring('sysprompt.txt')
        ans = get_llm_response(prompt=prompt, sysprompt=sysprompt)
        ans_strip = ''
        for line in ans.splitlines():
            if not line.startswith('```'):
                ans_strip += line + '\n'
        print(ans_strip)
        generated_fn = None
        try:
            local_namespace = {}
            print('debug')
            print(ans_strip)
            exec(ans_strip, globals(), local_namespace)
            if 'generated_fn' in local_namespace:
                generated_fn = local_namespace['generated_fn']
            else:
                raise Exception('problem assigning "generated_fn"') 
        except SyntaxError as e:
            print("Syntax Error in Generated Code:", e)
            return
        # print(generated_fn)
        self.rngstate = random.getstate()
        write_history(f'history_{self.difficulty}.txt', ans_strip)
        return ans_strip, generated_fn

    def word_generator(self, minL=0, maxL=float('inf')):
        random.setstate(self.rngstate)
        k = random.choice(range(minL, maxL))
        word = ''.join(random.choice(string.ascii_lowercase) for _ in range(k))
        self.rngstate = random.getstate()
        return word

    def word_generator_from_corpus(self, minL=4, maxL=8, corpus=None):
        if corpus is None:
            words = get_std_corpus()
        else:
            words = corpus
        valid_words = [word.lower() for word in words 
                    if minL <= len(word) < maxL]
        if not valid_words:
            raise ValueError(f"No words found with length between {minL} and {maxL}")
        random.setstate(self.rngstate)
        word = random.choice(valid_words)
        self.rngstate = random.getstate()
        return word

    # def generate_rule(self):
    #     def has_at_least_two_vowels(x: string):
    #         return sum([c in 'aeiou' for c in x]) >= 2
    #     def has_less_than_two_vowels(x: string):
    #         return not has_at_least_two_vowels(x)
    #     def starts_with_first_half_alphabet(x: string):
    #         return ord(x[0]) - ord('a') < 13
    #     random.setstate(self.rngstate)
    #     fn = random.choice([has_at_least_two_vowels, has_less_than_two_vowels, starts_with_first_half_alphabet])
    #     self.rngstate = random.getstate()
    #     return 'dummy', fn

    def generate_example(self):
        random_word = self.wordgen_fn()
        # breakpoint()
        return random_word, self.rule_fn(random_word)
    
    def validate_guess(self, guess):  # llm to validate guess
        sysprompt = read_promptstring('validate_sysprompt.txt')
        prompt = 'Function code:\n'
        prompt += self.rule_code
        prompt += '\n\n'
        prompt += 'Guess:\n'
        prompt += guess
        ans = get_llm_response(prompt=prompt, sysprompt=sysprompt)
        ans = ans.strip()
        print('debug: ' + ans)
        ans_last = ans.split()[-1]
        print('debug: ' + ans_last)
        if ans_last not in ['YES', 'NO']:
            print('invalid LLM output')
            raise Exception
        return ans_last == 'YES'

class LexicalFunctionGame(GuessTheRuleGame):

    def create_game_instance(self):
        assert not self.uuid, 'Cannot create a new game with an already generated UUID'
        self.uuid = uuid.uuid4()
        self.game_class_name = self.__class__.__name__
        random.seed(self.uuid.int)
        self._game = GuessingGame(random.getstate(), domain=self.domain, difficulty=self.difficulty, init_examples=None, use_llm=True)
        self.rule = self._game.rule_code

        self.judge_model = 'gpt-4o-mini'
        self.judge_prompt = read_promptstring('validate_sysprompt.txt')

        self.start_time = time.time()
        self.win_time = None
        self.total_game_time = None
        self.turns = 0
        self.history = {'positives': set(), 'negatives': set()}
        self.total_examples_available = 0
        self.total_pos_examples_shown = 0
        self.total_neg_examples_shown = 0
        self.win = False
        self.status = 'ongoing'

        positives, negatives = self.generate_examples(self.num_init_examples)
        self.save_game()  # Save the game after creation
        return {
            'game_uuid': str(self.uuid),
            'domain': self.domain,
            'difficulty': self.difficulty,
            'game_gen_type': self.game_gen_type,
            'start_time': time.ctime(int(self.start_time)),
            'total_examples_available': self.total_examples_available,
            'positive_examples': positives,
            'negative_examples': negatives
        }
    
    def save_game(self):
        filename = os.path.join(GAMES_SAVE_DIR, f"{self.uuid}.pkl")
        temp_filename = filename + '.tmp'
        try:
            self._game.rule_fn = None
            with open(temp_filename, 'wb') as f:
                pickle.dump(self, f)
            os.replace(temp_filename, filename)
        except Exception as e:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
            print(f"Error saving game state: {e}")
            raise
    
    def load_game(self=None, uuid_str=None):
        assert (self and self.uuid) or uuid_str, f'Could not find a uuid to load the game.'
        uuid_to_load = (self and self.uuid) or uuid_str
        filename = os.path.join(GAMES_SAVE_DIR, f"{uuid_to_load}.pkl")
        if not os.path.exists(filename):
            raise FileNotFoundError(f"No saved game found with UUID: {uuid_to_load}")
        # breakpoint()
        try:
            with open(filename, 'rb') as f:
                state = pickle.load(f)
        except Exception as e:
            print(f"Error loading game state: {e}")
            raise
        try:
            local_namespace = {}
            print('debug')
            print(state._game.rule_code)
            exec(state._game.rule_code, globals(), local_namespace)
            if 'generated_fn' in local_namespace:
                state._game.rule_fn = local_namespace['generated_fn']
            else:
                raise Exception('problem assigning "generated_fn"')
        except SyntaxError as e:
            print("Syntax Error in Generated Code:", e)
            return

        # Create a new instance of the class
        # game = LexicalFunctionGame(uuid=state['uuid'])
        # # Update the instance's __dict__ with the loaded state
        # game.__dict__.update(state)

        # # Convert lists back to sets
        # game.history['positives'] = set(game.history['positives'])
        # game.history['negatives'] = set(game.history['negatives'])

        # # Convert UUID string back to UUID object
        # game.uuid = uuid.UUID(game.uuid)
        # return game
        return state
    
    def make_more_examples_system_message(self, positive_examples, negative_examples):
        positives_string = ', '.join(positive_examples)
        # breakpoint()
        negatives_string = ', '.join(negative_examples)
        return (
            f"I can bring: {positives_string}\n"
            f"I cannot bring: {negatives_string}\n\n"
            f"What would you like to do?"
        )

    def generate_examples(self, n=5):
        exs = []
        for _ in range(n):
            exs.append(self._game.generate_example())

        positives = [ex[0] for ex in exs if ex[1]]
        negatives = [ex[0] for ex in exs if not ex[1]]

        self.history["positives"].update(positives)
        self.history["negatives"].update(negatives)
        self.total_pos_examples_shown += len(positives)
        self.total_neg_examples_shown += len(negatives)
        return positives, negatives


    def get_more_examples(self, n=5):
        #TODO: are we supposed to serialize examples?/every game
        assert self.status == 'ongoing'
        positives, negatives = self.generate_examples(n)
        self.save_game()

        return {
            'game_uuid': str(self.uuid),
            'positive_examples': positives,
            'negative_examples': negatives,
            'system_message': self.make_more_examples_system_message(positives, negatives)
        }
    
    def validate_guess(self, guess):
        assert not self.win, f'Cannot validate guess after the game is finished.'
        is_correct = self._game.validate_guess(guess)
        print(f"Judge model {self.judge_model} response: {is_correct}")
        if is_correct:
            self.win = True
            self.win_time = time.time()
            self.total_game_time = self.win_time - self.start_time
        return is_correct

# # client level API (serverside responses to client requests)
# game_dct = {}
# def request_game_instance(domain=None, difficulty=None, init_examples=None, use_llm=False):
#     rngstate = random.Random()
#     if not init_examples:
#         init_examples = read_promptstring('init_examples_std_lexical_fns.txt')
#     game = GuessingGame(random.getstate(), domain=None, difficulty=None,
#                          init_examples=None, use_llm=False)
#     game_id = uuid.uuid4()
#     game_dct[game_id] = game
#     return game_id

# def request_more_examples(game_id, n_examples=5):
#     if game_id not in game_dct:
#         raise Exception('Invalid game id!')
#     print('sdfsdfsdf', game_id)
#     game = game_dct[game_id]
#     exs = []
#     for _ in range(n_examples):
#         exs.append(game.generate_example())
#     return exs

# def request_guess_validation(game_id, guess):
#     game = game_dct[game_id]
#     return game.validate_guess(guess)

# def main():
#     init_examples_std_lexical_fns = read_promptstring('init_examples_std_lexical_fns.txt')

#     print('Lexical style rules (string manipulation)')
#     print('5 random game instances (hardcoded rule fns)')
#     for i in range(5):
#         print(f'Game {i}')
#         random.seed(42 + i)
#         game = GuessingGame(random.getstate(), init_examples=init_examples_std_lexical_fns)
#         print(f'DEBUG: secret rule is: {game.rule_fn.__name__}')
#         for _ in range(10):
#             random_word, is_rule_true = game.generate_example()
#             print(random_word, is_rule_true)
#     print('5 LLM-generated rules (standard English corpus)')
#     for i in range(5):
#         print(f'Game {i}')
#         random.seed(42 + i)
#         game = GuessingGame(random.getstate(), init_examples=init_examples_std_lexical_fns,
#             use_llm=True)
#         print(f'DEBUG: secret rule is: {game.rule_fn.__name__}')
#         for _ in range(10):
#             random_word, is_rule_true = game.generate_example()
#             print(random_word, is_rule_true)

# if __name__ == "__main__":
#     if sys.flags.interactive:
#         print('Interactive mode')
#         print('Help (Function Signatures):')
#         print('------------------------------')
#         print('request_game_instance(domain=None, difficulty=None, init_examples=None, use_llm=False)')
#         print('request_more_examples(game_id)')
#         print('request_guess_validation(game_id, guess)')
#         init_examples_std_lexical_fns = read_promptstring('init_examples_std_lexical_fns.txt')
#         print('------------------------------')
#         game = GuessingGame(random.getstate(), init_examples=init_examples_std_lexical_fns,
#             use_llm=True)
#         pass
#     else:
#         main()