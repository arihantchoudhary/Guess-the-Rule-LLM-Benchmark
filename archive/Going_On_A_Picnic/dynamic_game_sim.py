# dynamic_game_sim.py

import os
import json
import random
import datetime
import re
import time
from openai import OpenAI
import openai
import anthropic
from retry import retry
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------
# Configuration & Setup
# --------------------------

# Get the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Load the API keys from 'keys.json'
keys_path = os.path.join(script_dir, 'keys.json')
with open(keys_path, 'r') as f:
    keys = json.load(f)
OPENAI_KEY = keys['OPENAI_API_KEY']
openai_client = OpenAI(api_key=OPENAI_KEY)

ANTHROPIC_API_KEY = keys['ANTHROPIC_API_KEY']
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# --------------------------
# Helper Functions
# --------------------------
# def get_llm_model_response(platform, model, message_history):
#     """
#     A modular function to get responses from different LLM platforms.
#     Properly formats prompts for Anthropic models.
#     """
#     if platform == 'openai':
#         response = openai_client.chat.completions.create(
#             model=model,
#             messages=message_history
#         )
#         return response.choices[0].message.content.strip()

#     elif platform == 'anthropic':
#         # Use the Messages API rather than the Completions API
#         system_prompt = ''
#         user_prompts = []
#         for m in message_history:
#             if not system_prompt and m['role'] == 'system':
#                 system_prompt += m['content']
#             elif m['role'] == 'user':
#                 user_prompts.append(m)
#             # If there are assistant messages, you may need to include them as well,

#         response = anthropic_client.messages.create(
#             max_tokens=1024,
#             system=system_prompt,
#             messages=user_prompts,
#             model=model,
#         )
#         # Adjust the way we access the response depending on the actual structure.
#         # Your friend’s code suggests this format:
#         return response.content[0].text.strip().lower()

#     else:
#         raise ValueError(f"Unknown platform '{platform}' provided.")

