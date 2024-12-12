import random
import string
import os
from openai import OpenAI
from dotenv import load_dotenv
import json
from collections import defaultdict

# Load the .env file
load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI()

# Register attributes here
attributes = {
    "color": ["red", "blue", "green", "yellow", "black", "white", "pink", "purple", "orange"],
    "size": ["small", "medium", "large", "tiny", "huge"],
    "shape": ["circle", "square", "triangle", "rectangle", "oval"],
    'kind': ["kitchen item", "animal", "fruit", "vehicle", "furniture"]
}

# Load items
with open('items.json', 'r') as file:
    items = json.load(file)

# Function to select difficulty level
def choose_difficulty():
    while True:
        difficulty = input("Choose a difficulty level: L1 (easy), L2 (medium), L3 (hard): ").strip().upper()
        if difficulty in ["L1", "L2", "L3"]:
            return difficulty
        else:
            print("Invalid choice. Please choose L1, L2, or L3.")

# Function to ask if user wants hints
def ask_for_hints():
    while True:
        hint_preference = input("Would you like hints during the game? (yes/no): ").strip().lower()
        if hint_preference in ["yes", "no"]:
            return hint_preference == "yes"
        else:
            print("Please answer 'yes' or 'no'.")

# Function to dynamically select a rule based on difficulty
def pick_rule(difficulty):
    if difficulty == "L1":
        category = random.choice(attributes['kind'])
        return {"type": "category", "rule": f"Items from the category '{category}'", "category": category}

    elif difficulty == "L2":
        attribute_type = random.choice(["color", "size", "shape"])
        attribute_value = random.choice(attributes[attribute_type])
        return {"type": "attribute", "rule": f"Items with {attribute_type} '{attribute_value}'", "attribute_type": attribute_type, "attribute_value": attribute_value}

    elif difficulty == "L3":
        # Aggregates for each rule type with sufficient items
        color_size_rules = defaultdict(list)
        color_shape_rules = defaultdict(list)
        shape_size_rules = defaultdict(list)

        # Iterate over items to group them by potential rule combinations
        for item, item_attributes in items.items():
            color = next((attr for attr in item_attributes if attr in attributes["color"]), None)
            size = next((attr for attr in item_attributes if attr in attributes["size"]), None)
            shape = next((attr for attr in item_attributes if attr in attributes["shape"]), None)

            # Collect rules for each combination type if all necessary attributes are present
            if color and size:
                color_size_rules[(color, size)].append(item)
            if color and shape:
                color_shape_rules[(color, shape)].append(item)
            if shape and size:
                shape_size_rules[(shape, size)].append(item)

        # Filter rules with at least two examples per rule to ensure gameplay
        valid_rules = []
        for (color, size), examples in color_size_rules.items():
            if len(examples) >= 4:
                valid_rules.append({
                    "type": "color_size",
                    "rule": f"Items that are {color} and {size}",
                    "color": color,
                    "size": size
                })
        for (color, shape), examples in color_shape_rules.items():
            if len(examples) >= 4:
                valid_rules.append({
                    "type": "color_shape",
                    "rule": f"Items that are {color} and {shape}",
                    "color": color,
                    "shape": shape
                })
        for (shape, size), examples in shape_size_rules.items():
            if len(examples) >= 4:
                valid_rules.append({
                    "type": "shape_size",
                    "rule": f"Items that are {shape} and {size}",
                    "shape": shape,
                    "size": size
                })

        # Randomly select a valid rule to start the game, or return None if no rules are valid
        return random.choice(valid_rules) if valid_rules else None


# Improved generate_examples with debugging
def generate_examples(rule, history):
    rule_tags = []
    all_rule_type = rule["type"].split("_")
    # print(f"--DEBUG-- {rule}, {all_rule_type}")
    for r in all_rule_type:
        if r == 'attribute':
            rule_tags.append(rule['attribute_value'])
        else:
            rule_tags.append(rule[r])

    # Debug statement to check the tags being used
    # print(f"Generating examples with rule tags: {rule_tags}, rule {rule}")

    # Filter for items matching all rule tags
    available_positives = [item for item, tags in items.items() if all(tag in tags for tag in rule_tags) and item not in history["positives"]]
    available_negatives = [item for item, tags in items.items() if not all(tag in tags for tag in rule_tags) and item not in history["negatives"]]

    # Debug statements to see available items
    # print(f"Available positives: {available_positives}")
    # print(f"Available negatives: {available_negatives}")

    if len(available_positives) < 2 or len(available_negatives) < 2:
        print("Insufficient examples for this rule.")
        return [], []

    positives = random.sample(available_positives, 2)
    negatives = random.sample(available_negatives, 2)

    return positives, negatives

