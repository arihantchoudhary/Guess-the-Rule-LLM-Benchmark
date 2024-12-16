import random
import re
import json
import time
import os
import string
from datetime import datetime
import anthropic
import google.generativeai
import asyncio

from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Initialize the OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = AsyncOpenAI()

# Initialize the Anthropic client
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Configure the Google PaLM API key
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
google.generativeai.configure(api_key=GOOGLE_API_KEY)

# Get the directory of the current file (base.py)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Load items and counts data
with open(os.path.join(current_dir, 'data', 'open_images_combined_items.json'), 'r') as file:
    items = json.load(file)

# Load individual, pair, and triplet counts from JSON files
with open(os.path.join(current_dir, 'data', 'pp_individual_counts.json'), 'r') as file:
    l1_counts = json.load(file)
    l1_counts = {tuple(eval(key)): value for key, value in l1_counts.items()}

with open(os.path.join(current_dir, 'data', 'pp_pairs_counts.json'), 'r') as file:
    l2_counts = json.load(file)
    l2_counts = {tuple(eval(key)): value for key, value in l2_counts.items()}

with open(os.path.join(current_dir, 'data', 'pp_triplets_counts.json'), 'r') as file:
    l3_counts = json.load(file)
    l3_counts = {tuple(eval(key)): value for key, value in l3_counts.items()}

# Categorize individuals, pairs, and triplets based on count thresholds
L1_individuals = [key[0] for key, count in l1_counts.items() if count > 6]
L2_individuals = [key[0] for key, count in l1_counts.items() if 4 <= count <= 6]
L3_individuals = [key[0] for key, count in l1_counts.items() if 3 <= count < 4]

L2_pairs = [pair for pair, count in l2_counts.items() if count > 6]
L3_pairs = [pair for pair, count in l2_counts.items() if 4 <= count < 6]
L3_triplets = [triplet for triplet, count in l3_counts.items() if count > 4]  # Exclude triplets with ≤ 2 examples

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

async def check_guess(user_guess, actual_rule, positive_examples):
    judge_model = "gpt-4o-mini"
    # Enhanced prompt to consider synonyms and semantic similarity
    prompt = (
        f"Determine if the following user guess is semantically equivalent or reasonably close in meaning to the actual rule.\n"
        f"Consider synonyms, related terms, and general concepts.\n\n"
        f"The user was also provided some examples. If the user's answer is correct according to the examples but deviates from the rule a little bit (only a little), it can still be marked as correct.\n"
        f"User Guess: \"{user_guess}\"\n"
        f"Actual Rule: \"{actual_rule}\"\n"
        f"Examples Shown: {positive_examples}\n\n"
        f"Respond with 'yes' if they are equivalent or similar, otherwise respond with 'no'."
    )

    print(f"\n*** Prompt for JUDGE ***\n{prompt}\n\n")
    try:
        response = await openai_client.chat.completions.create(
            model=judge_model,
            messages=[
                {"role": "system", "content": "You are an expert at identifying semantic equivalency in a game called 'Going on a Picnic'."},
                {"role": "user", "content": prompt}
            ],
        )
        answer = response.choices[0].message.content.strip().lower()
        print(f"Judge model {judge_model} response: {answer}")
        return answer == "yes"
    except Exception as e:
        print(f"Error while calling OpenAI API - falling back on string check. Error: {e}")
        return canonicalize_string(user_guess) == canonicalize_string(actual_rule)

# Function to parse the LLM's "more N" / "N more" request
def parse_more_request(llm_action):
    matches = list(re.finditer(r"(?:more\s+(\d+))|(?:(\d+)\s+more)", llm_action, re.IGNORECASE))
    if matches:
        last_match = matches[-1]
        num_str = last_match.group(1) or last_match.group(2)
        try:
            return int(num_str)
        except (ValueError, TypeError):
            return None
    return None

