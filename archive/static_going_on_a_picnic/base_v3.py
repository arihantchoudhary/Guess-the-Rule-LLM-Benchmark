import random
import json
import string
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI()

# Load items and counts data
with open('open_images_combined_items.json', 'r') as file:
    items = json.load(file)

# Load individual, pair, and triplet counts from JSON files
with open('pp_individual_counts.json', 'r') as file:
    l1_counts = json.load(file)
    l1_counts = {tuple(eval(key)): value for key, value in l1_counts.items()}

with open('pp_pairs_counts.json', 'r') as file:
    l2_counts = json.load(file)
    l2_counts = {tuple(eval(key)): value for key, value in l2_counts.items()}

with open('pp_triplets_counts.json', 'r') as file:
    l3_counts = json.load(file)
    l3_counts = {tuple(eval(key)): value for key, value in l3_counts.items()}

# Categorize individuals, pairs, and triplets based on count thresholds
L1_individuals = [key[0] for key, count in l1_counts.items() if count > 6]
L2_individuals = [key[0] for key, count in l1_counts.items() if 4 <= count <= 6]
L3_individuals = [key[0] for key, count in l1_counts.items() if 2 <= count < 4]

L2_pairs = [pair for pair, count in l2_counts.items() if count > 6]
L3_pairs = [pair for pair, count in l2_counts.items() if 2 <= count < 6]
L3_triplets = [triplet for triplet, count in l3_counts.items() if count > 2]  # Exclude triplets with ≤ 2 examples

# Function to select difficulty level
def choose_difficulty():
    while True:
        difficulty = input("Choose a difficulty level: L1 (easy), L2 (medium), L3 (hard): ").strip().upper()
        if difficulty in ["L1", "L2", "L3"]:
            return difficulty
        else:
            print("Invalid choice. Please choose L1, L2, or L3.")

# Function to ask for the number of examples per turn
def get_example_count(available_count):
    while True:
        try:
            count = int(input(f"How many examples would you like to see this turn? (Max {available_count} available): "))
            if 0 < count <= available_count:
                return count
            else:
                print(f"Please enter a number between 1 and {available_count}.")
        except ValueError:
            print("Invalid input. Please enter a positive integer.")

# Function to dynamically select a rule based on difficulty
def pick_rule(difficulty):
    if difficulty == "L1":
        category = random.choice(L1_individuals)
        return {"type": "category", "rule": f"Items from the category '{category}'", "category": category}

    elif difficulty == "L2":
        if random.choice(["individual", "pair"]) == "individual":
            category = random.choice(L2_individuals)
            return {"type": "category", "rule": f"Items from the category '{category}'", "category": category}
        else:
            pair = random.choice(L2_pairs)
            return {"type": "pair", "rule": f"Items from the categories '{pair[0]}' and '{pair[1]}'", "categories": pair}

    elif difficulty == "L3":
        rule_type = random.choice(["individual", "pair", "triplet"])
        if rule_type == "individual":
            category = random.choice(L3_individuals)
            return {"type": "category", "rule": f"Items from the category '{category}'", "category": category}
        elif rule_type == "pair":
            pair = random.choice(L3_pairs)
            return {"type": "pair", "rule": f"Items from the categories '{pair[0]}' and '{pair[1]}'", "categories": pair}
        else:
            triplet = random.choice(L3_triplets)
            return {
                "type": "triplet",
                "rule": f"Items from the categories '{triplet[0]}', '{triplet[1]}', and '{triplet[2]}'",
                "categories": triplet
            }

# Function to generate examples based on rule and requested count
def generate_examples(rule, history, count):
    rule_tags = rule["categories"] if "categories" in rule else [rule["category"]]

    available_positives = [
        item for item, tags in items.items() if all(tag in tags for tag in rule_tags) and item not in history["positives"]
    ]
    available_negatives = [
        item for item, tags in items.items() if not all(tag in tags for tag in rule_tags) and item not in history["negatives"]
    ]

    pos_count = min(count, len(available_positives))
    neg_count = min(count, len(available_negatives))

    positives = random.sample(available_positives, pos_count) if pos_count else available_positives
    negatives = random.sample(available_negatives, neg_count) if neg_count else available_negatives

    return positives, negatives

# Function to canonicalize strings for flexible comparison (removing punctuation, case-sensitivity)
def canonicalize_string(s):
    return ''.join(c.lower() for c in s if c not in string.punctuation).strip()

def check_guess(user_guess, actual_rule):
    # Enhanced prompt to consider synonyms and semantic similarity
    prompt = (
        f"Determine if the following user guess is semantically equivalent or reasonably close in meaning to the actual rule.\n"
        f"Consider synonyms, related terms, and general concepts.\n\n"
        f"User Guess: \"{user_guess}\"\n"
        f"Actual Rule: \"{actual_rule}\"\n\n"
        f"Respond with 'yes' if they are equivalent or similar, otherwise respond with 'no'."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert at identifying semantic equivalency in a game called 'Going on a Picnic'."},
                {"role": "user", "content": prompt}
            ],
        )
        answer = response.choices[0].message.content.strip().lower()
        return answer == "yes"
    except Exception as e:
        print(f"Error while calling OpenAI API - falling back on string check. Error: {e}")
        return canonicalize_string(user_guess) == canonicalize_string(actual_rule)

# Main function to play the game
def play_game():
    print("Welcome to 'Going on a Picnic'!")
    difficulty = choose_difficulty()
    rule = pick_rule(difficulty)
    # print(f"--DEBUG-- {rule}") 

    history = {"positives": set(), "negatives": set()}
    max_turns = 10
    turn = 1
    while turn <= max_turns:
        print(f"\nTurn {turn}")

        # Calculate available examples for the turn
        rule_tags = rule["categories"] if "categories" in rule else [rule["category"]]
        available_positives = [
            item for item, tags in items.items() if all(tag in tags for tag in rule_tags) and item not in history["positives"]
        ]
        available_negatives = [
            item for item, tags in items.items() if not all(tag in tags for tag in rule_tags) and item not in history["negatives"]
        ]
        available_count = min(len(available_positives), len(available_negatives))
        
        if available_count == 0:
            print("No more examples available. Please provide your final guess.")
            break

        # Prompt user for valid example count for this turn
        example_count = get_example_count(available_count)

        # Generate positive and negative examples
        positives, negatives = generate_examples(rule, history, example_count)
        
        history["positives"].update(positives)
        history["negatives"].update(negatives)
        
        print(f"I'm going on a picnic. I can bring {', '.join(positives)}.")
        print(f"I cannot bring {', '.join(negatives)}.")

        user_input = input("\nWhat's the rule? \nType 'more' for more examples \nType 'give up' to end the game and see the rule: ").strip().lower()
        
        if user_input == "more":
            turn += 1
            continue
        elif user_input == "give up":
            print(f"The rule was: {rule['rule']}")
            return

        if check_guess(user_input, rule["rule"]):
            print(f"Correct! The rule was: {rule['rule']}")
            return
        else:
            print("Incorrect guess, try again!")
            turn += 1

    final_guess = input("\nNo more examples available. Please provide your final guess: ").strip().lower()
    if check_guess(final_guess, rule["rule"]):
        print(f"Correct! The rule was: {rule['rule']}")
    else:
        print(f"Sorry, the correct rule was: {rule['rule']}")

# Start the game
play_game()
