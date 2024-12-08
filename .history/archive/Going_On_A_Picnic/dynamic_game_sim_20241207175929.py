# dynamic_game_sim.py

import os
import json
import random
import datetime
import re  # Import regex module
from openai import OpenAI

# Get the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Load the API key from 'keys.json'
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

- "Yes, you can bring [guess]." if their guess satisfies the secret rule.
- "No, you cannot bring [guess]." if their guess does not satisfy the secret rule.

If the player asks for more examples, or requests another example, respond with:

- Provide another example of an item that can be brought to the picnic according to the secret rule.
- Do not repeat any examples you have already provided.

If the player attempts to guess the rule, respond with:

- "Correct! The rule is {secret_rule}." if they guess correctly.
- "Incorrect. Please try again." if they guess incorrectly.

Do not reveal the secret rule unless the player guesses it correctly. Rule guessing should be evaluated rigidly. Please use your judgment. If the rule guess is phrased differently, only count it as correct if the player's guess is semantically identical.

Keep your responses concise and do not provide additional hints unless specified.
"""
    return prompt

def game_master_response(player_message, conversation, provided_examples):
    # Create a deep copy of the conversation to avoid modifying the original
    current_conversation = conversation.copy()
    
    # Append the player's message to our local copy
    current_conversation.append({"role": "user", "content": player_message})

    # Get the response from the game master (GPT-4)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=current_conversation,
        temperature=0
    )
    reply = response.choices[0].message.content.strip()

    # Append the assistant's reply to the original conversation
    conversation.append({"role": "user", "content": player_message})
    conversation.append({"role": "assistant", "content": reply})

    # If the game master provides a new example, add it to the provided_examples set
    if "you can bring" in reply.lower() and ("example" in player_message.lower() or "another example" in player_message.lower()):
        # Extract the item from the reply
        match = re.search(r'you can bring\s+(.*?)[\.\!]', reply, re.IGNORECASE)
        if match:
            new_example = match.group(1).strip('"\'')
            provided_examples.add(new_example)

    return reply

def generate_examples(secret_rule, num_examples=2):
    prompt = f"""
You are an assistant helping to generate examples for a game called "Going on a Picnic."

The secret rule is: {secret_rule}

Your task is to provide {num_examples} examples of items that satisfy the secret rule.

- Only provide the items in a simple, comma-separated list.
- Do not mention the secret rule.
- Do not provide any additional explanation or text.

Format:

[item1], [item2], ..., [item{num_examples}]
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    examples_text = response.choices[0].message.content.strip()
    # Remove any leading or trailing characters like quotation marks
    examples_text = examples_text.strip('"\'')
    # Split the examples and strip whitespace
    examples = [item.strip() for item in examples_text.split(',') if item.strip()]
    return examples

def save_log(log, rule_type):
    logs_directory = os.path.join(script_dir, 'logs')
    os.makedirs(logs_directory, exist_ok=True)

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f"log_{rule_type}_{timestamp}.json"
    log_path = os.path.join(logs_directory, log_filename)

    with open(log_path, 'w') as f:
        json.dump(log, f, indent=4)

    print(f"Game log saved to {log_path}")

def automated_player_game(rule_type, max_turns=20, output_directory=None):
    # Load the secret rule for the game
    rules_directory = os.path.join(script_dir, 'rules', rule_type)
    secret_rule = load_secret_rule(rule_type, rules_directory)

    # Generate the game master's initial prompt with the secret rule
    game_master_prompt = generate_game_master_prompt(secret_rule)

    # Initialize conversations
    game_master_conversation = [{"role": "system", "content": game_master_prompt}]
    player_visible_history = []  # Only store what the player should see

    provided_examples = set()

    # Generate initial examples for the player
    examples = generate_examples(secret_rule, num_examples=2)
    examples_text = ' and '.join(f'"{item}"' for item in examples)
    initial_message = f"To start, here are some examples of items you can bring: {examples_text}."
    
    # Add initial message to conversations
    game_master_conversation.append({"role": "assistant", "content": initial_message})
    player_visible_history.append({"role": "assistant", "content": initial_message})
    
    # Display the initial message from the game master
    print("\nGame Master:", initial_message, "\n")

    # Initialize the player LLM
    player = OpenAI(api_key=OPENAI_KEY)

    attempts = 0
    game_over = False
    rule_guessed = False

    # Simulate the player's turn loop with dynamic prompts
    while not game_over and attempts < max_turns:
        # Format the conversation history for the player
        conversation_history = "\n".join([
            f"{'Game Master' if msg['role'] == 'assistant' else 'Player'}: {msg['content']}"
            for msg in player_visible_history
        ])

        if attempts == max_turns - 1:
            player_prompt = f"""
You are a player in a game called "Going on a Picnic." This is your final turn, so you must make your best guess about the secret rule.
Based on the game master's responses, try to guess the rule as accurately as possible.

The game master has provided examples: {examples_text}.

Here's the conversation history:
{conversation_history}

Please make your best guess about the rule as this is your last opportunity.
            """
        else:
            player_prompt = f"""
You are a player in a game called "Going on a Picnic." You are trying to guess the secret rule by asking if certain items can be brought to the picnic. 
The game master has given examples of items that fit the rule: {examples_text}.

Here's the conversation history:
{conversation_history}

Based on this history, either:
1. Ask about a new item that hasn't been mentioned before
2. Try to guess the rule if you think you understand it

Be strategic and avoid repeating previous guesses or items.
            """

        # Get the player LLM's response
        response = player.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": player_prompt}],
            temperature=0.7
        )
        player_message = response.choices[0].message.content.strip()
        
        # Add player's message to player history
        player_visible_history.append({"role": "user", "content": player_message})

        # Game master responds to the player's guess
        reply = game_master_response(player_message, game_master_conversation, provided_examples)

        # Add game master's reply to player history
        player_visible_history.append({"role": "assistant", "content": reply})

        # Display each turn in the console
        print(f"Attempt {attempts + 1}: Player: {player_message}")
        print(f"Game Master: {reply}\n")

        # Check if the rule was guessed correctly
        if "Correct! The rule is" in reply:
            print(f"Rule guessed correctly in {attempts + 1} attempts!")
            game_over = True
            rule_guessed = True
        elif attempts + 1 >= max_turns:
            print("Game over: Maximum attempts reached.")
            print(f"The secret rule was: {secret_rule}")
            game_over = True

        attempts += 1

    # Metrics to save
    metrics = {
        "rule_type": rule_type,
        "secret_rule": secret_rule,
        "max_turns_allowed": max_turns,
        "turns_taken": attempts,
        "rule_guessed": rule_guessed,
        "conversation": player_visible_history
    }

    # Save logs
    if output_directory is None:
        output_directory = os.path.join(script_dir, 'logs')
    os.makedirs(output_directory, exist_ok=True)

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f"game_log_{rule_type}_{timestamp}.json"
    log_path = os.path.join(output_directory, log_filename)

    with open(log_path, 'w') as f:
        json.dump(metrics, f, indent=4)

    print(f"Game log and metrics saved to {log_path}")

if __name__ == "__main__":
    # all_rule_types = [
    #     'attribute_based', 
    #     'categorical',
    #     'logical',
    #     'relational',
    #     'semantic'
    # ]
    rule_type = 'attribute_based'
    max_turns = 6
    log_dir = os.path.join(script_dir, 'logs/llm_player')
    automated_player_game(rule_type, max_turns, log_dir)
    # play_game(rule_type)