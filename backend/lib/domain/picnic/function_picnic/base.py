import os
import pickle
import random
from openai import OpenAI
import string
import nltk
import uuid
import time
from lib.domain.base import GuessTheRuleGame
from lib.domain.common import GAMES_SAVE_DIR
import anthropic
import google.generativeai
# import pandas as pd

# Set your OpenAI API key (or any other LLM provider's key)
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# juno : for testing purposes
if not OPENAI_KEY and os.path.exists('/mnt/c/Users/juno/Desktop/llmstuff/secretkey'):
    with open('/mnt/c/Users/juno/Desktop/llmstuff/secretkey', 'r') as f:
        OPENAI_KEY = f.read().strip()
        OpenAI.api_key = OPENAI_KEY

openai_client = client = OpenAI(api_key=OPENAI_KEY)

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
google.generativeai.configure(api_key=GOOGLE_API_KEY)

# juno : for testing purposes
if not GOOGLE_API_KEY and os.path.exists('/mnt/c/Users/juno/Desktop/llmstuff/secretkey_goog'):
    with open('/mnt/c/Users/juno/Desktop/llmstuff/secretkey_goog', 'r') as f:
        GOOGLE_API_KEY = f.read().strip()
        google.generativeai.configure(api_key=GOOGLE_API_KEY)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# juno : for testing purposes
if not ANTHROPIC_API_KEY and os.path.exists('/mnt/c/Users/juno/Desktop/llmstuff/secretkey_claude'):
    with open('/mnt/c/Users/juno/Desktop/llmstuff/secretkey_claude', 'r') as f:
        ANTHROPIC_API_KEY = f.read().strip()
        anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

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
    pth = os.path.join(current_dir, 'promptstrings', filename)
    if not os.path.exists(pth):
        return 'Empty file\n'
    with open(pth, 'r') as f:
        promptstring = f.read()
    return promptstring

def write_history(filename, txt):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_dir, 'promptstrings', filename), 'a') as f:
        f.write(txt)
    return
class GuessingGame:

    def __init__(self, rngstate, domain=None, difficulty=None, init_examples=None, use_llm=True):
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
        if self.init_examples:
            prompt += f"Examples: {self.init_examples}\n\n"
        # don't repeat
        prompt += 'Here are some BAD examples, which did not evenly split between True/False:\n'
        prompt += read_promptstring(f'negative_history_{self.difficulty}.txt')
        prompt += 'Here are some GOOD examples (which you should reference, but not copy):\n'
        prompt += read_promptstring(f'history_{self.difficulty}.txt')
        prompt += "Generated code:"

        sysprompt = read_promptstring('sysprompt.txt')
        sysprompt += '\n'
        if self.difficulty == 'L1':
            sysprompt += 'Your function should be very simple. You are encouraged to use simple attributes, '
            sysprompt += 'like the length of the word, or the first letter.\n'
            sysprompt += 'You should try to make sure your function does not use multiple lines.\n'
            sysprompt += 'You should make sure not to use the "and" operator to chain together complex rules.\n'
            sysprompt += 'If you can\'t think of a good, simple example, it is okay to repeat one of the previous GOOD examples.'
        if self.difficulty == 'L3':
            sysprompt += 'Your function should be very creative and original (while still splitting words fairly evenly).\n'
            sysprompt += 'You are encouraged to use keywords like "and" and "not" to string together a complex rule.'
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
                print('problem assigning "generated_fn"')
                return self.generate_rule_chatgpt()
        except SyntaxError as e:
            print("Syntax Error in Generated Code:", e)
            return self.generate_rule_chatgpt()
        # test if it's a reasonable rule (sometimes true/false)
        exs = [self.wordgen_fn() for _ in range(50)]
        exs = [generated_fn(ex) for ex in exs]
        if not 4 < sum(exs) < 46:
            print('debug: rule failed', sum(exs))
            write_history(f'negative_history_{self.difficulty}.txt', ans_strip)
            return self.generate_rule_chatgpt()
        else:
            print('debug: rule success', sum(exs))
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
        print('debug (guess): ' + guess)
        print('debug (judge): ' + ans)
        ans_last = ans.split()[-1]
        print('debug: ' + ans_last)
        if ans_last not in ['YES', 'NO']:
            print('invalid LLM output')
            raise Exception
        return ans_last == 'YES'

