import random
import string
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI()

# --------------------------------------START OF EXAMPLES--------------------------------------

attributes = {
    "color": ["red", "blue", "green", "yellow", "black", "white", "pink", "purple", "orange"],
    "size": ["small", "medium", "large", "tiny", "huge"],
    "shape": ["circle", "square", "triangle", "rectangle", "oval"],
}

categories = {
    "kitchen items": [
        "fork", "spoon", "knife", "pan", "teapot", 
        "blender", "plate", "mug", "spatula", "whisk", 
        "measuring cup", "oven mitt", "cutting board", 
        "strainer", "can opener", "frying pan", 
        "rolling pin", "pot", "baking tray", "mixing bowl"
    ],
    "animals": [
        "dog", "cat", "elephant", "lion", "penguin", 
        "rabbit", "tiger", "giraffe", "dolphin", "horse", 
        "kangaroo", "zebra", "rhinoceros", "otter", 
        "hippopotamus", "deer", "cheetah", "bear", 
        "owl", "eagle"
    ],
    "fruits": [
        "apple", "banana", "orange", "watermelon", "strawberry", 
        "grape", "pineapple", "kiwi", "peach", "mango", 
        "pear", "blueberry", "blackberry", "raspberry", 
        "lemon", "lime", "plum", "cherry", "grapefruit", "pomegranate"
    ],
    "vehicles": [
        "car", "bike", "bus", "train", "airplane", 
        "boat", "helicopter", "motorcycle", "submarine", 
        "truck", "scooter", "tram", "trolley", "hovercraft", 
        "jet", "sailboat", "canoe", "yacht", "spaceship", "hot air balloon"
    ],
    "furniture": [
        "chair", "table", "bed", "sofa", "wardrobe", 
        "desk", "bookshelf", "cabinet", "stool", "armchair", 
        "bench", "rocking chair", "dresser", "ottoman", 
        "nightstand", "bar stool", "coffee table", "tv stand", 
        "bean bag", "couch"
    ]
}

