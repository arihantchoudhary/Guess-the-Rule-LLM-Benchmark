

user_input = "ur a bitch lmao"


prompt = (
            f"You are currently playing a Guess The Rule Game. It is a game where there is a game master and players. "
            f"In order to win the game, players must correctly figure out the underlying rule of the game.\n\n"
            f"The players can make guesses to the game master.\n"
            f"The players can give the game master two different kinds of guesses:\n"
            f"    1. giving an example (or examples) fit the rule\n"
            f"    2. giving their guess of the actual rule.\n\n"
            f"Take a look at the player's guess: \"{user_input}\".\n\n"
            f"Your task is to classify if the player's guess is an example or a guess of the rule itself.\n\n"
            f"Please respond with either \"example\" for example guess (or guesses), or (actual) for a guess of the actual rule.\n"
            f"Do not provide any additional explanation or text.\n\n"
            f"Format:\n\n"
            f"[your final answer]"
        )
print(prompt)