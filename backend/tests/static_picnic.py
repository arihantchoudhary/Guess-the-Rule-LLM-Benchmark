from lib.domain.picnic.static_picnic.base import StaticGoingOnAPicnic

# Get a new object for the static picnic game
static_picnic_obj = StaticGoingOnAPicnic(
    difficulty='L1',
    num_init_examples=2
)

# Create a new game instance
static_picnic_obj.create_game_instance()

# Request more examples
static_picnic_obj.get_more_examples(n=1)
static_picnic_obj.get_more_examples(n=2)
static_picnic_obj.get_more_examples(n=3)

# Validate guess
static_picnic_obj.validate_guess(guess='Items from the category kitchen appliances')

# Get game summary
static_picnic_obj.get_game_summary()

# Load an existing game and check its summary
loaded_game = StaticGoingOnAPicnic.load_game('650499e9-a5da-4129-b426-8d6517bf65e6')
loaded_game.get_game_summary(include_rule=True)


