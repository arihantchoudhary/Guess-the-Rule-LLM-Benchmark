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
    # Prompt template for GPT-4 classification
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

if __name__ == "__main__":
    