# dynamic_game_sim.py

import os
import json
import random
import datetime
import re
from openai import OpenAI

# --------------------------
# Configuration & Setup
# --------------------------

# Get the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Load the API key from 'keys.json'
keys_path = os.path.join(script_dir, 'keys.json')
with open(keys_path, 'r') as f:
    keys = json.load(f)
OPENAI_KEY = keys['OPENAI_API_KEY']
client = OpenAI(api_key=OPENAI_KEY)

# --------------------------
# Helper Functions
# --------------------------

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
        raise ValueError(f"No rules found for rule_type '{rule_type}' with level '{level_difficulty}'.")
    
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

def game_master_response(player_message, conversation, provided_examples):
    """
    Send the player's message to the game master LLM and get the response.
    Update the conversation and track provided examples if applicable.
    """
    current_conversation = conversation.copy()
    current_conversation.append({"role": "user", "content": player_message})

    response = client.chat.completions.create(
        model="gpt-4o",  # Use the appropriate model name
        messages=current_conversation,
        temperature=0
    )
    reply = response.choices[0].message.content.strip()

    conversation.append({"role": "user", "content": player_message})
    conversation.append({"role": "assistant", "content": reply})

    # If the game master provides a new example in response to a request for examples
    if "you can bring" in reply.lower() and ("example" in player_message.lower() or "another example" in player_message.lower()):
        # Extract the item from the reply
        match = re.search(r'you can bring\s+(.*?)[\.\!]', reply, re.IGNORECASE)
        if match:
            new_example = match.group(1).strip('"\'')
            provided_examples.add(new_example)

    return reply

def generate_examples(secret_rule, num_examples=2):
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
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    examples_text = response.choices[0].message.content.strip().strip('"\'')
    examples = [item.strip() for item in examples_text.split(',') if item.strip()]
    return examples

def validate_examples(secret_rule, examples):
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
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": validation_prompt}],
        temperature=0
    )
    reply = response.choices[0].message.content.strip()

    # Extract JSON from the reply
    json_match = re.search(r'\{.*?\}', reply, re.DOTALL)
    if not json_match:
        return [False]*len(examples)

    json_str = json_match.group(0)
    try:
        data = json.loads(json_str)
        validations = data.get("validations", [])
        if len(validations) != len(examples):
            return [False]*len(examples)
        return validations
    except json.JSONDecodeError:
        return [False]*len(examples)

def validate_game_master_decision(secret_rule, item, gm_response):
    """
    Validate the game master's yes/no decision against the secret rule.
    If GM says "Yes" but item does not fit the rule, or "No" but item does fit, return False.
    Otherwise, return True.
    """
    lowered = gm_response.lower()
    if "yes, you can bring" in lowered:
        # The GM claims the item fits the rule
        validations = validate_examples(secret_rule, [item])
        if not validations[0]:
            return False
        return True
    elif "no, you cannot bring" in lowered:
        # The GM claims the item does not fit the rule
        validations = validate_examples(secret_rule, [item])
        if validations[0]:
            # Item actually fits the rule, mismatch
            return False
        return True
    else:
        # Not a direct yes/no decision, so no validation needed here.
        return True

def save_log(log, rule_type, level_difficulty):
    """
    Save the game log to a JSON file.
    """
    logs_directory = os.path.join(script_dir, 'logs')
    os.makedirs(logs_directory, exist_ok=True)

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f"log_{rule_type}_{level_difficulty}_{timestamp}.json"
    log_path = os.path.join(logs_directory, log_filename)

    with open(log_path, 'w') as f:
        json.dump(log, f, indent=4)

    print(f"Game log saved to {log_path}")