@retry(tries=5, delay=1, exceptions=(anthropic.InternalServerError, openai.InternalServerError))
def get_llm_model_response(platform, model, message_history):
    if platform == 'openai':
        try:
            response = openai_client.chat.completions.create(
                model=model,
                messages=message_history
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI encountered an error: {e}")
            raise
        
    elif platform == 'anthropic':
        try:
            system_prompt = ""
            anthro_messages = []
            for m in message_history:
                if m['role'] == 'system' and not system_prompt:
                    system_prompt = m['content']
                elif m['role'] == 'system' and system_prompt:
                    system_prompt += "\n" + m['content']
                elif m['role'] == 'user':
                    anthro_messages.append({"role": "user", "content": m['content']})
                elif m['role'] == 'assistant':
                    anthro_messages.append({"role": "assistant", "content": m['content']})

            response = anthropic_client.messages.create(
                model=model,
                system=system_prompt,
                messages=anthro_messages,
                max_tokens=1024
            )

            assistant_text = ""
            for block in response.content:
                if block.type == 'text':
                    assistant_text += block.text

            return assistant_text.strip()
        except Exception as e:
            logger.error(f"Anthropic encountered an error: {e}")
            raise
    else:
        raise ValueError(f"Unknown platform '{platform}' provided.")

def load_secret_rule(rule_type, level_difficulty, directory):
    """
    Load a secret rule from a JSON file containing a list of rules.
    Filters rules based on rule_type and level_difficulty, then picks a random rule.
    """
    filename = os.path.join(directory, f"{rule_type}_rules.json")
    with open(filename, 'r') as f:
        rules = json.load(f)
    
    # Filter rules based on level_difficulty
    filtered_rules = [rule for rule in rules if rule.get('level') == level_difficulty]
    
    if not filtered_rules:
        raise ValueError(f"No rules found for rule_type {rule_type} of level {level_difficulty}.")
    
    secret_rule = random.choice(filtered_rules)
    return secret_rule['rule']

def generate_game_master_prompt(secret_rule):
    """
    Generate a system-level prompt for the game master LLM. 
    This defines how the game master should behave.
    """
    prompt = f"""
You are the game master for "Guess the Rule Games." The secret rule is: {secret_rule}

When the player asks if they can bring an item, respond with:

- "Yes, you can bring [guess]." if their guess satisfies the secret rule.
- "No, you cannot bring [guess]." if their guess does not satisfy the secret rule.

If the player asks for more examples, or requests another example, respond by:
- Providing another example that can be brought to the game according to the secret rule.
- Do not repeat any examples you have already provided.

If the player attempts to guess the rule, respond with:
- "Correct! The rule is {secret_rule}." if they guess correctly.
- "Incorrect. Please try again." if they guess incorrectly.

Do not reveal the secret rule unless the player guesses it correctly.
Rule guessing should be evaluated rigidly. Please use your judgment. For example, if the rule guess is phrased differently, only count it as correct if the player's guess is semantically identical or almost fully correct.

Keep your responses concise and do not provide additional hints unless specified.
"""
    return prompt

def game_master_response(platform, model, player_message, conversation, provided_examples):
    """
    Send the player's message to the game master LLM and get the response.
    Update the conversation and track provided examples if applicable.
    """
    # Append the player's message to the conversation
    conversation.append({"role": "user", "content": player_message})

    # Get the game master's response using the modular LLM function
    reply = get_llm_model_response('openai', 'gpt-4o', conversation)

    # Append the game master's reply to the conversation
    conversation.append({"role": "assistant", "content": reply})

    # If the game master provides a new example in response to a request for examples
    if "you can bring" in reply.lower() and ("example" in player_message.lower() or "another example" in player_message.lower()):
        # Extract the item from the reply
        match = re.search(r'you can bring\s+["\']?(.*?)["\']?[.\!]', reply, re.IGNORECASE)
        if match:
            new_example = match.group(1).strip('"\'')
            provided_examples.add(new_example)

    return reply

def generate_examples(platform, model, secret_rule, num_examples=2):
    """
    Generate candidate examples that satisfy the secret rule.
    The LLM is asked to provide items in a comma-separated list without explanation.
    """
    prompt = f"""
You are an assistant helping to generate examples for a game called "Guess the Rule Games."

The secret rule is: {secret_rule}

Your task is to provide {num_examples} examples of items that satisfy the secret rule.

- Only provide the items in a simple, comma-separated list.
- Do not mention the secret rule.
- Do not provide any additional explanation or text.

Format:

[item1], [item2], ..., [item{num_examples}]
"""
    # Initialize the conversation history with a system prompt if needed
    message_history = [{"role": "user", "content": prompt}]
    examples_text = get_llm_model_response(platform, model, message_history)

    # Clean and parse the examples
    examples_text = examples_text.strip().strip('"\'')
    examples = [item.strip() for item in examples_text.split(',') if item.strip()]
    return examples

def validate_examples(platform, model, secret_rule, examples):
    """
    Validate the given examples against the secret rule.
    Returns a list of booleans for each example.
    """
    validation_prompt = f"""
You are a strict validator. The secret rule is: {secret_rule}

Given the following examples:
{', '.join(examples)}

For each example, determine if it strictly satisfies the secret rule.
Respond in JSON with a field "validations" that is a list of booleans in the same order as the given examples.
After the JSON, you may explain your reasoning.

Format exactly:
{{"validations": [true/false, ...]}}

Then explain reasoning after the JSON block.
"""
    message_history = [{"role": "user", "content": validation_prompt}]
    reply = get_llm_model_response(platform, model, message_history)

    # Extract JSON from the reply
    json_match = re.search(r'\{.*?\}', reply, re.DOTALL)
    if not json_match:
        return [False] * len(examples)

    json_str = json_match.group(0)
    try:
        data = json.loads(json_str)
        validations = data.get("validations", [])
        if len(validations) != len(examples):
            return [False] * len(examples)
        return validations
    except json.JSONDecodeError:
        return [False] * len(examples)

def validate_game_master_decision(platform, model, secret_rule, item, gm_response):
    """
    Validate the game master's yes/no decision against the secret rule.
    If GM says "Yes" but item does not fit the rule, or "No" but item does fit, return False.
    Otherwise, return True.
    """
    lowered = gm_response.lower()
    if "yes, you can bring" in lowered:
        # The GM claims the item fits the rule
        validations = validate_examples(platform, model, secret_rule, [item])
        if not validations[0]:
            return False
        return True
    elif "no, you cannot bring" in lowered:
        # The GM claims the item does not fit the rule
        validations = validate_examples(platform, model, secret_rule, [item])
        if validations[0]:
            # Item actually fits the rule, mismatch
            return False
        return True
    else:
        # Not a direct yes/no decision, so no validation needed here.
        return True

def save_log(metrics, rule_type, level_difficulty, platform, model, output_directory):
    """
    Save the game log to a JSON file.
    """
    logs_directory = os.path.join(script_dir, output_directory)
    os.makedirs(logs_directory, exist_ok=True)

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f"log_{platform}_{model}_{rule_type}_{level_difficulty}_{timestamp}.json"
    log_path = os.path.join(logs_directory, log_filename)

    with open(log_path, 'w') as f:
        json.dump(metrics, f, indent=4)

    print(f"Game log and metrics saved to {log_path}")

def automated_player_game(rule_type, level_difficulty, max_turns=20, platform='openai', model='gpt-4o-mini', output_directory='logs/llm_player'):
    """
    Simulates the game with an automated player (LLM) trying to guess the rule.
    Tries up to 5 times to generate valid examples. If after 5 attempts no valid examples
    are found, uses the last generated set anyway. Also validates the game master's decisions,
    correcting any inconsistencies before presenting them to the player.
    
    Parameters:
    - rule_type: str, one of ['attribute_based', 'categorical', 'logical', 'relational', 'semantic']
    - level_difficulty: str, one of ['L1', 'L2', 'L3']
    - max_turns: int, maximum number of turns in the game
    - platform: str, either 'openai' or 'anthropic'
    - model: str, model name (e.g., 'gpt-4o', 'claude-3-haiku')
    - output_directory: str, directory to save the game log
    """
    # Record the start time
    start_time = time.time()
    
    # Initialize the conversation history with the game master's system prompt
    secret_rule = load_secret_rule(rule_type, level_difficulty, os.path.join(script_dir, 'rules', rule_type))
    game_master_prompt = generate_game_master_prompt(secret_rule)
    game_master_conversation = [{"role": "system", "content": game_master_prompt}]
    player_visible_history = []
    
    provided_examples = set()
    
    # Attempt to generate and validate examples up to 5 times
    attempts = 0
    examples = None
    while attempts < 5:
        candidates = generate_examples(platform, model, secret_rule, num_examples=2)
        validations = validate_examples(platform, model, secret_rule, candidates)
        if all(validations):
            examples = candidates
            break
        else:
            examples = candidates
            attempts += 1
    
    # If after 5 attempts we still don't have fully validated examples, use last generated anyway
    if examples is None or not examples:
        examples = ["example_item_1", "example_item_2"]
    
    examples_text = ' and '.join(f'"{item}"' for item in examples)
    initial_message = f"To start, here are some examples of items you can bring: {examples_text}."
    
    # Append the initial message to the game master's conversation and player history
    game_master_conversation.append({"role": "assistant", "content": initial_message})
    player_visible_history.append({"role": "assistant", "content": initial_message})
    
    print("\nGame Master:", initial_message, "\n")
    
    # Initialize logging
    log = []
    
    attempts = 0
    game_over = False
    rule_guessed = False
    failed_attempts = 0  # Counter for failed attempts
    
    # Game loop
    while not game_over and attempts < max_turns:
        # Create a prompt for the player
        conversation_history = "\n".join([
            f"{'Game Master' if msg['role'] == 'assistant' else 'Player'}: {msg['content']}"
            for msg in player_visible_history
        ])
    
        if attempts == max_turns - 1:
            player_prompt = f"""
You are a player in a game called "Guess the Rule Games." This is your final turn, so you must make your best guess about the secret rule.
Based on the game master's responses, try to guess the rule as accurately as possible.

The game master has provided examples: {examples_text}.

Here's the conversation history:
{conversation_history}

Please make your best guess about the rule as this is your last opportunity.
"""
        else:
            player_prompt = f"""
You are a player in a game called "Guess the Rule Games." You are trying to guess the secret rule by asking if certain items can be brought to the game.
The game master has given examples of items that fit the rule: {examples_text}.

Here's the conversation history:
{conversation_history}

Based on this history, either:
1. Make a new guess that hasn't been mentioned before.
2. Ask the game master for more examples if you've been getting a lot of incorrect guesses or are still confused/unsure about the rule.
3. Try to guess the rule if you think you got it.

Be strategic and avoid repeating previous guesses.
"""
    
        # Player (LLM) responds
        try:
            player_message = get_llm_model_response(platform, model, [{"role": "user", "content": player_prompt}]).strip()
        except anthropic.InternalServerError as e:
            # If after 3 retries it still fails, handle the error here without stopping the loop
            print(f"An error occurred with model {model} on platform {platform}: {e}")
            # You can choose to continue to the next iteration or do something else
            player_message = "No valid response due to repeated internal server errors."
    
        # Add player's message to visible history
        player_visible_history.append({"role": "user", "content": player_message})
    
        # Send to game master and get the reply
        reply = game_master_response(platform, model, player_message, game_master_conversation, provided_examples)
    
        # Append game master's reply to player_visible_history as 'assistant' role
        player_visible_history.append({"role": "assistant", "content": reply})
    
        # Now reply is correct and consistent
        print(f"Attempt {attempts + 1}: Player: {player_message}")
        print(f"Game Master: {reply}\n")
    
        # Log the turn
        log_entry = {
            'attempt': attempts + 1,
            'player_message': player_message,
            'game_master_reply': reply,
            'timestamp': datetime.datetime.now().isoformat()
        }
        log.append(log_entry)
    
        # Check for correct guess
        if "Correct! The rule is" in reply:
            print(f"Rule guessed correctly in {attempts + 1} attempts!")
            game_over = True
            rule_guessed = True
        elif attempts + 1 >= max_turns:
            print("Game over: Maximum attempts reached.")
            print(f"The secret rule was: {secret_rule}")
            game_over = True
    
        # Update failed_attempts counter
        if "Incorrect" in reply and "please try again" in reply.lower():
            failed_attempts += 1
        elif "No, you cannot bring" in reply or "Yes, you can bring" in reply:
            failed_attempts += 1
        else:
            # Reset failed_attempts if the reply is something else
            failed_attempts = 0
    
        attempts += 1
    
    # Record the end time
    end_time = time.time()
    duration = round(end_time - start_time, 2)  # Duration in seconds, rounded to 2 decimal places
    
    # Save metrics
    metrics = {
        "rule_type": rule_type,
        "level_difficulty": level_difficulty,
        "secret_rule": secret_rule,
        "max_turns_allowed": max_turns,
        "turns_taken": attempts,
        "rule_guessed": rule_guessed,
        "duration_seconds": duration,  # Added duration metric
        "platform": platform,
        "model": model,
        "conversation": player_visible_history
    }
    log.append({"final_metrics": metrics})
    
    # Save the log
    save_log(metrics, rule_type, level_difficulty, platform, model, output_directory)

if __name__ == "__main__":
    # Example usage:
    # rule_type could be one of: 'attribute_based', 'categorical', 'logical', 'relational', 'semantic'
    # level_difficulty could be one of: 'L1', 'L2', 'L3'

    # rule_type = 'semantic'  # Example rule type
    # level_difficulty = 'L1'        # Example level difficulty
    # max_turns = 10

    # ---

    # llm_models = {
    #     'openai': [
    #         'gpt-4o',
    #         'gpt-4o-mini',
    #     ],
    #     'anthropic': [
    #         'claude-3-haiku-20240307',
    #         'claude-3-5-haiku-latest'
    #     ]
    # }
    
    # llm_models = {
    #     'anthropic': [
    #         'claude-3-haiku-20240307',
    #         'claude-3-5-haiku-latest'
    #     ]
    # }
    llm_models = {
        'anthropic': [
            'claude-3-haiku-20240307'
        ]
    }

    # Define other parameters
    # valid_difficulties = ['L1', 'L2', 'L3']
    valid_difficulties = ['L3']
    valid_rule_types = ['attribute_based', 'categorical', 'logical', 'relational', 'semantic']

    # max_turns_list = [1, 3, 5, 7, 10, 15]
    max_turns_list = [15]
    
    # Define the output directory
    output_dir = 'logs/llm_player'
    
    # Iterate over all combinations of platform, model, level, turns, and rule_type
    for platform, models in llm_models.items():
        for model in models:
            for level_difficulty in valid_difficulties:
                for max_turns in max_turns_list:
                    for rule_type in valid_rule_types:
                        print(f"Starting game with Platform: {platform}, Model: {model}, Rule Type: {rule_type}, Difficulty: {level_difficulty}, Max Turns: {max_turns}")
                        automated_player_game(
                            rule_type=rule_type,
                            level_difficulty=level_difficulty,
                            max_turns=max_turns,
                            platform=platform,
                            model=model,
                            output_directory=output_dir
                        )