attribute_items = {
    "color": {
        "red": [
            "fire hydrant", "lipstick", "apple", "chili pepper", "strawberries", 
            "tomato", "ruby", "brick", "lobster", "red panda", 
            "Santa's suit", "ladybug", "pomegranate", "rose", "stoplight", 
            "ketchup", "maple leaf", "fire engine", "heart emoji"
        ],
        "blue": [
            "clear sky", "jeans", "blueberry", "sapphire", 
            "ink pen", "denim jacket", "cornflower", "police uniform",
            "Neptune", "blue jay", "frozen lake", 
            "aquarium water",
        ],
        "green": [
            "grass", "leaf", "avocado", "kiwi fruit", "jade stone", 
            "turtle", "cucumber", "go traffic light", "broccoli", 
            "mint plant","lettuce", "tree frog", "apple", "aloe vera", "caterpillar", "moss"
        ],
        "yellow": [
            "banana", "sunflower", "lemon", "american school bus", "new york taxi cab", 
            "rubber duck", "bumblebee", "gold bar", "egg yolk", 
            "pineapple", "corn", "daffodil", "mustard bottle", "raincoat", 
            "canary", "cheese wedge"
        ],
        "black": [
            "crow", "coal", "black hole", 
            "charcoal", "night sky", "leather jacket", "raven", 
            "bat", "panther", "tuxedo", "charred wood", "tar", 
            "licorice", "coffee",
        ],
        "white": [
            "cotton", "snowman", "polar bear", "whiteboard", "western wedding dress", 
            "milk", "cloud", "pearl", "dandelion seed", "golf ball", 
            "dove", "snowflake", "marshmallow", "toothpaste",
            "all purpose flour", "swan"
        ],
        "pink": [
            "flamingo", "pig", "strawberry ice cream", 
            "blush makeup", "ballet slippers", "tutu", "watermelon flesh", 
            "strawberry milkshake", "cherry blossoms",
        ],
        "purple": [
            "lavender", "amethyst", "eggplant", 
            "plum", "orchid", 
            "lilac", "bruise",
        ],
        "orange": [
            "orange fruit", "pumpkin", "traffic cone", "basketball", "carrot", 
            "ginger tabby cat", "squash", "goldfish",
            "tangerine", "clementine", "construction vest", 
            "fox"
        ]
    },
    "size": {
        "small": [
            "button", "paperclip", "eraser", "golf ball", 
            "key", "thumbtack", "toy car", "sugar cube", "ring", 
            "seashell", "penny", "needle", "ladybug", 
            "pea", "ant", "contact lens", "paper plane",
        ],
        "medium": [
            "laptop", "football", "water bottle", "backpack", "microwave", 
            "cushion", "chair", "basketball", "vase", "frisbee", 
            "helmet", "dog", "umbrella", "pillow", "toaster", 
            "cat", "printer", "suitcase", "notebook", "headphones"
        ],
        "large": [
            "sofa", "car", "refrigerator", "dining table", "bed", 
            "wardrobe", "tree", "boat", "trampoline", "grand piano", 
            "elephant", "mattress", "cow", "pool table", 
            "washing machine", "water tank",
        ],
        "tiny": [
            "ant", "flea", "pin", "grain of sand", "water droplet", 
            "baby spider", "grain of sugar", "splinter", "sesame seed", 
            "snowflake", "hair strand", "matchstick tip", "glitter particle", 
            "speck of dust", "rice grain", "poppy seed", "eye of a needle", 
            "microchip", "crumb", "mite"
        ],
        "huge": [
            "whale", "skyscraper", "airplane", "cruise ship", "mountain", 
            "football stadium", "redwood tree", "glacier", "airship", 
            "boulder", "bridge", "train station", "castle", "cathedral", 
            "ferris wheel", "suspension bridge", "space shuttle", 
            "wind turbine", "volcano", "billboard"
        ]
    },
    "shape": {
        "circle": [
            "pizza", "frisbee", "globe", "plate", "donut", 
            "CD", "moon", "button", "ring", "tire", 
            "clock face", "hula hoop", "coaster", "basketball", 
            "soccer ball", "roulette wheel", "wagon wheel", 
            "steering wheel", "compass", "cookie cutter"
        ],
        "square": [
            "post-it note", "board game tile", "chessboard", "window pane", 
            "floor tile", "picture frame", "cutting board", 
            "book cover", "cracker", "box lid", "playing card", 
            "dice", "puzzle piece", "wall clock", "tile coaster", 
            "quilt patch", "laptop screen", "wall mirror", "Rubik's cube face"
        ],
        "triangle": [
            "yield sign", "nacho chip", "traffic cone", "pyramid", 
            "slice of pizza", "slice of pie", "flag pennant", 
            "sail on a sailboat",
            "warning sign", "wedge of cheese", "mountain peak", 
            "roof gable", "trifold paper", "pizza cutter blade", 
            "nacho chip",
        ],
        "rectangle": [
            "door", "television screen", "brick", "envelope", 
            "whiteboard", "chocolate bar", "flag", "mirror", 
            "book cover", "chalkboard", "license plate", 
            "billboard", "postcard", "mobile phone", 
            "newspaper", "picture frame", "wallet", "playing card box"
        ],
        "oval": [
            "egg", "surfboard", "rugby ball", 
            "almond", "pebble",
            "spoon", "pocket watch", "raindrop", 
            "yoga mat", "jellybean", "avocado pit", 
            "eyeglass lens", "soap bar", "bathtub", 
            "olive", "peach pit"
        ]
    }
}

# --------------------------------------END OF EXAMPLES--------------------------------------

# Semantic rule phrases mapped to the corresponding category keys in 'categories'
semantic_rule_mapping = {
    "Items found in a kitchen": "kitchen items",
    "Animals": "animals",
    "Fruits": "fruits",
    "Vehicles": "vehicles",
    "Furniture": "furniture"
}