# Get the appropriate prompt for the turn
def get_prompt(turns, remaining_count, positives, negatives, examples_exceeded, max_turns):
    positives_string = ', '.join(positives)
    negatives_string = ', '.join(negatives)

    prompt = f"Turn {turns}\n"

    if examples_exceeded:
        prompt += f"Requested number of examples exceeds the maximum available count. Defaulting to maximum available {remaining_count}\n"

    if turns == 1:
        if max_turns == 1:
            prompt += (
                f"Let's play the game 'going on a picnic'. I will be the host. You will be a competitive player who wants to win the game. I will give you some examples and you have to guess the underlying rule of the game. The rule will be common for all the examples.\n"
                f"There will be only 1 turn and no more.\n"
                f"The rule you will guess should only encompass the positive examples. The negative examples are only for guidance and they do not form the underlying rule itself.\n"
                f"To play the game you can only do one of the following actions:\n"
                f"1. type the rule if you think you've guessed it. The format must be 'Items from the category/categories <category>'. Do not repeat chat history or irrelevant text when presenting your answer rule.\n"
                f"2. type 'give up' if you want to give up and see the rule.\n\n"
                f"I can bring: {positives_string}\n"
                f"I cannot bring: {negatives_string}\n\n"
                f"What would you like to do?"
            )
        else:
            prompt += (
                f"Let's play the game 'going on a picnic'. I will be the host. You will be a competitive player who wants to win the game in as few turns as possible. I will give you some examples in each turn and you have to guess the underlying rule of the game. The rule will be common for all the examples.\n"
                f"There will be a total of {max_turns} turns. Your score will be based on the number of turns taken, number of examples seen, and overall time elapsed playing the game. The highest score will be for the fewest turns taken, fewest examples seen, and shortest game played. You will be penalized for each new turn and example.\n"
                f"The rule you will guess should only encompass the positive examples. The negative examples are only for guidance and they do not form the underlying rule itself.\n"
                f"To play the game you can only do one of the following actions in a turn:\n"
                f"1. type 'more N' to request N more examples for that rule (up to {remaining_count} available).\n"
                f"2. type the rule if you think you've guessed it. The format must be 'Items from the category/categories <category>'. Do not repeat chat history or irrelevant text when presenting your answer rule.\n"
                f"3. type 'give up' if you want to end the game and see the rule.\n\n"
                f"I can bring: {positives_string}\n"
                f"I cannot bring: {negatives_string}\n\n"
                f"What would you like to do?"
            )
    else:
        prompt += (
            f"I can bring: {positives_string}\n"
            f"I cannot bring: {negatives_string}\n\n"
        )
        if remaining_count > 0:
            if turns == max_turns:
                prompt += (
                    f"This is the final turn. Please provide your answer."
                )
            else:
                prompt += (
                    f"1. type 'more N' to request N more examples for the rule (up to {remaining_count} available).\n"
                    f"2. type the rule if you think you've guessed it. The format must be 'Items from the category/categories <category>'. Do not repeat chat history or irrelevant text when presenting your answer rule.\n"
                    f"3. type 'give up' if you want to end the game and see the rule.\n\n"
                    f"What would you like to do?"
                )
        else:
            prompt += (
                f"No more examples available.\n"
                f"Please provide your final answer."
            )
    return prompt

# Function to get LLM model response
async def get_llm_model_response(model, message_history):
    if model in ['gpt-4o', 'gpt-4o-mini']:
        response = await openai_client.chat.completions.create(
            model=model,
            messages=message_history
        )
        return response.choices[0].message.content.strip().lower()
    else:
        system_prompt = ''
        user_prompts = []
        for m in message_history:
            if not system_prompt and m['role'] == 'system':
                system_prompt += m['content']
            elif m['role'] == 'user':
                user_prompts.append(m)

        response = await anthropic_client.messages.create(
            max_tokens=1024,
            system=system_prompt,
            messages=user_prompts,
            model=model,
        )
        return response.content[0].text.strip().lower()
    # elif 'idk':
    #     # change the format of message history for google's model
    #     google_messages_history = []
    #     for m in range(len(message_history) - 1):
    #         curr_message = message_history[m]
    #         if curr_message['role'] == 'system':
    #             google_messages_history.append({'role': 'model', 'parts': curr_message['content']})
    #         elif curr_message['role'] == 'user':
    #             google_messages_history.append({'role': 'user', 'parts': curr_message['content']})

    #     gen_model = google.generativeai.GenerativeModel(model)
    #     chat = gen_model.start_chat(
    #         history=google_messages_history
    #     )
    #     response = chat.send_message(message_history[-1]['content'])
    #     return response.text
    # else:
    #     assert False, f'Unknown platform {platform} given'

