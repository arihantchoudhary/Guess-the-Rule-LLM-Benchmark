# game_master_module.py

import random
import json
import os
import sys
from openai import OpenAI
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(script_dir, '..')))

keys_path = os.path.join(script_dir, 'keys.json')
with open(keys_path, 'r') as f:
    keys = json.load(f)
OPENAI_KEY = keys['OPENAI_API_KEY']
client = OpenAI(api_key=OPENAI_KEY)

def load_secret_rule(rule_type, directory):
    filename = os.path.join(directory, f"{rule_type}_rules.json")
    with open(filename, 'r') as f:
        rules = json.load(f)
    secret_rule = random.choice(rules)
    return secret_rule['rule']

def generate_game_master_prompt(secret_rule):
    prompt = f"""
You are the game master for "Going on a Picnic." The secret rule is: {secret_rule}

When the player asks if they can bring an item, respond with:

- "Yes, you can bring [item]." if the item satisfies the secret rule.
- "No, you cannot bring [item]." if the item does not satisfy the secret rule.

If the player attempts to guess the rule, respond with:

- "Correct! The rule is {secret_rule}." if they guess correctly.
- "Incorrect. Please try again." if they guess incorrectly.

Do not reveal the secret rule unless the player guesses it correctly.

Keep your responses concise and do not provide additional hints unless specified.
"""
    return prompt

def game_master_response(player_message, secret_rule, game_master_prompt):
    # Construct the conversation
    messages = [
        {"role": "system", "content": game_master_prompt},
        {"role": "user", "content": player_message}
    ]
    # Get the response from the game master (GPT-4)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0
    )
    reply = response.choices[0].message.content.strip()
    return reply