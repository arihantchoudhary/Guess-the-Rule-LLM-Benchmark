import random

# Define the rule categories and templates for each type of rule.
rule_templates = {
    "attribute_based": [
        "Only things that are {attribute}.",   # Example: "Only things that are green."
        "Only objects that are {size}.",       # Example: "Only objects that are larger than a loaf of bread."
        "Only objects that have a {shape} shape."  # Example: "Only objects that have a circular shape."
    ],
    "categorical": [
        "Only objects that belong to the category {category}.",  # Example: "Only animals can be brought."
        "Only things that are types of {subcategory}.",          # Example: "Only fruits."
    ],
    "relational": [
        "Only things that are {relation} than a {object}.",      # Example: "Only things larger than a book."
        "Only things that are {comparison} to a {context_object}."  # Example: "Only things heavier than a car."
    ],
    "logical": [
        "Only objects that are both {attribute_1} and {attribute_2}.",  # Example: "Only objects that are red and circular."
        "Only things that are either {attribute_1} or {attribute_2}.",  # Example: "Only objects that are metallic or soft."
    ],
    "semantic": [
        "Only things that are used in a {context}.",             # Example: "Only things used in the kitchen."
        "Only objects that are related to {contextual_activity}."  # Example: "Only things related to camping."
    ]
}

# Example attributes, categories, relations, etc.
attributes = ["green", "yellow", "large", "small", "round", "square"]
categories = ["animals", "furniture", "fruits", "vehicles"]
relations = ["larger", "smaller", "heavier", "lighter"]
contextual_objects = ["car", "book", "pencil"]
contextual_activities = ["cooking", "camping", "cleaning"]
contexts = ["kitchen", "bedroom", "outdoors"]

# Function to select a random template from a rule type and generate the prompt
def generate_rule_prompt(rule_type):
    template = random.choice(rule_templates[rule_type])
    
    # Fill in the template with appropriate values based on the rule type
    if rule_type == "attribute_based":
        return template.format(attribute=random.choice(attributes), 
                               size=random.choice(["larger", "smaller"]), 
                               shape=random.choice(["circular", "square"]))
    elif rule_type == "categorical":
        return template.format(category=random.choice(categories), 
                               subcategory=random.choice(["fruits", "tools", "vehicles"]))
    elif rule_type == "relational":
        return template.format(relation=random.choice(relations), 
                               object=random.choice(contextual_objects), 
                               comparison=random.choice(["similar", "different"]),
                               context_object=random.choice(contextual_objects))
    elif rule_type == "logical":
        return template.format(attribute_1=random.choice(attributes), 
                               attribute_2=random.choice(attributes))
    elif rule_type == "semantic":
        return template.format(context=random.choice(contexts), 
                               contextual_activity=random.choice(contextual_activities))

# Example rule generation
def generate_rule():
    rule_type = random.choice(list(rule_templates.keys()))
    prompt = generate_rule_prompt(rule_type)
    
    print(f"Generated rule type: {rule_type}")
    print(f"Rule: {prompt}")
    
    # Here you would use an LLM like GPT to provide more creative options or refinement:
    # Example LLM Prompt for rule refinement: "Create a rule for going on a picnic: {prompt}"
    # response = llm.generate(prompt)
    
    return prompt  # Or the final response from the LLM

# Main loop to generate and display a rule
if __name__ == "__main__":
    print("Generating picnic rules dynamically...")
    for _ in range(5):
        rule = generate_rule()
        print("\n")