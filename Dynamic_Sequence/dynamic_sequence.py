import openai
import csv
import os
import random
import pdb
import argparse

# Initialize OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_sequence_rule():
    """
    Use OpenAI's model to generate a mathematical rule for generating a sequence.
    """
    prompt = (
        "Generate a mathematical rule that can be used to create a sequence for elementary school students to find a pattern. "
        "The rule should not be obvious and should be challenging but solvable for students. For example, the rule could be 'add Fibonacci sequence(index) to the input' or 'multiply by 3 and subtract 1'."
        "Provide the rule in a concise format and generate a Python function that implements this rule."
        "The function input is the current value in the sequence and the index of the current value, and the output is the next value in the sequence."
        "Do not use any Markdown formatting (such as triple backticks ```) in the response."
        "Your response should include the following format:\n\n"
        "Mathematical rule: <Your explaination of the rule in natural language>\n\n"
        "(Important) Your should end your mathematical rule with a '$$'\n\n"
        "def generate_next(current_value, index):\n    # Your code here\n    return next-value-in-the-sequence"
        "(Important) Your shoud end your function with a '&&'\n\n"
        "Make sure the function is valid and can be executed to generate a sequence."
    )

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates mathematical rules and Python functions."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=1,
        )
    return response.choices[0].message.content.strip()

def get_function_code(rule):
    # Extract Natural Language Mathematical Rule
    math_start_index = rule.find("Mathematical rule:")
    math_end_index = rule.find("$$")
    rule_math_code = rule[math_start_index:math_end_index].replace("Mathematical rule:", "").strip()
    
    # Extract Python Function Code
    start_idx = rule.find("def")
    if start_idx == -1:
        print("Error: Generated rule does not contain a valid function definition.")
        return []
    end_index = rule.find("&&")
    rule_function_code = rule[start_idx:end_index]
    rule_function_code = rule_function_code.replace("```python", "").replace("```", "").strip()
    return rule_math_code, rule_function_code


def generate_sequence_function(rule_code):
    """
    Generate a sequence using the provided Python-style function code.
    """
    # Define the function from the generated code
    exec(rule_code, globals())
    sequence = []
    current_value = random.randint(1, 10)
    for i in range(10):
        sequence.append(current_value)
        try:
            current_value = generate_next(current_value, i)
        except Exception as e:
            print(f"Error generating sequence with rule function: {e}")
            break
    return sequence

def save_to_dataset(sequence, dataset_path):
    """
    Save the generated rule and sequence to a CSV file.
    """
    with open(dataset_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(sequence)

def main(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    # Generate a specified number of sequences
    num_rules = 5
    num_sequences = 10
    num_rule = 0
    while num_rule < num_rules:
        rule_code = generate_sequence_rule()
        if rule_code == []:
            continue

        # Address Specification
        current_rule_dir = os.path.join(dir_path, f'rule_{num_rule}')
        if not os.path.exists(current_rule_dir):
            os.makedirs(current_rule_dir)
        rule_math_path = os.path.join(current_rule_dir, 'math_rule.txt')
        rule_code_path = os.path.join(current_rule_dir, 'code_rule.txt')
        rule_sequence_path = os.path.join(current_rule_dir, 'sequence_dataset.csv')
        
        # get the mathematical rule and function code
        math_rule, code_rule = get_function_code(rule_code)

        # write the rule and function code to files
        with open(rule_math_path, 'w') as file:
            file.write(math_rule)
        with open(rule_code_path, 'w') as file:
            file.write(code_rule)
        
        # Generate sequences based on the rule
        for _ in range(num_sequences):  
            sequence = generate_sequence_function(code_rule)
            save_to_dataset(sequence, rule_sequence_path)
        num_rule += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--save_dir", type=str, default='./demos', help="the dictionary to save the generated dataset")
    args = parser.parse_args()
    main(args.save_dir)
