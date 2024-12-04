# dynamic_rule_generator.py

# run this file to generate more rules

import os
import sys
import json
from openai import OpenAI
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(script_dir, '..')))
from dynamic_rule_generator_prompts import *

# Initialize OpenAI client
keys_path = os.path.join(script_dir, 'keys.json')
with open(keys_path, 'r') as f:
    keys = json.load(f)
OPENAI_KEY = keys['OPENAI_API_KEY']
client = OpenAI(api_key=OPENAI_KEY)


def get_llm_response(prompt, sysprompt="You are a creative and diverse assistant."):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": sysprompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.9,  
        top_p=0.95        
    )
    generated_text = response.choices[0].message.content.strip()
    return generated_text

prompt_generators = {
    "attribute_based": generate_attribute_based_rule_prompt,
    "categorical": generate_categorical_rule_prompt,
    "relational": generate_relational_rule_prompt,
    "logical": generate_logical_rule_prompt,
    "semantic": generate_semantic_rule_prompt
}

def generate_rules(rule_type, n, directory):
    os.makedirs(directory, exist_ok=True)

    if rule_type not in prompt_generators:
        raise ValueError(f"Invalid rule_type '{rule_type}'. Valid options are: {list(prompt_generators.keys())}")

    # Prepare the filename
    filename = os.path.join(directory, f"{rule_type}_rules.json")

    # Load existing rules if the file exists
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                existing_rules = json.load(f)
            print(f"Loaded {len(existing_rules)} existing rules from '{filename}'.")
        except json.JSONDecodeError:
            print(f"Warning: The file '{filename}' contains invalid JSON. Overwriting the file.")
            existing_rules = []
    else:
        existing_rules = []
        print(f"No existing file found. Creating new file '{filename}'.")

    # Extract existing rule texts
    existing_rule_texts = [rule['rule'] for rule in existing_rules]

    # Get the prompt function and pass existing rules
    prompt_function = prompt_generators[rule_type]
    prompt = prompt_function(existing_rules=existing_rule_texts)

    new_rules = []

    for i in range(n):
        print(f"Generating rule {i+1}/{n} for rule type '{rule_type}'...")
        try:
            rule_output = get_llm_response(prompt)
            # Extract the rule from the output
            rule_text = rule_output.strip()
            if rule_text.lower().startswith('rule:'):
                rule_text = rule_text[5:].strip()
            else:
                # If the output doesn't start with 'Rule:', handle accordingly
                pass  # Proceed with the output as is

            # Remove surrounding brackets if present
            if rule_text.startswith('[') and rule_text.endswith(']'):
                rule_text = rule_text[1:-1].strip()

            # Add the new rule to the list
            new_rules.append({
                "rule_type": rule_type,
                "rule": rule_text
            })

            # Update the prompt with the new rule to prevent future duplicates
            existing_rule_texts.append(rule_text)
            prompt = prompt_function(existing_rules=existing_rule_texts)

        except Exception as e:
            print(f"Error generating rule {i+1}: {e}")

    # Combine existing and new rules
    combined_rules = existing_rules + new_rules

    # Save the combined rules back to the JSON file
    with open(filename, 'w') as f:
        json.dump(combined_rules, f, indent=4)
    print(f"Saved total of {len(combined_rules)} rules to '{filename}'.")

if __name__ == "__main__":
    # Base directory for rules
    rules_base_dir = os.path.join(script_dir, 'rules')

    # Directories for each rule type
    attribute_based_dir = os.path.join(rules_base_dir, 'attribute_based')
    categorical_dir = os.path.join(rules_base_dir, 'categorical')
    relational_dir = os.path.join(rules_base_dir, 'relational')
    logical_dir = os.path.join(rules_base_dir, 'logical')
    semantic_dir = os.path.join(rules_base_dir, 'semantic')

    # Generate rules
    generate_rules("attribute_based", 10, directory=attribute_based_dir)
    generate_rules("categorical", 10, directory=categorical_dir)
    generate_rules("relational", 10, directory=relational_dir)
    generate_rules("logical", 10, directory=logical_dir)
    generate_rules("semantic", 10, directory=semantic_dir)
