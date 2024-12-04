# Rule Generator
def generate_rule():
    pass

# Input Generator
def generate_input(input_type):
    pass

# Dataset Creation
def create_dataset(rule, input_type, n=10):
    dataset = []
    for _ in range(n):
        input_value = generate_input(input_type)
        groundtruth = rule(input_value)
        dataset.append((input_value, groundtruth))
    return dataset



