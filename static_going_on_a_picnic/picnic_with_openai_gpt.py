import random
import re
import json
import time
import os
import sys
import string

from openai import OpenAI
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Initialize the OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI()

MAX_TURNS = 3

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
L3_individuals = [key[0] for key, count in l1_counts.items() if 3 <= count < 4]

L2_pairs = [pair for pair, count in l2_counts.items() if count > 6]
L3_pairs = [pair for pair, count in l2_counts.items() if 4 <= count < 6]
L3_triplets = [triplet for triplet, count in l3_counts.items() if count > 4]  # Exclude triplets with ≤ 2 examples

# Get difficulty level from the command line
if len(sys.argv) != 2 or sys.argv[1] not in ["L1", "L2", "L3"]:
    print("Usage: python script_name.py <difficulty_level>")
    print("Where <difficulty_level> is one of: L1, L2, L3")
    sys.exit(1)

difficulty = sys.argv[1]

# Function to select a rule based on difficulty
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

# Function to parse the LLM's "more N" request
def parse_more_request(llm_action):
    match = re.search(r"more (\d+)", llm_action)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    return None

# Get the appropriate prompt for the turn
def get_prompt(turns, remaining_count, positives, negatives, examples_exceeded):
    positives_string = ', '.join(positives)
    negatives_string = ', '.join(negatives)

    prompt = f"Turn {turns}\n"

    if examples_exceeded:
        prompt += f"Requested number of examples exceede the maximum available count. Defaulting to maximum available {remaining_count}\n"

    if turns == 1:
        prompt += (
            f"Let's play the game 'going on a picnic'. I will be the host. You will be a competitive player who wants to win the game in as few turns as possible. I will give you some examples in each turn and you have to guess the underlying rule of the game. The rule will be common for all the examples.\n"
            f"There will be a total of {MAX_TURNS}. Your score will be based on the number of turns taken, number of examples seen, and overall time elapsed playing the game. The highest score will be for the fewest turns taken, fewest examples seen, and shortest game played. You will be penalized for each new turn and example.\n"
            f"The rule you will guess should only encompass the positive examples. The negative examples are only for guidance and they do not form the underlying rule itself.\n"
            f"To play the game you can only do one of the following actions in a turn:\n"
            f"1. type 'more N' to request N more examples for that rule (up to {remaining_count} available).\n"
            f"2. type the rule if you think you've guessed it.\n"
            f"3. type 'give up' if you want to end the game and see the rule.\n\n"
            f"I can bring: {positives_string}\n"
            f"I cannot bring: {negatives_string}\n\n"
            f"What would you like to do?"
        )
    elif remaining_count > 0:
        if turns == MAX_TURNS:
            prompt += (
                f"I can bring: {positives_string}\n"
                f"I cannot bring: {negatives_string}\n\n"
                f"This is the final turn. Please provide your answer."
            )
        else:
            prompt += (
                f"I can bring: {positives_string}\n"
                f"I cannot bring: {negatives_string}\n\n"
                f"1. type 'more N' to request N more examples for the rule (up to {remaining_count} available).\n"
                f"2. type the rule if you think you've guessed it.\n"
                f"3. type 'give up' if you want to end the game and see the rule.\n\n"
                f"What would you like to do?"
            )
    else:
        prompt += (
            f"No more examples available.\n"
            f"Please provide your final answer."
        )
    return prompt

# Main function to run the game
def play_game_with_gpt():
    start_time = time.time()
    rule = pick_rule(difficulty)
    print(f"Starting the game with GPT-4o on difficulty {difficulty}. Rule: {rule['rule']}")

    history = {"positives": set(), "negatives": set()}
    message_history = [
        {"role": "system", "content": "You are playing a game called 'Going on a Picnic'. Your goal is to guess the rule behind a set of examples. You can request more examples or make a guess."}
    ]
    turns = 0
    llm_won = False
    total_examples_shown = 0

    # Initial examples to show
    num_examples = 2

    while turns < MAX_TURNS:
        turns += 1
        # Calculate available examples for the turn
        rule_tags = rule["categories"] if "categories" in rule else [rule["category"]]
        available_positives = [
            item for item, tags in items.items() if all(tag in tags for tag in rule_tags) and item not in history["positives"]
        ]
        available_negatives = [
            item for item, tags in items.items() if not all(tag in tags for tag in rule_tags) and item not in history["negatives"]
        ]
        available_count = min(len(available_positives), len(available_negatives))

        # Check if the requested number of examples exceeds available examples
        examples_exceeded = False
        if num_examples > available_count:
            print(f"Only {available_count} examples are available.")
            examples_exceeded = True
            num_examples = available_count

        # Generate positive and negative examples
        positives, negatives = generate_examples(rule, history, num_examples)

        # Add to history and update the total count of examples shown
        history["positives"].update(positives)
        history["negatives"].update(negatives)
        total_examples_shown += len(positives)

        # Correct calculation of remaining examples
        remaining_count = available_count - num_examples
        prompt = get_prompt(turns, remaining_count, positives, negatives, examples_exceeded)

        print(f"\n\n*** Prompt for turn {turns} ***\n{prompt}\n\n")

        message_history.append({"role": "user", "content": prompt})

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=message_history
            )
            llm_action = response.choices[0].message.content.strip().lower()
            print(f"GPT-4o action: {llm_action}")

            # Record the LLM's action in the message history
            message_history.append({"role": "assistant", "content": llm_action})

            if "more" in llm_action:
                parsed_num = parse_more_request(llm_action)
                if parsed_num:
                    num_examples = parsed_num
                else:
                    print("Invalid 'more' request format. Defaulting to 2 examples.")
                    num_examples = 2

            elif llm_action == "give up":
                print(f"The rule was: {rule['rule']}")
                break

            else:
                if check_guess(llm_action, rule["rule"]):
                    print("GPT-4o guessed correctly!")
                    llm_won = True
                    break
                else:
                    print("GPT-4o's guess was incorrect.")
                    if remaining_count == 0:
                        print("No more examples available. Game over!")
                        break
        except Exception as e:
            print(f"Error during LLM interaction: {e}")
            break

    end_time = time.time()
    duration = end_time - start_time

    print("\n***Game Summary***")
    print(f"Difficulty: {difficulty}")
    print(f"Rule: {rule['rule']}")
    print(f"Turns taken: {turns}")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Total examples shown: {total_examples_shown}")
    print(f"Result: {'GPT-4o won' if llm_won else 'GPT-4o lost'}")

# Start the game
play_game_with_gpt()