def automated_player_game(rule_type, level_difficulty, max_turns=20, output_directory=None):
    """
    Simulates the game with an automated player (LLM) trying to guess the rule.
    Tries up to 5 times to generate valid examples. If after 5 attempts no valid examples
    are found, uses the last generated set anyway. Also validates the game master's decisions,
    correcting any inconsistencies before presenting them to the player.
    
    Parameters:
    - rule_type: str, one of ['attribute_based', 'categorical', 'logical', 'relational', 'semantic']
    - level_difficulty: str, one of ['L1', 'L2', 'L3']
    - max_turns: int, maximum number of turns in the game
    - output_directory: str, directory to save the game log
    """
    import datetime  # Ensure datetime is imported
    
    # Record the start time
    start_time = datetime.datetime.now()
    
    try:
        # Load the secret rule for the game
        rules_directory = os.path.join(script_dir, 'rules', rule_type)
        secret_rule = load_secret_rule(rule_type, level_difficulty, rules_directory)

        # Generate the game master's initial prompt
        game_master_prompt = generate_game_master_prompt(secret_rule)
        game_master_conversation = [{"role": "system", "content": game_master_prompt}]
        player_visible_history = []

        provided_examples = set()

        # Attempt to generate and validate examples up to 5 times
        attempts = 0
        examples = None
        while attempts < 5:
            candidates = generate_examples(secret_rule, num_examples=2)
            validations = validate_examples(secret_rule, candidates)
            if all(validations):
                examples = candidates
                break
            else:
                examples = candidates
                attempts += 1

        # If after 5 attempts we still don't have fully validated examples, use last generated anyway
        if examples is None:
            examples = ["example_item_1", "example_item_2"]

        examples_text = ' and '.join(f'"{item}"' for item in examples)
        initial_message = f"To start, here are some examples of items you can bring: {examples_text}."

        game_master_conversation.append({"role": "assistant", "content": initial_message})
        player_visible_history.append({"role": "assistant", "content": initial_message})

        print("\nGame Master:", initial_message, "\n")

        # Initialize the automated player (LLM)
        player = OpenAI(api_key=OPENAI_KEY)

        attempts = 0
        game_over = False
        rule_guessed = False
        log = []
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
            response = player.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": player_prompt}],
                temperature=0.7
            )
            player_message = response.choices[0].message.content.strip()

            # Add player's message to visible history
            player_visible_history.append({"role": "user", "content": player_message})

            # Send to game master
            reply = game_master_response(player_message, game_master_conversation, provided_examples)

            # Append game master's reply to player_visible_history as 'assistant' role
            player_visible_history.append({"role": "assistant", "content": reply})

            # Validate the game master's yes/no decision if applicable
            yes_no_pattern = r"(Yes, you can bring|No, you cannot bring)\s+(.*?)[\.\!]"
            match = re.search(yes_no_pattern, reply, re.IGNORECASE)
            if match:
                decision_phrase = match.group(1).lower()
                item_guess = match.group(2).strip('"\'')
                is_valid_decision = validate_game_master_decision(secret_rule, item_guess, reply)
                if not is_valid_decision:
                    # Correct the decision
                    validations = validate_examples(secret_rule, [item_guess])
                    correct_fits_rule = validations[0]

                    if "yes, you can bring" in decision_phrase:
                        # GM said yes but should say no
                        corrected_reply = f"No, you cannot bring {item_guess}."
                    else:
                        # GM said no but should say yes
                        corrected_reply = f"Yes, you can bring {item_guess}."

                    # Correct the conversation entries
                    # The last two appended to game_master_conversation are the user's message and GM's faulty reply.
                    # We just replace the GM reply in the conversation:
                    game_master_conversation[-1]["content"] = corrected_reply

                    # Also replace the last message in player_visible_history:
                    player_visible_history[-1]["content"] = corrected_reply

                    # Update reply variable so the code below uses the corrected version
                    reply = corrected_reply

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

    finally:
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        metrics = {
            "rule_type": rule_type,
            "level_difficulty": level_difficulty,
            "secret_rule": secret_rule,
            "max_turns_allowed": max_turns,
            "turns_taken": attempts,
            "rule_guessed": rule_guessed,
            "duration (s)": duration,  
            "conversation": player_visible_history
        }
        log.append({"final_metrics": metrics})

        if output_directory is None:
            output_directory = os.path.join(script_dir, 'logs')
        os.makedirs(output_directory, exist_ok=True)

        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = f"game_log_{rule_type}_{level_difficulty}_{timestamp}.json"
        log_path = os.path.join(output_directory, log_filename)

        with open(log_path, 'w') as f:
            json.dump(metrics, f, indent=4)

        print(f"Game log and metrics saved to {log_path}")

if __name__ == "__main__":
    # Example usage:
    # rule_type could be one of: 'attribute_based', 'categorical', 'logical', 'relational', 'semantic'
    # level_difficulty could be one of: 'L1', 'L2', 'L3'

    rule_type = 'semantic'  # Example rule type
    level_difficulty = 'L1'        # Example level difficulty
    max_turns = 10
    log_dir = os.path.join(script_dir, 'logs', 'llm_player')

    automated_player_game(rule_type, level_difficulty, max_turns, log_dir)