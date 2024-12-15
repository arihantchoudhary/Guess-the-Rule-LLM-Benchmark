import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
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
import pdb
from anthropic import Anthropic

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_KEY)

ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
claude = Anthropic(api_key=ANTHROPIC_KEY)

claude_name_dict = {'claude-3-haiku': 'claude-3-haiku-20240307', 'claude-3.5-haiku':'claude-3-sonnet-20240229'}


class MathBase:
    def __init__(self,
                uuid,
                difficulty,
                rule_str=None,
                rule_code=None,
                gen_agent_type='gpt-4o-mini',
                validate_agent_type='gpt-4o-mini'):
        self.uuid = uuid
        self.difficulty = difficulty
        self.gen_sys_prompt = self.load_prompt('promptstrings/gen_sys_prompt_easy.txt')
        self.validate_sys_prompt = self.load_prompt('promptstrings/validate_sys_prompt.txt')
        L1_examples_math_str = self.load_prompt('promptstrings/L1_examples_math_str.txt')
        L1_examples_math_fns = self.load_prompt('promptstrings/L1_examples_math_fns.txt')
        L2_examples_math_str = self.load_prompt('promptstrings/L2_examples_math_str.txt')
        L2_examples_math_fns = self.load_prompt('promptstrings/L2_examples_math_fns.txt')
        L3_examples_math_str = self.load_prompt('promptstrings/L3_examples_math_str.txt')
        L3_examples_math_fns = self.load_prompt('promptstrings/L3_examples_math_fns.txt')
        self.gen_sys_prompt += 'Here is some examples of L1 level math sequence description: ' + L1_examples_math_str
        self.gen_sys_prompt += 'Here is some examples of L1 level math sequence function: ' + L1_examples_math_fns
        self.gen_sys_prompt += 'Here is some examples of L2 level math sequence description: ' + L2_examples_math_str
        self.gen_sys_prompt += 'Here is some examples of L2 level math sequence function: ' + L2_examples_math_fns
        self.gen_sys_prompt += 'Here is some examples of L3 level math sequence description: ' + L3_examples_math_str
        self.gen_sys_prompt += 'Here is some examples of L3 level math sequence function: ' + L3_examples_math_fns

        
        self.sequence_length = 15
        self.validate_agent_type = validate_agent_type
        self.gen_agent_type = gen_agent_type
        if rule_str is None or rule_code is None:
            self.rule_str, self.rule_code = self.get_math_rule()
        else:
            self.rule_str = rule_str
            self.rule_code = rule_code

    """ Get different responses from different models """
    def get_llm_response(self, prompt, model, sysprompt=None):
        if model in ['gpt-4o-mini', 'gpt-4o']:
            response = self.get_openai_response(prompt, model, sysprompt)
        elif model in ['claude-3-haiku', 'claude-3.5-haiku']:
            model_name = claude_name_dict[model]
            response = self.get_claude_response(prompt, model_name, sysprompt)
        return response

    def get_openai_response(self, prompt, model="gpt-4o-mini", sysprompt=None):
        response = openai.chat.completions.create(model=model,
                messages=[
                    {"role": "system", "content": sysprompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7)
        return response.choices[0].message.content.strip()
    
    def get_claude_response(self, prompt, model="claude-3.5-haiku", sysprompt=None):
        response = claude.messages.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            system=sysprompt,
            max_tokens=1000,
            temperature=0.7)
        return response.content[0].text.strip()
    
    """ Load tools"""
    def load_prompt(self, filename):
        with open(filename, 'r') as f:
            return f.read()
        
    """" Get rule details"""
    def get_math_rule(self):
        user_prompt = f'Your uuid is {self.uuid}. Please make sure your rule is different every time you generate a rule'
        user_prompt += f'difficulty: {self.difficulty}\n'
        user_prompt += 'please give me the math sequence and math function in the format of your system prompt'
        response = self.get_llm_response(user_prompt, self.gen_agent_type, self.gen_sys_prompt)   
        rule_str, rule_code = self.string2func(response)
        return rule_str, rule_code
    
    def string2func(self,rule):
        str_start_index = rule.find("Mathematical rule:")
        str_end_index = rule.find("$$")
        rule_str = rule[str_start_index:str_end_index].replace("Mathematical rule:", "").strip()
        
        # Extract Python Function Code
        fc_start_idx = rule.find("def")
        if fc_start_idx == -1:
            print("Error: Generated rule does not contain a valid function definition.")
            return []
        fc_end_index = rule.find("&&")
        rule_code = rule[fc_start_idx:fc_end_index]
        rule_code = rule_code.replace("```python", "").replace("```", "").strip()
        return rule_str, rule_code
    
    """ Generate sequence """
    def generate_single_sequence(self,rule_code):
        """
        Generate a sequence using the provided Python-style function code.
        """
        # Define the function from the generated code
        exec(rule_code, globals())
        sequence = []
        current_value = random.randint(-10, 10)
        for i in range(self.sequence_length):
            sequence.append(current_value)
            try:
                current_value = generate_next(current_value, i)
            except Exception as e:
                print(f"Error generating sequence with rule function: {e}")
                break
        return sequence
    
    def generate_multi_sequence(self, num_examples=5):
        examples = []
        for i in range(num_examples):
            sequence = self.generate_single_sequence(self.rule_code)
            examples.append(sequence)
        return examples
    
    """ Process """
    def get_more_examples(self):
        if self.rule_str is None:
            self.rule_str, self.rule_code = self.get_math_rule()
        examples = self.generate_multi_sequence()
        return examples

    def validate_result(self, guess):
        user_prompt = ''
        user_prompt += f'the rule to guess is: {self.rule_str}\n'
        user_prompt += f'the rule of the generation function is {self.rule_code}\n'
        user_prompt += f'the rule that the user guess is {guess}\n, please validate the guess and return True if they are consistent or return False if they are not'
        validate_result = self.get_llm_response(user_prompt, self.validate_agent_type, self.validate_sys_prompt)
        return validate_result
    

    """ Save Game"""
    def save_game(self, GAMES_SAVE_DIR='./saved_games'):
        os.makedirs(GAMES_SAVE_DIR, exist_ok=True)
        print(f"Saved game data to {GAMES_SAVE_DIR}")
        game_data = {
            'uuid': self.uuid,
            'difficulty': self.difficulty,
            'rule_str': self.rule_str,
            'rule_code': self.rule_code
        }
        game_file = os.path.join(GAMES_SAVE_DIR, f'{self.uuid}.json')
        with open(game_file, 'w') as f:
            json.dump(game_data, f)
        return game_file
    


class MathGuessTheRuleGame(GuessTheRuleGame):  

    def load_game(self, uuid, GAMES_SAVE_DIR='./saved_games'):
        game_file = os.path.join(GAMES_SAVE_DIR, f'{uuid}.json')
        if not os.path.exists(game_file):
            raise FileNotFoundError(f"No game file found for UUID {uuid} at {game_file}")

        with open(game_file, 'r') as f:
            game_data = json.load(f)

        return MathBase(
            uuid=game_data['uuid'],
            difficulty=game_data['difficulty'],
            rule_str=game_data['rule_str'],
            rule_code=game_data['rule_code']
        )
        

    def create_game_instance(self, difficulty, return_json=False):
        """
        Create a new game instance by generating multiple examples.
        """
        assert not self.uuid, 'Cannot create a new game with an already generated UUID'
        self.game_class_name = self.__class__.__name__
        uuid = uuid.uuid4()
        math_base = MathBase(uuid, difficulty)
        if return_json:
            return {
                'uuid': math_base.uuid,
                'difficulty': math_base.difficulty,
                'rule_str': math_base.rule_str,
                'rule_code': math_base.rule_code
            }
        else:
            return math_base

    def get_more_examples(self, math_base_instance):
        """
        Generate additional examples for the current rule.
        """
        # Use MathBase to generate more examples
        return math_base_instance.generate_multi_sequence()

    def validate_guess(self, math_base_instance, guess):
        """
        Validate the user's guess against the rule.
        """
        # Use MathBase to validate the user's guess
        if math_base_instance.validate_result(guess) == 'True':
            return True
        elif math_base_instance.validate_result(guess) == 'False':
            return False
        else:
            print('Value Error: validate result is not True or False')
            return False

    

def demo_play(difficulty, admin=False):
    game = MathBase(uuid=0, difficulty=difficulty)
    welcome_message = "Welcome to the Math Function Game! In this game, you will be given a sequence of numbers and you have to guess the function that generates the sequence. Let's get started!"
    print(welcome_message)
    flag = True
    while(True):
        examples = game.get_more_examples()
        if admin and flag==True:
            print(f"Rule Str is {game.rule_str}")
            print(f"Rule code is {game.rule_code}")
            flag = False

        print(examples)
        guess = input("Please guess the rule: ")
        if guess == 'exit':
            break
        elif guess == 'more':
            print("Okay, Here are more examples:")
            examples = game.get_more_examples()
            print(examples)
        else:
            result = game.validate_result(guess)
            print(f'result from validation: {result}')
            if result=='True':
                print("You are correct!")
            elif result=='False':
                print("You are wrong!")
            else:
                print(f"Error: validate result is not True or False. Result: {result}")
            cont = input("Do you want to continue? (y/n)")
            if cont == 'n':
                break
    print("Thanks for playing!")



if __name__ == "__main__":
    demo_play(difficulty='L2', admin=True)
    demo_play(difficulty='L2', admin=True)
    demo_play(difficulty='L2', admin=True)
    demo_play(difficulty='L2', admin=True)
    demo_play(difficulty='L2', admin=True)
    demo_play(difficulty='L2', admin=True)

    
