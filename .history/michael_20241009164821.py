import random
import string

# Rule Generator
def generate_rule():
    def rule(word):
        for i in range(len(word) - 1):
            if ord(word[i].lower()) + 1 == ord(word[i+1].lower()):
                return True
        return False
    return rule

# Input Generator
def generate_input(input_type):
    if input_type == "word":
        word_length = random.randint(3, 10)
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(word_length))
    else:
        raise ValueError("Unsupported input type")

# Dataset Creation
def create_dataset(rule, input_type, n=10):
    dataset = []
    for _ in range(n):
        input_value = generate_input(input_type)
        groundtruth = rule(input_value)
        dataset.append((input_value, groundtruth))
    return dataset

if __name__ == "__main__":
    rule = generate_rule()

    # Create the dataset
    dataset = create_dataset(rule, "word", n=20)

    # Print the dataset
    print("Dataset:")
    for word, is_valid in dataset:
        print(f"Word: {word}, Follows rule: {is_valid}")