import csv
import os
import openai
import pdb

def load_rule(rule_path):
    with open(rule_path, 'r') as rule_file:
        return rule_file.read().strip()

# Initialize OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define the agents using OpenAI's LLM
def agent_llm(data, rule, model):
    prompt = f"According to the rule: '{rule}', the data I provide follows the format: [<object>, <true or false>], where the first item is the object, and the second item indicates whether the object complies with the rule. Your task is to evaluate this object based on the rule and compare your result with the previous agent's answer. If your result matches theirs, return 'true'; if it differs, return 'false'. No explanation is needed.\nItem: {', '.join(data)}"
    response = openai.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an assistant agent that checks if the item is true or false."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def read_dataset(dataset_path):
    with open(dataset_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        return [row for row in reader]

def save_inconsistent_results(output_path, inconsistent_results):
    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Item Details'])
        writer.writerows(inconsistent_results)

def main(dir_path):
    # Load the rule
    rule_path = os.path.join(dir_path, 'rule.txt')
    rule = load_rule(rule_path)

    # Read the dataset
    dataset_path = os.path.join(dir_path, 'dataset.csv')
    dataset = read_dataset(dataset_path)
    inconsistent_results = []

    # models = ["gpt-3.5-turbo", "text-davinci-003", "text-davinci-002"]
    models = ["gpt-3.5-turbo", "gpt-3.5-turbo", "gpt-3.5-turbo"]

    # Process the dataset
    for idx, row in enumerate(dataset):
        result_1 = agent_llm(row, rule, models[0])
        result_2 = agent_llm(row, rule, models[1])
        result_3 = agent_llm(row, rule, models[2])
        # Check if the agents have different results
        print('Results:', row[1], result_1, result_2, result_3)
        if len(set([row[1], result_1, result_2, result_3])) > 1:
            inconsistent_results.append([idx, row])

    # Save inconsistent results to a new file
    output_path =  os.path.join(dir_path, 'inconsistent_results.csv')
    save_inconsistent_results(output_path, inconsistent_results)

    print(f"Inconsistent results saved to {output_path}")

if __name__ == "__main__":
    dir_path = './demo_rule'
    main(dir_path)
