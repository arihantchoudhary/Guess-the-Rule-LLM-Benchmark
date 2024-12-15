# dynamic_rule_classifier.py

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

def get_prompt_template(rule):
    # A new prompt that focuses on complexity and abstractness in "Guess the Rule Games"
    return f"""
You are an expert in analyzing "Guess the Rule Games." 
Your task is to classify a given rule into one of three complexity levels based on how abstract and conceptually challenging it is:

- L1: The rule is straightforward and concrete, requiring little to no abstraction. Anyone can quickly understand and apply it.
- L2: The rule is moderately abstract or involves some logical reasoning or pattern recognition that isn't immediately obvious. It may require a moment of thought or some reasoning steps to fully grasp.
- L3: The rule is highly abstract, conceptually difficult, or relies on complex, non-trivial reasoning patterns. It may involve multiple layers of logic, external knowledge, or intricate patterns that are challenging to understand.

Consider the complexity and level of abstraction required to comprehend the given rule. Then assign it one of the labels: L1, L2, or L3.

Rule: "{rule}"

Respond with only one label: L1, L2, or L3.
"""

def classify_rule_with_gpt4(rule):
    prompt = get_prompt_template(rule)
    messages = [{"role": "system", "content": prompt}]
    response = client.chat.completions.create(
        model="gpt-4o", 
        messages=messages,
        temperature=0
    )
    classification = response.choices[0].message.content.strip()
    return classification

def classify_until_valid(rule):
    valid_levels = ["L1", "L2", "L3"]
    classification = classify_rule_with_gpt4(rule)
    attempts = 1
    # If invalid, keep trying until we get a correct label
    while classification not in valid_levels:
        print("\nClassification for rule failed!\n")
        classification = classify_rule_with_gpt4(rule)
        attempts += 1
        # Optional: include a safeguard in case the model keeps failing
        if attempts > 5:
            # fallback to L2 or handle differently
            classification = "L2"
            break
    return classification

def process_rule_files(base_dir="rules"):
    # Iterate over subdirectories in the `rules` directory
    for subdir_name in os.listdir(base_dir):
        subdir_path = os.path.join(base_dir, subdir_name)
        if os.path.isdir(subdir_path):
            json_file = f"{subdir_name}.json"
            json_path = os.path.join(subdir_path, json_file)
            print(json_path)
            if os.path.exists(json_path):
                with open(json_path, "r") as f:
                    rules_data = json.load(f)
                    print(rules_data)

                # Classify only those rules that do not have a 'level' key
                modified = False
                for rule_obj in rules_data:
                    if "level" not in rule_obj:
                        rule_text = rule_obj.get("rule", "")
                        classification = classify_until_valid(rule_text)
                        rule_obj["level"] = classification
                        modified = True
                        print(f"\nRule classified!\n")

                # If we made changes, rewrite the file
                if modified:
                    with open(json_path, "w") as outfile:
                        json.dump(rules_data, outfile, indent=4)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(script_dir, "rules")
    process_rule_files(base_dir)