# Main function to run the game
async def play_game_with_llms(difficulty, max_turns, model, num_init_examples):
    rule = pick_rule(difficulty)
    print(f"------------ Starting the game with {model} on difficulty {difficulty} with max turns {max_turns}. Rule: {rule['rule']} ------------")

    history = {"positives": set(), "negatives": set()}
    message_history = [
        {"role": "system", "content": "You are playing a game called 'Going on a Picnic'. Your goal is to guess the rule behind a set of examples. You can request more examples or make a guess."}
    ]
    turns = 0
    total_pos_examples_shown = 0
    total_neg_examples_shown = 0
    message_id = 0  # Initialize message ID counter

    # Initial examples to show
    num_examples = num_init_examples

    while turns < max_turns:
        await asyncio.sleep(1)
        turns += 1

        # Calculate available examples
        rule_tags = rule["categories"] if "categories" in rule else [rule["category"]]
        available_positives = [
            item for item, tags in items.items() if all(tag in tags for tag in rule_tags) and item not in history["positives"]
        ]
        available_negatives = [
            item for item, tags in items.items() if not all(tag in tags for tag in rule_tags) and item not in history["negatives"]
        ]

        # Compute available_count based on current history
        available_count = min(len(available_positives), len(available_negatives))

        # Check if requested examples exceed available examples
        examples_exceeded = False
        if num_examples > available_count:
            print(f"Only {available_count} examples are available.")
            examples_exceeded = True
            num_examples = available_count

        # Generate examples for the turn
        positives, negatives = generate_examples(rule, history, num_examples)

        # Update history
        history["positives"].update(positives)
        history["negatives"].update(negatives)
        total_pos_examples_shown += len(positives)
        total_neg_examples_shown += len(negatives)

        # Recalculate remaining examples
        remaining_count = min(
            len([item for item in items if all(tag in items[item] for tag in rule_tags) and item not in history["positives"]]),
            len([item for item in items if not all(tag in items[item] for tag in rule_tags) and item not in history["negatives"]])
        )

        # Generate the prompt
        prompt = get_prompt(turns, remaining_count, positives, negatives, examples_exceeded, max_turns)

        # Emit the SYSTEM message with a unique ID
        message_id += 1
        yield json.dumps({"id": message_id, "sender": "SYSTEM", "content": prompt})
        await asyncio.sleep(1.5)

        message_history.append({"role": "user", "content": prompt})

        try:
            # Get the model response
            llm_action = await get_llm_model_response(model, message_history)
            message_id += 1
            yield json.dumps({"id": message_id, "sender": "USER", "content": llm_action})

            print(f"{model} model's action: {llm_action}")
            message_history.append({"role": "assistant", "content": llm_action})

            if "more" in llm_action and "items from the category" not in llm_action:
                # Parse more request
                parsed_num = parse_more_request(llm_action)
                if parsed_num:
                    num_examples = parsed_num
                else:
                    print("Invalid 'more' request format. Defaulting to 2 examples.")
                    num_examples = 2

            elif llm_action == "give up":
                message_id += 1
                yield json.dumps({"id": message_id, "sender": "SYSTEM", "content": f"Game Over! The rule was: {rule['rule']}"})
                print(f"The rule was: {rule['rule']}")
                break

            else:
                # Check the LLM's guess
                guess_result = await check_guess(llm_action, rule["rule"], history["positives"])
                if guess_result:
                    message_id += 1
                    yield json.dumps({"id": message_id, "sender": "SYSTEM", "content": f"{model} model guessed the rule correctly!"})
                    print(f"{model} model guessed correctly!")
                    break
                else:
                    message_id += 1
                    yield json.dumps({"id": message_id, "sender": "SYSTEM", "content": "Incorrect guess. Try again!"})
                    print(f"{model} model's guess was incorrect.")
                    if remaining_count == 0:
                        message_id += 1
                        yield json.dumps({"id": message_id, "sender": "SYSTEM", "content": "No more examples available. Game over!"})
                        print("No more examples available. Game over!")
                        break

        except Exception as e:
            # Handle any errors during the LLM interaction
            print(f"Error during LLM interaction: {e}")
            message_id += 1
            yield json.dumps({"id": message_id, "sender": "SYSTEM", "content": f"Error during LLM interaction: {e}"})
            break

