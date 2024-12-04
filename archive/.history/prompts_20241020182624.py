

PICNIC_RULES = {
    ...
}

def get_picnic_game(rule, getExamples):
    if rule in PICNIC_RULES:
        rule_prompt = PICNIC_RULES.get(rule)
    prompt = f"""
    
    We are playing a guess the rule game. This game is called picnic. There is a hidden rule governing the game.

    {rule_prompt}

    Please try and guess the rule.
    """
    return prompt