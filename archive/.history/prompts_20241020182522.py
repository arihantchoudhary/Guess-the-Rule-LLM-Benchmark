

PICNIC_RULES = {
    ...
}

def get_picnic_game(rule, ):
    if rule in PICNIC_RULES:
        rule_prompt = PICNIC_RULES.get(rule)
    prompt = f"""
    We are playing a guess the rule game. This game is called picnic. There is a hidden rule governing the game. Please give me a 
    """
    return prompt