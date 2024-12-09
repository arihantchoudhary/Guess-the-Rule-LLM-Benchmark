# dynamic_rule_generator_prompts.py

def generate_attribute_based_rule_prompt(existing_rules=None):
    existing_rules_text = ""
    if existing_rules:
        existing_rules_text = "\n".join(f"- {rule}" for rule in existing_rules)
        existing_rules_text = f"You have already created the following rules and should not repeat them:\n{existing_rules_text}\n"

    prompt = f"""
You are the game master for "Going on a Picnic." {existing_rules_text}Your task is to create a **unique and creative attribute-based rule** that determines which items can be brought to the picnic.

- The rule should be based on a specific attribute of the items (e.g., items that contain double letters, items with exactly five letters).
- Avoid common attributes like color or starting letter.
- Think of less obvious attributes to make the game challenging.
- Clearly state the rule.

Do not include any examples or additional text.

Format:

Rule: [Your unique attribute-based rule]
"""
    return prompt

# Similarly modify other prompt functions
def generate_categorical_rule_prompt(existing_rules=None):
    existing_rules_text = ""
    if existing_rules:
        existing_rules_text = "\n".join(f"- {rule}" for rule in existing_rules)
        existing_rules_text = f"You have already created the following rules and should not repeat them:\n{existing_rules_text}\n"

    prompt = f"""
You are the game master for "Going on a Picnic." {existing_rules_text}Your task is to create a **unique and creative categorical rule** that determines which items can be brought to the picnic.

- The rule should be based on a less obvious category or group (e.g., items related to time, mythical creatures).
- Avoid common categories like fruits or animals.
- Clearly state the rule.

Do not include any examples or additional text.

Format:

Rule: [Your unique categorical rule]
"""
    return prompt

def generate_relational_rule_prompt(existing_rules=None):
    existing_rules_text = ""
    if existing_rules:
        existing_rules_text = "\n".join(f"- {rule}" for rule in existing_rules)
        existing_rules_text = f"You have already created the following rules and should not repeat them:\n{existing_rules_text}\n"

    prompt = f"""
You are the game master for "Going on a Picnic." {existing_rules_text}Your task is to create a **unique and creative relational rule** that determines which pairs of items can be brought to the picnic.

- The rule should be based on a specific relationship between pairs of items (e.g., items that are anagrams of each other, items that are sequential in the alphabet).
- Avoid common relationships like rhyming words.
- Clearly state the rule.

Do not include any examples or additional text.

Format:

Rule: [Your unique relational rule]
"""
    return prompt

def generate_logical_rule_prompt(existing_rules=None):
    existing_rules_text = ""
    if existing_rules:
        existing_rules_text = "\n".join(f"- {rule}" for rule in existing_rules)
        existing_rules_text = f"You have already created the following rules and should not repeat them:\n{existing_rules_text}\n"

    prompt = f"""
You are the game master for "Going on a Picnic." {existing_rules_text}Your task is to create a **unique and creative logical rule** that determines which items can be brought to the picnic.

- The rule should involve a logical condition, possibly combining multiple attributes or categories (e.g., items that are either palindromes or have exactly seven letters, but not both).
- Avoid simple or previously used logical conditions.
- Clearly state the rule.

Do not include any examples or additional text.

Format:

Rule: [Your unique logical rule]
"""
    return prompt

def generate_semantic_rule_prompt(existing_rules=None):
    existing_rules_text = ""
    if existing_rules:
        existing_rules_text = "\n".join(f"- {rule}" for rule in existing_rules)
        existing_rules_text = f"You have already created the following rules and should not repeat them:\n{existing_rules_text}\n"

    prompt = f"""
You are the game master for "Going on a Picnic." {existing_rules_text}Your task is to create a **unique and creative semantic rule** that determines which items can be brought to the picnic.

- The rule should be based on a semantic property or meaning associated with the items (e.g., items associated with royalty, items that symbolize wisdom).
- Avoid common themes or previously used semantic properties.
- Clearly state the rule.

Do not include any examples or additional text.

Format:

Rule: [Your unique semantic rule]
"""
    return prompt


