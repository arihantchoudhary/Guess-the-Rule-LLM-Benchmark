import openai
import os
import csv
import pdb

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_dataset(prompt, max_items=20):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant that helps generate datasets."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.7,
    )
    generated_text = response.choices[0].message.content.strip()
    return generated_text

def save_to_txt(content, filename='dataset.txt'):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

def save_to_csv(content, filename='dataset.csv'):
    lines = content.split('\n')
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for line in lines:
            parts = line.split(',')
            if len(parts) == 2:
                writer.writerow([parts[0].strip(), parts[1].strip()])

if __name__ == "__main__":
    dir_path = './demo_rule'
    with open(os.path.join(dir_path, 'rule.txt'), 'r', encoding='utf-8') as file:
        content = file.read()
    prompt = (
        f"Please generate a dataset containing item names and their corresponding colors, with a total of 100 rows. The items should only have two colors: yellow and red. Each row should contain two fields, the first column being the item name and the second column being the color, separated by a comma. Your data should meet the following rules: {content}. Your response should only include the format below, without any additional text, for example"
        "banana,true\n"
        "apple,false\n"
        
    )

    dataset = generate_dataset(prompt, max_items=20)
    
    save_to_txt(dataset, os.path.join(dir_path, 'dataset.txt'))
    print("dataset has been save as 'dataset.txt'.")
    
    save_to_csv(dataset, os.path.join(dir_path,'dataset.csv' ))
    print("dataset has been save as 'dataset.csv'.")
