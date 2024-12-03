from openai import OpenAI 
import dotenv
import os
from openai import OpenAI 

# Load environment variables
dotenv.load_dotenv()
client = OpenAI(api_key= os.getenv("OPENAI_API_KEY"))

def generate_response(prompt, model="gpt-4"):
    response = client.chat.completions.create(
        model="gpt-4",  # Replace with "gpt-3.5-turbo" or your desired model
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    generated_text = response.choices[0].message.content.strip()
    return generated_text


def chat_between_models(model1="gpt-4", model2="gpt-4"):
    prompt1= "Give me math problem and some instructions on how to solve it and ask me to solve it"
    print(f"Model 1: {prompt1}")

    for i in range(5):  # Limit the conversation to 5 exchanges
        response1 = generate_response(prompt1, model=model1)
        print(f"Model 2: {response1}")

        response2 = generate_response(response1, model=model2)
        print(f"Model 1: {response2}")

        prompt1 = response2

if __name__ == "__main__":
    chat_between_models()