semantic_rules = list(semantic_rule_mapping.keys())

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
        rule_type = random.choice(["category", "semantic"])
        if rule_type == "category":
            category = random.choice(list(categories.keys()))
            return {"type": "category", "rule": f"Items from the category '{category}'", "category": category}
        elif rule_type == "semantic":
            semantic_rule = random.choice(semantic_rules)
            context_key = semantic_rule_mapping[semantic_rule]
            return {"type": "semantic", "rule": f"Items related to '{semantic_rule}'", "context": context_key}

    elif difficulty == "L2":
        # Medium difficulty: Attribute-based rules (e.g., items of a certain color, size, or shape)
        attribute_type = random.choice(["color", "size", "shape"])
        attribute_value = random.choice(attributes[attribute_type])
        return {"type": "attribute", "rule": f"Items with {attribute_type} '{attribute_value}'", "attribute_type": attribute_type, "attribute_value": attribute_value}

    elif difficulty == "L3":
        # Hard difficulty: Combination of attributes or categories (e.g., items that are red and from the kitchen)
        if random.choice([True, False]):
            # Combine attribute and category
            attribute_type = random.choice(["color", "size", "shape"])
            attribute_value = random.choice(attributes[attribute_type])
            category = random.choice(list(categories.keys()))
            return {"type": "attribute_category_combo", "rule": f"Items that are {attribute_type} '{attribute_value}' and from the category '{category}'", "attribute_type": attribute_type, "attribute_value": attribute_value, "category": category}
        else:
            # Combine two attributes (e.g., red and small)
            attribute_type1 = random.choice(["color", "size", "shape"])
            attribute_value1 = random.choice(attributes[attribute_type1])
            attribute_type2 = random.choice([a for a in ["color", "size", "shape"] if a != attribute_type1])
            attribute_value2 = random.choice(attributes[attribute_type2])
            return {"type": "attribute_combo", "rule": f"Items that are {attribute_type1} '{attribute_value1}' and {attribute_type2} '{attribute_value2}'", "attribute_type1": attribute_type1, "attribute_value1": attribute_value1, "attribute_type2": attribute_type2, "attribute_value2": attribute_value2}

# Function to generate subtle examples based on the rule
def generate_examples(rule, history):
    positives = []
    negatives = []
    
    if rule["type"] == "category":
        available_positives = [item for item in categories[rule["category"]] if item not in history["positives"]]
        available_negatives = [item for cat in categories if cat != rule["category"] for item in categories[cat] if item not in history["negatives"]]
        
        if len(available_positives) < 2 or len(available_negatives) < 2:
            return [], []

        positives = random.sample(available_positives, min(2, len(available_positives)))
        negatives = random.sample(available_negatives, min(2, len(available_negatives)))

    elif rule["type"] == "semantic":
        available_positives = [item for item in categories[rule["context"]] if item not in history["positives"]]
        available_negatives = [item for cat in categories if cat != rule["context"] for item in categories[cat] if item not in history["negatives"]]

        if len(available_positives) < 2 or len(available_negatives) < 2:
            return [], []

        positives = random.sample(available_positives, min(2, len(available_positives)))
        negatives = random.sample(available_negatives, min(2, len(available_negatives)))

    elif rule["type"] == "attribute":
        available_positives = [item for item in attribute_items[rule["attribute_type"]][rule["attribute_value"]] if item not in history["positives"]]
        available_negatives = [item for item in attribute_items[rule["attribute_type"]][random.choice(attributes[rule["attribute_type"]])] if item not in history["negatives"]]

        if len(available_positives) < 2 or len(available_negatives) < 2:
            return [], []

        positives = random.sample(available_positives, min(2, len(available_positives)))
        negatives = random.sample(available_negatives, min(2, len(available_negatives)))

    elif rule["type"] == "attribute_category_combo":
        available_positives = [item for item in attribute_items[rule["attribute_type"]][rule["attribute_value"]] if item not in history["positives"]]
        available_negatives = [item for item in attribute_items[rule["attribute_type"]][random.choice(attributes[rule["attribute_type"]])] if item not in history["negatives"]]

        if len(available_positives) < 2 or len(available_negatives) < 2:
            return [], []

        positives = random.sample(available_positives, min(2, len(available_positives)))
        negatives = random.sample(available_negatives, min(2, len(available_negatives)))

    elif rule["type"] == "attribute_combo":
        available_positives = [item for item in attribute_items[rule["attribute_type1"]][rule["attribute_value1"]] if item not in history["positives"]]
        available_negatives = [item for item in attribute_items[rule["attribute_type1"]][random.choice(attributes[rule["attribute_type1"]])] if item not in history["negatives"]]

        if len(available_positives) < 2 or len(available_negatives) < 2:
            return [], []

        positives = random.sample(available_positives, min(2, len(available_positives)))
        negatives = random.sample(available_negatives, min(2, len(available_negatives)))

    return positives, negatives