def L1_generate_attribute_based_rule_prompt(existing_rules=None):
    existing_rules_text = ""
    if existing_rules:
        existing_rules_text = "\n".join(f"- {rule}" for rule in existing_rules)
        existing_rules_text = f"You have already created the following rules and should not repeat them:\n{existing_rules_text}\n"

    prompt = f"""
You are the game master for "Guess the Rule Games." {existing_rules_text}Your task is to create a **simple attribute-based rule** not in the list above that determines which items can be brought to the game.

- The rule should be based on a straightforward attribute of the items (e.g., items that are red, items that start with the letter 'A').
- Use common and easily recognizable attributes.
- Make sure the rule is something even children could guess correctly.
- Avoid complex or abstract attributes.
- Ensure the rule is easy to understand and apply.
- Clearly state the rule.

Do not include any examples or additional text.

Format:

Rule: [Your simple attribute-based rule]
"""
    return prompt


def L1_generate_categorical_rule_prompt(existing_rules=None):
    existing_rules_text = ""
    if existing_rules:
        existing_rules_text = "\n".join(f"- {rule}" for rule in existing_rules)
        existing_rules_text = f"You have already created the following rules and should not repeat them:\n{existing_rules_text}\n"

    prompt = f"""
You are the game master for "Guess the Rule Games." {existing_rules_text}Your task is to create a **simple categorical rule** not in the list above that determines which items can be brought to the game.

- The rule should be based on a common and easily identifiable category or group (e.g., fruits, animals, kitchen utensils).
- Use familiar and widely recognized categories.
- Make sure the rule is something even children could guess correctly.
- Avoid obscure or complex categories.
- Ensure the rule is easy to understand and apply.
- Clearly state the rule.

Do not include any examples or additional text.

Format:

Rule: [Your simple categorical rule]
"""
    return prompt


def L1_generate_relational_rule_prompt(existing_rules=None):
    existing_rules_text = ""
    if existing_rules:
        existing_rules_text = "\n".join(f"- {rule}" for rule in existing_rules)
        existing_rules_text = f"You have already created the following rules and should not repeat them:\n{existing_rules_text}\n"

    prompt = f"""
You are the game master for "Guess the Rule Games." {existing_rules_text}Your task is to create a **simple relational rule** not in the list above that determines which pairs of items can be brought to the game.

- The rule should be based on a straightforward relationship between pairs of items (e.g., items that are the same color, items that share the same starting letter).
- Use common and easily understandable relationships.
- Make sure the rule is something even children could guess correctly.
- Avoid complex or abstract relationships.
- Ensure the rule is easy to understand and apply.
- Clearly state the rule.

Do not include any examples or additional text.

Format:

Rule: [Your simple relational rule]
"""
    return prompt


def L1_generate_logical_rule_prompt(existing_rules=None):
    existing_rules_text = ""
    if existing_rules:
        existing_rules_text = "\n".join(f"- {rule}" for rule in existing_rules)
        existing_rules_text = f"You have already created the following rules and should not repeat them:\n{existing_rules_text}\n"

    prompt = f"""
You are the game master for "Guess the Rule Games." {existing_rules_text}Your task is to create a **simple logical rule** not in the list above that determines which items can be brought to the game.

- The rule should involve a basic logical condition, such as "items that are even-numbered letters" or "items that start with a vowel."
- Use straightforward logical conditions that are easy to follow.
- Make sure the rule is something even children could guess correctly.
- Avoid combining multiple attributes or using complex logic.
- Ensure the rule is easy to understand and apply.
- Clearly state the rule.

Do not include any examples or additional text.

Format:

Rule: [Your simple logical rule]
"""
    return prompt


def L1_generate_semantic_rule_prompt(existing_rules=None):
    existing_rules_text = ""
    if existing_rules:
        existing_rules_text = "\n".join(f"- {rule}" for rule in existing_rules)
        existing_rules_text = f"You have already created the following rules and should not repeat them:\n{existing_rules_text}\n"

    prompt = f"""
You are the game master for "Guess the Rule Games." {existing_rules_text}Your task is to create a **simple semantic rule** not in the list above that determines which items can be brought to the game.

- The rule should be based on a clear and common semantic property or meaning associated with the items (e.g., items related to food, items used in sports).
- Use easily recognizable semantic properties.
- Make sure the rule is something even children could guess correctly.
- Avoid abstract or complex semantic themes.
- Ensure the rule is easy to understand and apply.
- Clearly state the rule.

Do not include any examples or additional text.

Format:

Rule: [Your simple semantic rule]
"""
    return prompt