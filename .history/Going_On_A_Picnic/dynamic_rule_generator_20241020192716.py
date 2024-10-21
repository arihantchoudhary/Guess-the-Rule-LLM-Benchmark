import random
import openai  # Assuming you're using OpenAI's GPT model

# Set your OpenAI API key (or any other LLM provider's key)
openai.api_key = "YOUR_OPENAI_API_KEY"

# Define the rule templates for each rule type.
rule_templates = {
    "attribute_based": "Generate a rule based on a single object attribute like color, size, or shape.",
    "categorical": "Generate a rule based on a specific category of objects.",
    "relational": "Generate a rule based on a relational attribute between objects (e.g., size, weight).",
    "logical": "Generate a rule that combines two attributes using logical conditions like AND or OR.",
    "semantic": "Generate a rule that involves objects related by their use or context (e.g., used in a kitchen)."
}
# Function to send a prompt to the LLM and get the response
def get_llm_response(prompt):
    response = openai.Completion.create(
        model="text-davinci-003",  # You can replace this with any LLM model you're using
        prompt=prompt,
        max_tokens=100,  # Adjust token size based on expected response length
        temperature=0.7  # Adjust for more creativity or randomness
    )
    return response.choices[0].text.strip()

# Function to generate a rule prompt for each rule type
def generate_rule_prompt(rule_type):
    template_prompt = rule_templates[rule_type]
    return template_prompt

# Function to collect and process the LLM outputs from the rule prompt
def generate_rule_with_llm(rule_type):
    # Generate the template prompt based on the rule type
    prompt = generate_rule_prompt(rule_type)
    
    # Call the LLM with the prompt to generate a specific rule
    llm_response = get_llm_response(prompt)
    
    # Process and return the rule generated by the LLM
    return llm_response

# Example of generating rules
def generate_rule():
    # Randomly select a rule type
    rule_type = random.choice(list(rule_templates.keys()))
    
    # Get the specific rule from the LLM based on the rule type
    rule = generate_rule_with_llm(rule_type)
    
    print(f"Generated rule type: {rule_type}")
    print(f"Rule: {rule}")
    
    return rule

# Main loop to generate and display a set of rules
if __name__ == "__main__":
    print("Generating picnic rules dynamically from LLM...")
    for _ in range(5):
        rule = generate_rule()
        print("\n")