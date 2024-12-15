import time
from base import MathBase
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
from datetime import datetime
import pandas as pd
import random
import time
import uuid




"""Import OpenAI and Anthropic API keys"""
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_KEY)
ANTHROPIC_KEY = os.getenv("CLAUDE_API_KEY")
claude = Anthropic(api_key=ANTHROPIC_KEY)
claude_name_dict = {'claude-3-haiku': 'claude-3-haiku-20240307', 'claude-3.5-haiku':'claude-3-5-haiku-20241022'}


"""Get different responses from different models"""
def get_llm_response(prompt, model, sysprompt=None):
        if model in ['gpt-4o-mini', 'gpt-4o']:
            response = get_openai_response(prompt, model, sysprompt)
        elif model in ['claude-3-haiku', 'claude-3.5-haiku']:
            model_name = claude_name_dict[model]
            response = get_claude_response(prompt, model_name, sysprompt)
        return response

def get_openai_response(prompt, model="gpt-4o-mini", sysprompt=None):
    response = openai.chat.completions.create(model=model,
            messages=[
                {"role": "system", "content": sysprompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7)
    return response.choices[0].message.content.strip()

def get_claude_response(prompt, model="claude-3.5-haiku", sysprompt=None):
    response = claude.messages.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        system=sysprompt,
        max_tokens=1000,
        temperature=0.7)
    return response.content[0].text.strip()

def load_prompt(filename):
        with open(filename, 'r') as f:
            return f.read()

def play_math_with_llms(difficulty, max_turns, model, uuid):
    game = MathBase(uuid=uuid, difficulty=difficulty)
    turns = 1
    test_llm_sys_prompt = load_prompt('promptstrings/test_llm_sys_prompt.txt')
    test_prompt = ''
    rule = game.rule_str
    time_start = time.time()
    time_end = None
    llm_actions = []
    llm_won = False
    examples_num = 0
    while(turns < max_turns):
        try:
            examples = game.get_more_examples()
            examples_num += len(examples)
            test_prompt += str(examples)
            response = get_llm_response(test_prompt, model, sysprompt=test_llm_sys_prompt)
            assert response, 'No response from LLM'
            # print(f"Response: {response}")
            
            if response == 'More':
                turns += 1
                llm_actions.append(response)
                continue
            elif response.startswith('My Guess is:'):
                guess = response.split('My Guess is:')[1].strip()
                if game.validate_result(guess) == 'True':
                    # print(f"LLM Guessed Correctly: {guess}")
                    # print(f'{game.rule_str}')
                    time_end = time.time()
                    llm_actions.append(response)
                    llm_won = True
                    break
                elif game.validate_result(guess) == 'False':
                    # print(f"LLM Guessed Incorrectly: {guess}")
                    # print(f'{game.rule_str}')
                    turns += 1
                    llm_actions.append(response)
                    continue
                else:
                    turns += 1
                    llm_actions.append(response)
                    continue
        except Exception as e:
            print(f"Error: {e}")
            game = MathBase(uuid=uuid, difficulty=difficulty)
            turns = 1
            test_llm_sys_prompt = load_prompt('promptstrings/test_llm_sys_prompt.txt')
            test_prompt = ''
            rule = game.rule_str
            time_start = time.time()
            time_end = None
            llm_actions = []
            llm_won = False
            examples_num = 0
            continue

    del game

    if time_end is None:
        time_end = time.time()
    duration = time_end - time_start
    # print("\n***Game Summary***")
    # print(f"Rule: {rule}")
    # print(f"Turns taken: {turns}")
    # print(f"Duration: {duration:.2f} seconds")
    # print(f'Test Prompt: {test_prompt}')
    # print(f'LLM Actions: {llm_actions}')
    # print(f'LLM Won: {llm_won}')
    return rule, turns, duration, test_prompt, llm_actions, llm_won, examples_num
    

if __name__ == "__main__":
    save_dir = 'exp_results'
    # valid_difficulties = ['L1', 'L2', 'L3']
    valid_difficulties = ['L2']
    # max_turns = [3, 5, 7, 10]
    max_turn_dict = {'L1': 10, 'L2': 15, 'L3': 20}

    total_iterations = 5
    # models = ['gpt-4o-mini', 'gpt-4o', 'claude-3-haiku', 'claude-3.5-haiku']
    # models = ['claude-3.5-haiku']
    models = ['gpt-4o-mini']

    results = []
    for model in models:
    # run experiments 
        for difficulty in valid_difficulties:
            max_turns = [max_turn_dict[difficulty]]
            for curr_max_turns in max_turns:
                for iteration in range(total_iterations):
                    current_uuid = str(uuid.uuid4())
                    rule, turns, duration, test_prompt, llm_actions, llm_won, examples_num = play_math_with_llms(difficulty, curr_max_turns, model, current_uuid)
                    # Append the results to the list
                    results.append({
                        "Model": model,
                        "Win": 1 if llm_won else 0, # 1 or 0
                        "Difficulty": difficulty,
                        "Max Turns": curr_max_turns,
                        "Iteration": iteration+1,
                        "Turns Taken": turns,
                        "Duration (s)": round(duration, 2),
                        "Total Examples Avaiable": examples_num,
                        "Rule": rule,
                        "LLM Final Answer": llm_actions[-1]
                    })
                    print(f'down: {model} - {difficulty} - {curr_max_turns} - {iteration+1} - {rule} - {llm_won} - {turns} - {duration:.2f} - {examples_num}')

    current_date = datetime.now()
    formatted_date = current_date.strftime("%m_%d_%Y")

    df = pd.DataFrame(results)
    print(f"\n*** FINAL RESULTS {formatted_date} ***")
    print(df)

    experiment_results_file_name_csv = os.path.join(save_dir, f"experiment_{formatted_date}.csv")
    experiment_results_file_name_excel = os.path.join(save_dir, f"experiment_{formatted_date}.xlsx")

    # to csv file
    if os.path.exists(experiment_results_file_name_csv):
        existing_df = pd.read_csv(experiment_results_file_name_csv)
        updated_df = pd.concat([existing_df, df], ignore_index=True)
        updated_df.to_csv(experiment_results_file_name_csv, index=False)
    else:
        df.to_csv(experiment_results_file_name_csv, index=False)

    # to excel file
    if os.path.exists(experiment_results_file_name_excel):
        existing_df = pd.read_excel(experiment_results_file_name_excel, engine='openpyxl')
        updated_df = pd.concat([existing_df, df], ignore_index=True)
        updated_df.to_excel(experiment_results_file_name_excel, index=False, engine='openpyxl')
    else:
        df.to_excel(experiment_results_file_name_excel, index=False, engine='openpyxl')
