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
        self.domain = 'math'
        self.game_gen_type = 'dynamic'
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
        current_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(current_dir, filename)
        with open(filepath, 'r') as f:
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
    
    


class MathGuessTheRuleGame(GuessTheRuleGame):  
    def __init__(self, uuid=None, domain=None, difficulty=None, num_init_examples=None, game_gen_type=None, rule=None, rule_code=None):
        super().__init__(uuid, domain, difficulty, num_init_examples, game_gen_type)
        self.rule_str = None
        self.rule_code = None
    
    def add_to_conversation(self, role, content):
        self.history["conversation"].append({
            "role": role,
            "content": content
        })
    
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
    
    def make_init_system_message(self, generated_examples):
        generated_examples_str = ', '.join(str(generated_examples))
        return (
            f"Let's play the game 'Find Principle Behind Math Sequence'.\n\n"
            f"I will give you some examples in each turn and you have to guess the underlying rule of the math sequence. "
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

    def create_game_instance(self):
        """
        Create a new game instance by generating multiple examples.
        """
        assert not self.uuid, 'Cannot create a new game with an already generated UUID'
        self.game_class_name = self.__class__.__name__
        import uuid
        uuid = uuid.uuid4()
        self.uuid = uuid
        self.math_base = MathBase(uuid, self.difficulty)
        self.rule_str = self.math_base.rule_str
        self.rule_code = self.math_base.rule_code
        
        self.judge_model = 'gpt-4o-mini'
        
        self.start_time = time.time() 
        self.game_end_time = None
        self.total_game_time = None
        self.turns = 0
        self.status = 'ongoing'
        self.history = {"conversation": []}
        self.game_gen_type = 'dynamic'



        generated_examples = self.math_base.get_more_examples()
        system_message = self.make_init_system_message(generated_examples)
        self.add_to_conversation("assistant", system_message)
        self.system_prompt = self.math_base.gen_sys_prompt
        
        self.save_game()
        return {
            'game_uuid': str(self.uuid), # FE IN
            'domain': self.domain, # FE IN
            'difficulty': self.difficulty, # FE IN
            'game_gen_type': self.game_gen_type, # FE IN
            'start_time': time.ctime(int(self.start_time)), # FE IN
            'turns_taken': self.turns, # FE IN
            'status': self.status, # FE IN
            'system_message': self.system_prompt, # FE IN
        }
    
    def load_game(self, uuid_str=None):
        assert self.uuid or uuid_str, f'Could not find a uuid to load the game.'
        uuid_to_load = self.uuid or uuid_str
        filename = os.path.join(GAMES_SAVE_DIR, f'{uuid_to_load}.json')
        if not os.path.exists(filename):
            raise FileNotFoundError(f"No game file found for UUID {uuid} at {filename}")

        try:
            with open(filename, 'r') as f:
                state = json.load(f)
        except Exception as e:
            print(f"Error loading game state: {e}")
            raise
        
        game = MathGuessTheRuleGame(uuid=state['uuid'], 
                        difficulty=state['difficulty'], 
                        rule=state['rule_str'], 
                        rule_code=state['rule_code']
                        )
        game.__dict__.update(state)
        game.uuid = uuid.UUID(game.uuid)

        self.math_base = game

        return game
    

    def save_game(self):
        state = self.__dict__.copy()
        state.pop('math_base', None)


        state['uuid'] = str(self.uuid)
        state['start_time'] = self.start_time
        state['game_end_time'] = self.game_end_time

        print(f'state type: {type(state)}')

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

    def get_more_examples(self, n):
        if self.status != 'ongoing':
            return {
                'game_uuid': str(self.uuid),
                'status': self.status,
                'system_message': 'Cannot provide more examples after the game is finished.'
            }
        generated_examples = self.generate_examples(n)
        system_message = self.make_more_examples_system_message(generated_examples)
        self.add_to_conversation("assistant", system_message)

        self.save_game()
        return {
            'game_uuid': str(self.uuid),
            'status': self.status,
            'system_message': system_message
        }

    def validate_guess(self, guess):
        """
        Validate the user's guess against the rule.
        """
        if self.status != 'ongoing':
            return {
                'game_uuid': str(self.uuid),
                'status': self.status,
                'guess_result': False,
                'system_message': 'Cannot validate guess after the game is finished.'
            }
        result = self.math_base.validate_result(guess)
        system_message = self.make_validate_guess_system_message(result)
        self.add_to_conversation("assistant", system_message)
        
        self.save_game()
        return {
            'game_uuid': str(self.uuid),
            'status': self.status,
            'guess_result': result,
            'system_message': system_message,
        }
    
    def make_validate_guess_system_message(self, guess_result):
        if guess_result == 'True' or (type(guess_result) is str and "Yes" in guess_result):
            game_master_msg = 'You guessed the rule correctly! Check your performance stats in the panel above. Thanks for playing!'
            return game_master_msg
        else:
            game_master_msg = "Incorrect guess. What would you like to do next?"
            return game_master_msg

    

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

    
