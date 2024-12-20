# **GuessTheRuleBench Documentation**

## **Introduction**

**Key Features:**

- Four unique games: Static Picnic, Dynamic Picnic, Code Functions Picnic, and Math Game.
- Three difficulty levels for progressively challenging tasks.
- Open-source Python library for seamless integration.
- Web application for real-time interaction and visualization.

---

## **Quick Start**

### **Python Library**

```bash
pip install guesstherulebench

Example Usage:

from guesstherulebench import StaticGoingOnAPicnic, MathGuessTheRuleGame
game = StaticGoingOnAPicnic()
instance = game.create_game_instance(difficulty="L1", num_examples=3)
print(instance)
examples = game.get_more_examples(2)
print(examples)
result = game.validate_guess("personal care items")
print(result)  # Returns True or False
summary = game.get_game_summary()
print(summary)

Web Application
	1.	Access the Application: Open the app at [App Link].
	2.	Choose Your Game:
	•	Select from the four available games.
	•	Set difficulty level (L1, L2, L3).
	•	Decide the number of initial examples.
	3.	Play or Observe:
	•	Play the game yourself or observe LLMs guessing in real-time.
	4.	Performance Metrics:
	•	View metrics like turns taken, examples seen, and time elapsed in real-time.

Game Details

Static Picnic
	•	Objective: Deduce rules based on fixed datasets (e.g., personal care items).
	•	Data Source: Google Open Images Dataset.
	•	Difficulty Levels:
	•	L1: Single-category rules.
	•	L2: Two-category combinations.
	•	L3: Three-category combinations.

Dynamic Picnic
	•	Objective: Infer rules generated in real-time to mitigate memorization risks.
	•	Data Source: Dynamic LLM-generated examples.
	•	Difficulty Levels:
	•	L1: Attribute-based or categorical rules.
	•	L2: Logical or relational rules.
	•	L3: Multi-layered, abstract rules.

Code Functions Picnic
	•	Objective: Guess rules based on dynamically generated Python code.

Math Game
	•	Objective: Identify mathematical patterns in number sequences.
	•	Difficulty Levels:
	•	L1: Basic arithmetic operations.
	•	L2: Negative values and abrupt changes.
	•	L3: Index-dependent rules.

Evaluation Metrics
	•	Turns Taken: Total turns required to deduce the rule.
	•	Examples Seen: Number of positive examples viewed.
	•	Duration: Time taken to complete the game.

Experiment Results
	•	Best Performing Models:
	•	Claude 3 Haiku: High win rates in Static Picnic and Dynamic Picnic.
	•	GPT-4o: Strong performance in Math Game.
	•	Key Findings:
	•	Models struggled with Code Functions Picnic.
	•	Performance declined with increasing difficulty.

Contributing
	1.	Fork the repository: GitHub Repo.
	2.	Make your changes.
	3.	Submit a pull request.

Support
	•	Email: support@guesstherulebench.com
	•	GitHub Issues: Submit an Issue.

```
