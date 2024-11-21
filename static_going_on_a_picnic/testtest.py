from final_base import StaticGoingOnAPicnic

# Creating a new game instance
game = StaticGoingOnAPicnic(domain='natural_language', difficulty='L1', num_init_examples=3, game_gen_type='static')
game.create_game_instance()
print(game.get_game_summary())
# Save the game (already done in create_game_instance)

# Later on, load the game using its UUID
loaded_game = StaticGoingOnAPicnic.load_game(str(game.uuid))
print(loaded_game.get_game_summary(include_rule=True))

# Continue playing
more_examples = loaded_game.get_more_examples(n=1)
print(more_examples)
guess_result = loaded_game.validate_guess(guess='is it a flying insect')
print(guess_result)
print(loaded_game.get_game_summary(include_rule=True))


# Again load the game using its UUID
loaded_game = StaticGoingOnAPicnic.load_game('650499e9-a5da-4129-b426-8d6517bf65e6')
# Continue playing
more_examples = loaded_game.get_more_examples(n=2)
print(more_examples)
guess_result = loaded_game.validate_guess(guess='marine invertebrates')
print(guess_result)
print(loaded_game.get_game_summary(include_rule=True))