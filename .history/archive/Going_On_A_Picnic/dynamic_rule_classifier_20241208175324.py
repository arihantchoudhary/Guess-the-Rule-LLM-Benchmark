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
    return f"""
You are a system that classifies the abstract reasoning difficulty of given rules for a "Going on a Picnic" game.
Difficulty levels:
- L1: Very easy rule that can be understood and verified quickly.
- L2: Moderately difficult rule, somewhat challenging or slightly ambiguous.
- L3: Complex or hard rule that requires significant abstraction, external knowledge, or tricky logic.

Given the following rule, determine its difficulty level (L1, L2, or L3):

Rule: "{rule}"

Respond with only one of the labels: L1, L2, or L3.
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
    if classification not in ["L1", "L2", "L3"]:
        classification = "L2"  # fallback in case of unexpected response
    return classification

def process_rule_files(base_dir="rules"):
    # Iterate over subdirectories in the `rules` directory
    for subdir_name in os.listdir(base_dir):
        subdir_path = os.path.join(base_dir, subdir_name)
        if os.path.isdir(subdir_path):
            # Expect one json file inside each subdirectory
            # e.g. rules/categorical/categorical.json
            json_file = f"{subdir_name}.json"
            json_path = os.path.join(subdir_path, json_file)
            if os.path.exists(json_path):
                with open(json_path, "r") as f:
                    rules_data = json.load(f)

                classified_rules = {
                    "L1": [],
                    "L2": [],
                    "L3": []
                }

                # Classify each rule
                for rule_obj in rules_data:
                    rule_text = rule_obj.get("rule", "")
                    classification = classify_rule_with_gpt4(rule_text)
                    classified_rules[classification].append({
                        "rule_type": rule_obj.get("rule_type", subdir_name),
                        "Level": classification,
                        "rule": rule_text
                    })

                # Create L1, L2, L3 directories inside this subdirectory
                for level in ["L1", "L2", "L3"]:
                    level_dir = os.path.join(subdir_path, level)
                    if not os.path.exists(level_dir):
                        os.makedirs(level_dir)
                    # Write the classified rules into a JSON file
                    output_file = os.path.join(level_dir, f"{level}.json")
                    with open(output_file, "w") as outfile:
                        json.dump(classified_rules[level], outfile, indent=4)

if __name__ == "__main__":
    process_rule_files("rules")