class CodeFunctionsPicnic(GuessTheRuleGame):

    def __init__(self, uuid=None, difficulty=None, num_init_examples=None):
        self.domain = 'lexical'
        self.game_gen_type = 'dynamic'
        super().__init__(uuid, difficulty, num_init_examples)

    def make_init_system_message(self, positive_examples, negative_examples):
        positives_string = ', '.join(positive_examples)
        negatives_string = ', '.join(negative_examples)
        return (
            f"Let's play the game 'going on a picnic'.\n\n"
            f"I will give you some examples in each turn and you have to guess the underlying rule of the game. The rule will be common for all the examples.\n"
            f"Your score will be based on the number of turns taken, number of examples seen, and overall time elapsed playing the game. The highest score will be for the fewest turns taken, fewest examples seen, and shortest game played.\n"
            f"The rule you will guess should only encompass the positive examples. The negative examples are only for additional guidance and they do not form the underlying rule itself.\n"
            f"To play the game you can only do one of the following actions in a turn:\n"
            f"1. Request N more examples for that rule.\n"
            f"2. Type the rule if you think you've guessed it.\n\n"
            f"I can bring: {positives_string}\n"
            f"I cannot bring: {negatives_string}\n\n"
            f"What would you like to do?"
        )

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
        self.game_end_time = None
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
        system_message = self.make_init_system_message(positives, negatives)
        return {
            'game_uuid': str(self.uuid),
            'domain': self.domain,
            'difficulty': self.difficulty,
            'game_gen_type': self.game_gen_type,
            'start_time': time.ctime(int(self.start_time)),
            'turns_taken': self.turns,
            'status': self.status,
            'total_examples_available': self.total_examples_available,
            'system_message': system_message,
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
        # game = CodeFunctionsPicnic(uuid=state['uuid'])
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
    
    def make_validate_guess_system_message(self, guess_result):
        if guess_result is True:
            return 'You guessed correctly. Check your performance stats in the panel above. Thanks for playing!'
        elif self.status == 'lost':
            return 'Incorrect guess. Game over!'
        else:
            return 'Incorrect guess. What would you like to do next?'

    def validate_guess(self, guess):
        assert not self.win, f'Cannot validate guess after the game is finished.'
        if self.status != 'ongoing':
            return {
                'game_uuid': str(self.uuid),
                'status': self.status,
                'guess_result': False,
                'system_message': 'Cannot validate guess after the game is finished.'
            }        
        is_correct = self._game.validate_guess(guess)

        # if self.total_examples_available - self.total_pos_examples_shown <= 0:
        #     self.status = 'lost'
        #     self.game_end_time = time.time()
        #     self.total_game_time = self.game_end_time - self.start_time
        
        self.save_game()

        print(f"Judge model {self.judge_model} response: {is_correct}")
        if is_correct:
            self.win = True
            self.status = 'win'
            self.game_end_time = time.time()
            self.total_game_time = self.game_end_time - self.start_time

        return {
            'game_uuid': str(self.uuid),
            'status': self.status,
            'guess_result': is_correct,
            'system_message': self.make_validate_guess_system_message(is_correct),
        }
    
    def make_game_history_system_message(self):
        if self.status == 'ongoing':
            positives_string = ', '.join(list(self.history['positives']))
            negatives_string = ', '.join(list(self.history['negatives']))
            msg = (
                f"Welcome back to the game 'going on a picnic'.\n\n"
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
            if self.total_examples_available - self.total_pos_examples_shown <= 0:
                msg += '\n(This is the last turn because there are no more examples available)'
            return msg
        else:
            return f'Game is over. You {self.status}. The rule was {self.rule}.\nCheck your stats in the top panel.'

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
            'system_message': system_message
        }
        if include_rule or self.status in ['won', 'lost']:
            response['rule'] = self.rule

        return response    

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

def get_llm_model_response(platform, model, message_history):
    if platform == 'openai':
        response = openai_client.chat.completions.create(
            model=model,
            messages=message_history
        )
        return response.choices[0].message.content.strip().lower()
    elif platform == 'anthropic':
        system_prompt = ''
        user_prompts = []
        for m in message_history:
            if not system_prompt and m['role'] == 'system':
                system_prompt += m['content']
            elif m['role'] == 'user':
                user_prompts.append(m)

        response = anthropic_client.messages.create(
            max_tokens=1024,
            system=system_prompt,
            messages=user_prompts,
            model=model,
        )
        return response.content[0].text.strip().lower()
    elif platform == 'google':
        # change the format of message history for google's model
        google_messages_history = []
        for m in range(len(message_history) - 1):
            curr_message = message_history[m]
            if curr_message['role'] == 'system':
                google_messages_history.append({'role': 'model', 'parts': curr_message['content']})
            elif curr_message['role'] == 'user':
                google_messages_history.append({'role': 'user', 'parts': curr_message['content']})

        gen_model = google.generativeai.GenerativeModel(model)
        chat = gen_model.start_chat(
            history=google_messages_history
        )
        response = chat.send_message(message_history[-1]['content'])
        return response.text
    else:
        assert False, f'Unknown platform {platform} given'

def simulate_llm_guess(game, examples, platform, model):
    prompt = (
        f"You are playing a game called 'Going on a Picnic'. Your goal is to guess the rule behind a set of examples.\n"
        f"The rule is string-manipulation based, and does NOT consider the meaning/category of the words; only attributes like"
        f"length, number of vowels, etc.\n"
        f"It can be expressed in simple Python code, although you are not required to output code--it is enough to just explain the rule in plain English.\n"
        f"Here are some previously played games with words and answers, so you can learn how to play:\n<BEGIN TUTORIAL>\n"
    ) + (
        f"Game 1: I can bring: slaw, moly\n I cannot bring veronal, unwhite, ennomic\n"
        f"Answer: would be 'even length'\n"
        f"Game 2: I can bring: aciform, onsweep, again, analgia\n"
        f"I cannot bring: roleos, medimn, bunnell, lapacho, skinful"
        f"Answer: 'start with vowel'\n\n"    
    ) + (
        f"Game 3: I can bring: slaw, moly\n I cannot bring: letter, veronal, unwhite, ennomic\n"
        f"Answer: 'even length and no repeat letters'.\n"
        f"Game 4:I can bring: aciform, onsweep, again, analgia\n"
        f"I cannot bring: roleo, medimn, bunnell, lapacho, skinful"
        f"Answer: 'odd length and start with vowel'\n\n"
    ) if game.difficulty in ['L2', 'L3'] else "" + (
        f"<END TUTORIAL>\n\nNow you know how to play. You will now play a new game with a different rule than the examples.\n"
        f"The above examples were only to teach you the rules, and they do not count for our new game.\n"
        f"Do not discuss the example games above.\n"
        f"Do not ask for clarification or ask questions. Simply answer what I am about to ask."
        f"NEW GAME:\n"
        f"I can bring: {', '.join(examples[0])}\n"
        f"I cannot bring: {', '.join(examples[1])}\n"
        f"What is the rule? State your answer specifically in clear English."
    )
    
    message_history = [
        {"role": "system", "content": "You are playing a game called 'Going on a Picnic'. Your goal is to guess the rule behind a set of examples."},
        {"role": "user", "content": prompt}
    ]
    
    try:
        llm_guess = get_llm_model_response(platform, model, message_history)
        return llm_guess
    except Exception as e:
        print(f"Error during LLM interaction: {e}")
        return None

def make_example_pair(game):
    ans = [None, None]
    while not (ans[0] and ans[1]):
        word, boole = game.generate_example()
        print('debug pair', word, boole)
        boole = int(boole)
        ans[boole] = word
    return ans

if __name__ == "__main__":
    # game = GuessingGame(random.getstate(), domain='lexical', difficulty='L1', init_examples=None, use_llm=True)
    # print(game.rule_code)
    llm_models = {
        'openai': ['gpt-4o-mini', 'gpt-4o'],
        'anthropic': ['claude-3-haiku-20240307'],
        'google': ['gemini-1.5-flash']
    }

    # Test parameters
    difficulties = ['L1']
    # max_turns_options = [1, 3, 5, 7]
    max_turns_options = [3]
    iterations = 2
    results = []

    for platform in llm_models:
        for model in llm_models[platform]:
            for difficulty in difficulties:
                for iteration in range(iterations):
                    start_time = time.time()
                    game = GuessingGame(
                        random.getstate(), 
                        domain='lexical', 
                        difficulty=difficulty, 
                        init_examples=None, 
                        use_llm=True
                    )
                    pos_exs, neg_exs = [], []
                    for _ in range(5):
                        pos, neg = make_example_pair(game)
                        pos_exs, neg_exs = pos_exs+[pos], neg_exs+[neg]
                    for max_turns in max_turns_options:
                        # Game loop
                        turns_taken = 0
                        examples_shown = 10
                        win = False
                        
                        while turns_taken < max_turns:
                            turns_taken += 1
                            # examples = game.generate_example()
                            pos, neg = make_example_pair(game)
                            pos_exs.append(pos)
                            neg_exs.append(neg)

                            examples_shown += 2
                            
                            # Simulate LLM guess (you'll need to implement actual LLM interaction)
                            try:
                                llm_guess = simulate_llm_guess(game, (pos_exs, neg_exs), platform, model)
                                if llm_guess:
                                    guess = game.validate_guess(llm_guess)
                                    if guess:
                                        win = True
                                        break
                            except Exception as e:
                                print(f"Error during validation: {e}")
                                break
                        
                        duration = time.time() - start_time
                        
                        # Record results
                        results.append({
                            "Model": model,
                            "Win": 1 if win else 0,
                            "Difficulty": difficulty,
                            "Max_Turns": max_turns,
                            "Iteration": iteration + 1,
                            "Rule": game.rule_code,
                            "Turns_Taken": turns_taken,
                            "Duration": round(duration, 2),
                            "Examples_Shown": examples_shown
                        })

    # Create and save results
    df = pd.DataFrame(results)
    df.to_csv(f"lexical_game_results.csv", index=False)

    # Generate summary statistics
    summary = df.groupby(['Model', 'Difficulty', 'Max_Turns']).agg({
        'Win': 'mean',
        'Turns_Taken': 'mean',
        'Duration': 'mean',
        'Examples_Shown': 'mean'
    }).round(2)

    summary.to_csv(f"lexical_game_summary.csv")
    print("\nResults Summary:")
    print(summary)
