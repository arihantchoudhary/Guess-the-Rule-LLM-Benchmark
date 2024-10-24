import openai
import csv
import os
import random
import pdb

# Initialize OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_sequence_rule():
    """
    Use OpenAI's model to generate a mathematical rule for generating a sequence.
    """
    prompt = (
        "Generate a mathematical rule that can be used to create a sequence for elementary school students to find a pattern. "
        "The rule should be simple and suitable for children, such as 'add 3 each time', 'multiply by 2', or 'alternating add 1 and subtract 1'. "
        "Provide the rule in a concise format and generate a Python function that implements this rule."
    )

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates simple mathematical rules and Python functions."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.7,
        )
    return response.choices[0].message.content.strip()

def get_function_code(rule):
    # Extract and execute the function from the generated code
    start_idx = rule.find("def generate_next")
    if start_idx == -1:
        print("Error: Generated rule does not contain a valid function definition.")
        return []
    rule_function_code = rule[start_idx:]
    print(f"Rule Function Code: {rule_function_code}")
    print('type(rule_function_code)', type(rule_function_code))
    return rule_function_code

def generate_sequence_function(rule_code):
    """
    Generate a sequence using the provided Python-style function code.
    """
    # Define the function from the generated code
    rule_code = get_function_code(rule_code)
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

def save_to_dataset(rule, sequence, dataset_path="sequence_dataset.csv"):
    """
    Save the generated rule and sequence to a CSV file.
    """
    with open(dataset_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([rule, sequence])

def main():
    dir_path = './demos'
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    dataset_path = os.path.join(dir_path, "sequence_dataset.csv")
    # Create CSV file and write headers if not exists
    if not os.path.exists(dataset_path):
        with open(dataset_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Rule", "Sequence"])

    # Generate a specified number of sequences
    num_sequences = 10
    for _ in range(num_sequences):
        rule_code = generate_sequence_rule()
        print(f"Generated Rule Code: {rule_code}")
        sequence = generate_sequence_function(rule_code)
        print(f"Generated Sequence: {sequence}")
        save_to_dataset(rule_code, sequence, dataset_path)

    print(f"Sequences and rules saved to {dataset_path}")

if __name__ == "__main__":
    main()