# Function to canonicalize strings for flexible comparison (removing punctuation, case-sensitivity)
def canonicalize_string(s):
    return ''.join(c.lower() for c in s if c not in string.punctuation).strip()

def check_guess(user_guess, actual_rule):
    """
    Use OpenAI's LLM to check if the user's guess is semantically correct.
    :param user_guess: The user's guess input.
    :param actual_rule: The correct rule.
    :return: Boolean indicating whether the guess is correct.
    """
    # print(f'--DEBUG-- rule {actual_rule}, user {user_guess}')
    prompt = f"Determine if the following user guess is semantically equivalent to the actual rule:\n" \
             f"User Guess: {user_guess}\n" \
             f"Actual Rule: {actual_rule}\n" \
             f"Respond with 'yes' if they are equivalent, otherwise respond with 'no'."

    try:
        # Call the updated OpenAI API to check the user's guess
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a semantic evaluator for a guess-the-rule game called 'going on a picnic'"},
                {"role": "user", "content": prompt}
            ],
        )
        # Extract the result from the response
        answer = response.choices[0].message.content.strip().lower()

        # Return True if the model responded with 'yes', else False
        return answer == "yes"

    except Exception as e:
        print(f"Error while calling OpenAI API - falling back on string check. Error: {e}")
        return canonicalize_string(user_guess) == canonicalize_string(actual_rule)

# Main function to simulate the game
def play_game():
    print("Welcome to 'Going on a Picnic'!")
    
    # Choose the difficulty level
    difficulty = choose_difficulty()
    
    # Ask if the user wants hints
    # hints_enabled = ask_for_hints()

    # Pick a random rule that will be consistent throughout the game
    rule = pick_rule(difficulty)
    
    # History to track presented examples (positives and negatives)
    history = {"positives": set(), "negatives": set()}
    
    # Calculate the maximum turns based on available examples
    max_turns = 10  # You can adjust this based on game length preference

    turn = 1
    while turn <= max_turns:
        print(f"\nTurn {turn}")
        
        # Generate positive and negative examples based on tags and the rule
        positives, negatives = generate_examples(rule, history)

        # Add the generated examples to the history
        history["positives"].update(positives)
        history["negatives"].update(negatives)
        
        # Show examples to the user in natural language
        print(f"I'm going on a picnic. I can bring {positives[0]} and {positives[1]}.")
        print(f"I cannot bring {negatives[0]} or {negatives[1]}.")

        # # Provide a hint if the user opted for it
        # if hints_enabled:
        #     if rule["type"] == "attribute":
        #         print(f"\nHint: The answer is something like 'Items with {rule['attribute_type']} X'.")

        # User guesses the rule
        user_input = input("\nWhat's the rule? \nType 'more' for more examples \nType 'give up' to end the game and see the rule: ").strip().lower()
        
        if user_input == "more":
            turn += 1
            continue
        elif user_input == "give up":
            print(f'The rule was: {rule['rule']}')
            return
        
        # Check the user's guess with the actual rule using OpenAI's LLM
        if check_guess(user_input, rule["rule"]):
            print(f"Correct! The rule was: {rule['rule']}")
            return
        else:
            print("Incorrect guess, try again!")
            turn += 1

    # No more examples, ask for the final guess
    final_guess = input("\nNo more examples available. Please provide your final guess: ").strip().lower()
    
    # Check the final guess
    if check_guess(final_guess, rule["rule"]):
        print(f"Correct! The rule was: {rule['rule']}")
    else:
        print(f"Sorry, the correct rule was: {rule['rule']}")


# Start the game
play_game()
