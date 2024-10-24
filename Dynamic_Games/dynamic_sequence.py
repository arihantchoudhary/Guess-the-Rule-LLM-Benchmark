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
        "Provide the rule in a concise format."
    )

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates simple mathematical rules."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

def generate_sequence(rule, length=10):
    """
    Generate a sequence based on the given rule.
    """
    # Here we will use eval to interpret simple arithmetic rules.
    # Note: In a real-world scenario, it's important to avoid using eval for security reasons.
    sequence = []
    current_value = random.randint(1, 10)  # Start with a random initial value
    for i in range(length):
        sequence.append(current_value)
        try:
            # Apply the rule to generate the next value
            current_value = eval(rule.format(current_value=current_value, n=i))
            pdb.set_traceI()
        except Exception as e:
            print(f"Error generating sequence with rule '{rule}': {e}")
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
        rule = generate_sequence_rule()
        print(f"Generated Rule: {rule}")
        sequence = generate_sequence(rule)
        print(f"Generated Sequence: {sequence}")
        save_to_dataset(rule, sequence, dataset_path)

    print(f"Sequences and rules saved to {dataset_path}")

if __name__ == "__main__":
    main()
