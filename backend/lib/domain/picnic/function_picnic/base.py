import os
import random
from openai import OpenAI
import openai
import string
import nltk
import sys
import uuid
import __main__ as main
import time
import json
from lib.domain.base import GuessTheRuleGame
from lib.domain.common import GAMES_SAVE_DIR

# Set your OpenAI API key (or any other LLM provider's key)
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# juno : for testing purposes
if not OPENAI_KEY and os.path.exists('/mnt/c/Users/juno/Desktop/llmstuff/secretkey'):
    with open('/mnt/c/Users/juno/Desktop/llmstuff/secretkey', 'r') as f:
        OPENAI_KEY = f.read().strip()
        OpenAI.api_key = OPENAI_KEY

client = OpenAI(api_key=OPENAI_KEY)

# Define the rule templates for each rule type.
rule_templates = {
    "attribute_based": "Generate a rule based on a single object attribute like color, size, or shape.",
    "categorical": "Generate a rule based on a specific category of objects.",
    "relational": "Generate a rule based on a relational attribute between objects (e.g., size, weight).",
    "logical": "Generate a rule that combines two attributes using logical conditions like AND or OR.",
    "semantic": "Generate a rule that involves objects related by their use or context (e.g., used in a kitchen)."
}

# Dictionary to store rules under each rule type
rules_storage = {
    "attribute_based": [],
    "categorical": [],
    "relational": [],
    "logical": [],
    "semantic": []
}

# Function to send a prompt to the LLM and get the response
def get_llm_response(prompt, sysprompt=None):
    response = client.chat.completions.create(model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": sysprompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7)
    return response.choices[0].message.content.strip()

## Function to generate a rule prompt for each rule type
def generate_rule_prompt(rule_type):
    template_prompt = rule_templates[rule_type]
    return template_prompt

## Function to collect and process the LLM outputs from the rule prompt
def generate_rule_with_llm(rule_type):
    # Generate the template prompt based on the rule type
    prompt = generate_rule_prompt(rule_type)
    
    # Call the LLM with the prompt to generate a specific rule
    llm_response = get_llm_response(prompt)
    
    # Process and return the rule generated by the LLM
    return llm_response

## Function to generate and store the rule under the correct rule type
def generate_and_store_rule():
    # Randomly select a rule type
    rule_type = random.choice(list(rule_templates.keys()))
    
    # Get the specific rule from the LLM based on the rule type
    rule = generate_rule_with_llm(rule_type)
    
    # Store the rule in the correct category within rules_storage
    rules_storage[rule_type].append(rule)
    
    print(f"Generated rule type: {rule_type}")
    print(f"Rule: {rule}")
    
    return rule_type, rule

def get_std_corpus():
        try:
            words = set(nltk.corpus.words.words())
        except LookupError:
            nltk.download('words')
            words = set(nltk.corpus.words.words())
        return words

def read_promptstring(filename):
    with open(os.path.join('promptstrings', filename), 'r') as f:
        promptstring = f.read()
    return promptstring

class GuessingGame:

    def __init__(self, rngstate, domain=None, difficulty=None, init_examples=None, use_llm=False):
        self.rngstate = rngstate
        self.domain = domain
        self.difficulty = difficulty
        self.init_examples = init_examples
        self.use_llm = use_llm

        self.wordgen_fn = self.make_word_generator(k=5, is_using_corpus=True)
        genrule = self.generate_rule_chatgpt if self.use_llm else self.generate_rule
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
        return ans_strip, generated_fn

    def word_generator(self, minL=0, maxL=float('inf')):
        random.setstate(self.rngstate)
        k = random.choice(range(minL, maxL))
        word = ''.join(random.choice(string.ascii_lowercase) for _ in range(k))
        self.rngstate = random.getstate()
        return word

    def word_generator_from_corpus(self, minL=0, maxL=float('inf'), corpus=None):
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

    def make_word_generator(self, k, is_using_corpus=False):
        if is_using_corpus:
            return lambda: self.word_generator_from_corpus(minL=4, maxL=8, corpus=None)
        return lambda: self.word_generator(k)

    def generate_rule(self):
        def has_at_least_two_vowels(x: string):
            return sum([c in 'aeiou' for c in x]) >= 2
        def has_less_than_two_vowels(x: string):
            return not has_at_least_two_vowels(x)
        def starts_with_first_half_alphabet(x: string):
            return ord(x[0]) - ord('a') < 13
        random.setstate(self.rngstate)
        fn = random.choice([has_at_least_two_vowels, has_less_than_two_vowels, starts_with_first_half_alphabet])
        self.rngstate = random.getstate()
        return 'dummy', fn

    def generate_example(self):
        random_word = self.wordgen_fn()
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
        self._game = GuessingGame(random.getstate(), domain=None, difficulty=None, init_examples=None, use_llm=True)
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

        positives, negatives = self.generate_examples(self.num_init_examples, is_init=True)
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
        # Create a serializable copy of the instance's __dict__
        state = self.__dict__.copy()

        # Convert sets to lists for JSON serialization
        state['history']['positives'] = list(state['history']['positives'])
        state['history']['negatives'] = list(state['history']['negatives'])

        state['uuid'] = str(self.uuid)

        # Convert any time-related objects to timestamps
        state['start_time'] = self.start_time
        state['win_time'] = self.win_time

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
    
    def load_game(self=None, uuid_str=None):
        assert (self and self.uuid) or uuid_str, f'Could not find a uuid to load the game.'
        uuid_to_load = (self and self.uuid) or uuid_str
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
        game = LexicalFunctionGame(uuid=state['uuid'])
        # Update the instance's __dict__ with the loaded state
        game.__dict__.update(state)

        # Convert lists back to sets
        game.history['positives'] = set(game.history['positives'])
        game.history['negatives'] = set(game.history['negatives'])

        # Convert UUID string back to UUID object
        game.uuid = uuid.UUID(game.uuid)

        return game
    
    def get_more_examples(self, n=5):
        #TODO: are we supposed to serialize examples?/every game
        exs = []
        for _ in range(n):
            exs.append(self._game.generate_example())
        positives = [ex for ex in exs if ex[1]]
        negatives = [ex for ex in exs if not ex[1]]

        self.history["positives"].update(positives)
        self.history["negatives"].update(negatives)
        self.total_pos_examples_shown += len(positives)
        self.total_neg_examples_shown += len(negatives)

        return positives, negatives
    
    def validate_guess(self, guess):
        assert not self.win, f'Cannot validate guess after the game is finished.'
        is_correct = self._game.validate_guess(guess)
        print(f"Judge model {self.judge_model} response: {is_correct}")
        if is_correct:
            self.win = True
            self.win_time = time.time()
            self.total_game_time = self.win_time - self.start_time
        return is_correct
