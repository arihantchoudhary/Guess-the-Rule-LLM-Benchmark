import random
import re
import json
import time
import os
import sys
import string
import pandas as pd
from datetime import datetime
import anthropic
import google.generativeai

from openai import OpenAI
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Initialize the OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI()

# Initialize the Anthropic client
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Configure the Google PaLM API key
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
google.generativeai.configure(api_key=GOOGLE_API_KEY)

# MAX_TURNS = 3

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
# if len(sys.argv) != 2 or sys.argv[1] not in ["L1", "L2", "L3"]:
#     print("Usage: python script_name.py <difficulty_level>")
#     print("Where <difficulty_level> is one of: L1, L2, L3")
#     sys.exit(1)

# difficulty = sys.argv[1]

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

def check_guess(user_guess, actual_rule, positive_examples):
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
        response = openai_client.chat.completions.create(
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
def get_llm_model_response(platform, model, message_history):
    if platform == 'openai':
        response = openai_client.chat.completions.create(
            model=model,
            messages=message_history
        )
        return response.choices[0].message.content.strip().lower()
    elif platform == 'anthropic':
        system_prompt = ''
        user_prompts = []
        for m in message_history:
            if not system_prompt and m['role'] == 'system':
                system_prompt += m['content']
            elif m['role'] == 'user':
                user_prompts.append(m)

        response = anthropic_client.messages.create(
            max_tokens=1024,
            system=system_prompt,
            messages=user_prompts,
            model=model,
        )
        return response.content[0].text.strip().lower()
    elif platform == 'google':
        # change the format of message history for google's model
        google_messages_history = []
        for m in range(len(message_history) - 1):
            curr_message = message_history[m]
            if curr_message['role'] == 'system':
                google_messages_history.append({'role': 'model', 'parts': curr_message['content']})
            elif curr_message['role'] == 'user':
                google_messages_history.append({'role': 'user', 'parts': curr_message['content']})

        gen_model = google.generativeai.GenerativeModel(model)
        chat = gen_model.start_chat(
            history=google_messages_history
        )
        response = chat.send_message(message_history[-1]['content'])
        return response.text
    else:
        assert False, f'Unknown platform {platform} given'

# Main function to run the game
def play_game_with_llms(difficulty, max_turns, platform, model):
    start_time = time.time()
    rule = pick_rule(difficulty)
    print(f"------------ Starting the game with {model} on difficulty {difficulty} with max turns {max_turns}. Rule: {rule['rule']} ------------")

    history = {"positives": set(), "negatives": set()}
    message_history = [
        {"role": "system", "content": "You are playing a game called 'Going on a Picnic'. Your goal is to guess the rule behind a set of examples. You can request more examples or make a guess."}
    ]
    turns = 0
    llm_won = False
    total_examples_available = 0
    total_pos_examples_shown = 0
    total_neg_examples_shown = 0

    # Initial examples to show
    num_examples = 2

    while turns < max_turns:
        turns += 1
        # Calculate available examples for the turn
        rule_tags = rule["categories"] if "categories" in rule else [rule["category"]]
        available_positives = [
            item for item, tags in items.items() if all(tag in tags for tag in rule_tags) and item not in history["positives"]
        ]
        available_negatives = [
            item for item, tags in items.items() if not all(tag in tags for tag in rule_tags) and item not in history["negatives"]
        ]

        # Compute available_count based on current history
        available_count = min(len(available_positives), len(available_negatives))

        if turns == 1:
            total_examples_available = available_count

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
        total_pos_examples_shown += len(positives)
        total_neg_examples_shown += len(negatives)

        # Recalculate available examples for the next turn after updating history
        available_positives = [
            item for item, tags in items.items() if all(tag in tags for tag in rule_tags) and item not in history["positives"]
        ]
        available_negatives = [
            item for item, tags in items.items() if not all(tag in tags for tag in rule_tags) and item not in history["negatives"]
        ]
        available_count = min(len(available_positives), len(available_negatives))
        remaining_count = available_count


        prompt = get_prompt(turns, remaining_count, positives, negatives, examples_exceeded, max_turns)

        print(f"\n\n*** Prompt for turn {turns} ***\n{prompt}\n\n")

        message_history.append({"role": "user", "content": prompt})

        try:
            llm_action = get_llm_model_response(platform, model, message_history)
            print(f"{model} model's action: {llm_action}")

            # Record the LLM's action in the message history
            message_history.append({"role": "assistant", "content": llm_action})

            if "more" in llm_action and "items from the category" not in llm_action:
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
                if check_guess(llm_action, rule["rule"], history["positives"]):
                    print(f"{model} model guessed correctly!")
                    llm_won = True
                    break
                else:
                    print(f"{model} model's guess was incorrect.")
                    if remaining_count == 0:
                        print("No more examples available. Game over!")
                        break
        except Exception as e:
            llm_action = 'failed'
            print(f"Error during LLM interaction: {e}")
            break

    end_time = time.time()
    duration = end_time - start_time

    print("\n***Game Summary***")
    print(f"Rule: {rule['rule']}")
    print(f"Turns taken: {turns}")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Total examples available: {total_examples_available}")
    print(f"Positive examples shown: {total_pos_examples_shown}")
    print(f"Negative examples shown: {total_neg_examples_shown}")
    print(f"Result: {f'{model} won' if llm_won else f'{model} lost'}")

    return rule, turns, duration, total_examples_available, total_pos_examples_shown, total_neg_examples_shown, llm_action, llm_won

if __name__ == "__main__":
    valid_difficulties = ['L1', 'L2', 'L3']
    max_turns = [1, 3, 5, 7, 10, 15]
    total_iterations = 5
    llm_models = {
        'openai': [
                # 'gpt-4o-mini',
                'gpt-4o',
        ], # good, fast and cheap
        'anthropic': [
            'claude-3-haiku-20240307',
            'claude-3-5-haiku-latest'
        ], # good, fast and cheap
        'google': [
            'gemini-1.5-flash',
            'gemini-1.5-flash-8b'
        ] # good, fast and cheap
    }
    # llm_models['openai'] += ['o1-mini', 'o1-preview'] # expensive models; check them at the end
    # llm_models['anthropic'] += ['claude-3-sonnet-20240229', 'claude-3-5-sonnet-latest'] # expensive models; check them at the end
    # llm_models['google'] += ['gemini-1.5-pro'] # expensive models; check them at the end

    # run experiments
    results = []
    for platform in list(llm_models.keys()):
        for model in llm_models[platform]:
            for difficulty in valid_difficulties:
                for curr_max_turns in max_turns:
                    for iteration in range(total_iterations):
                        rule, turns_taken, duration, total_examples_available, total_pos_examples_shown, total_neg_examples_shown, llm_final_answer, llm_won = play_game_with_llms(difficulty, curr_max_turns, platform, model)
                        # Append the results to the list
                        results.append({
                            "Model": model,
                            "Win": 1 if llm_won else 0, # 1 or 0
                            "Difficulty": difficulty,
                            "Max Turns": curr_max_turns,
                            "Iteration": iteration+1,
                            "Rule": rule['rule'],
                            "Turns Taken": turns_taken,
                            "Duration (s)": round(duration, 2),
                            "Total Examples Available": total_examples_available,
                            "Positive Examples Shown": total_pos_examples_shown,
                            "Negative Examples Shown": total_neg_examples_shown,
                            "LLM Final Answer": llm_final_answer
                        })

    current_date = datetime.now()
    formatted_date = current_date.strftime("%m_%d_%Y")

    df = pd.DataFrame(results)
    print(f"\n*** FINAL RESULTS {formatted_date} ***")
    print(df)

    experiment_results_file_name = f"experiment_{formatted_date}.csv"
    df.to_csv(experiment_results_file_name, index=False)

    cols_for_analysis = ['Model', 'Win', 'Difficulty', 'Max Turns', 'Turns Taken', 'Duration (s)', 'Total Examples Available', 'Positive Examples Shown', 'Negative Examples Shown']
    cols_for_grouping = ['Model', 'Difficulty', 'Max Turns']
    mean_results = df[cols_for_analysis].groupby(cols_for_grouping).agg({'Win': 'sum', 'Turns Taken': 'mean', 'Duration (s)': 'mean', 'Total Examples Available': 'mean', 'Positive Examples Shown': 'mean', 'Negative Examples Shown': 'mean'})
    mean_results.to_csv(f"experiment_agg_{formatted_date}.csv", index=True)