# Function to canonicalize strings for flexible comparison (removing punctuation, case-sensitivity)
def canonicalize_string(s):
    return ''.join(c.lower() for c in s if c not in string.punctuation).strip()

# # Function to check the user's guess
# def check_guess(user_guess, actual_rule):
#     # Canonicalize both strings for comparison
#     return canonicalize_string(user_guess) == canonicalize_string(actual_rule)

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
    hints_enabled = ask_for_hints()

    # Pick a random rule that will be consistent throughout the game
    rule = pick_rule(difficulty)
    
    # History to track presented examples (positives and negatives)
    history = {"positives": set(), "negatives": set()}
    
    # Determine the available examples based on the rule type
    if rule["type"] == "category":
        available_positives = len(categories[rule["category"]])
        available_negatives = sum(len(categories[cat]) for cat in categories if cat != rule["category"])
    else:  # if the rule is "semantic", "attribute", "attribute_combo", or "attribute_category_combo"
        available_positives = len(categories[random.choice(list(categories.keys()))])
        available_negatives = available_positives  # Assume we have enough categories for both positive and negative

    # Calculate maximum turns based on available examples (the minimum between positives and negatives divided by 2)
    max_turns = min(available_positives, available_negatives) // 2

    turn = 1
    while turn <= max_turns:
        print(f"\nTurn {turn}")
        
        # Generate positive and negative examples based on the consistent rule, ensuring no repeats
        positives, negatives = generate_examples(rule, history)
        
        if not positives or not negatives:
            print("\nNo more examples available.")
            break
        
        # Add the generated examples to the history
        history["positives"].update(positives)
        history["negatives"].update(negatives)
        
        # Show examples to the user in natural language
        print(f"I'm going on a picnic. I can bring {positives[0]} and {positives[1]}.")
        print(f"I cannot bring {negatives[0]} or {negatives[1]}.")

        # Provide a hint if the user opted for it
        if hints_enabled:
            if rule["type"] == "category":
                print("\nHint: The answer is something like 'Items from the category X'.")
            elif rule["type"] == "semantic":
                print("\nHint: The answer is something like 'Items related to X'.")
            elif rule["type"] == "attribute":
                print(f"\nHint: The answer is something like 'Items with {rule['attribute_type']} X'.")
            elif rule["type"] == "attribute_combo":
                print(f"\nHint: The answer is something like 'Items that are {rule['attribute_type1']} and {rule['attribute_type2']}'.")
            elif rule["type"] == "attribute_category_combo":
                print(f"\nHint: The answer is something like 'Items that are {rule['attribute_type']} and from the category X'.")

        # User guesses the rule
        user_input = input("\nWhat's the rule? \nType 'more' for more examples \nType 'give up' to end the game and see the rule): ").strip().lower()
        
        if user_input == "more":
            turn += 1
            continue
        elif user_input == "give up":
            print(f'The rule was: {rule['rule']}')
            return
        
        # Check the user's guess with the actual rule using canonicalized comparison
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
