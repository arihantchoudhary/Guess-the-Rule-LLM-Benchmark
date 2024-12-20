# GuessTheRuleBench

Welcome to **GuessTheRuleBench**, a dynamic benchmark designed to evaluate implicit rule deduction capabilities of Large Language Models (LLMs) through "guess-the-rule" games. This repository contains:

- The code for running the benchmark via a Python library.
- A web application demo where human user can play the games or watch LLM agents interact with the system in real-time.
- Experiment results and a research paper detailing the methodology and findings.

## High-Level System Design Diagram

Below is a high-level system design diagram that illustrates the various components, their interactions, and the overall workflow of GuessTheRuleBench:

![](/docs/final-proj-system-design.png)

## Research Paper and Demo Presentation

For a complete understanding of the methodology, experiments, and analysis, please refer below

[**Research Paper PDF**](/docs/GuessTheRuleBench.pdf)

[**Demo Presentation Video**](https://www.youtube.com/watch?v=zgnqCNjr5H4)

[**Demo Slides**](https://docs.google.com/presentation/d/1_7-yq9PsrscZz8_R5mHI-rbg5dOxJNWxV9zhrfWpCSI/edit?usp=sharing)


## System Requirements

**Python 3.9 or below** is required to run the Python library and backend services. Use a conda environment to avoid installing libraries globally:
```bash
conda create -n guess_the_rule_env python=3.9
conda activate guess_the_rule_env
```

## For Agentic Use: Running the Benchmark Python Library
The Python library provides four game classes:

- ```StaticGoingOnAPicnic()``` for the Static Picnic game
- ```DynamicGoingOnAPicnic()``` for the Dynamic Picnic game
- ```CodeFunctionsPicnic()``` for the Code Functions Picnic game
- ```MathGuessTheRuleGame()``` for the Math game

Each class exposes the following methods:

- ```create_game_instance()``` to request a new instance of the game.
- ```get_more_examples(N)``` to request N more examples.
- ```validate_guess(guess)``` to present the user's guess for validation.
- ```get_game_summary()``` to retrieve the performance summary of the current game.
- ```load_game(uuid)``` to load a previously generated game instance.

### Sample Code for Static Picnic Game:

```python
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
```

## Run the Web Application for Benchmark Demo Locally
Before starting, ensure you have your `OPENAI_API_KEY` set in the `.env` file at the root of this repository:
```makefile
OPENAI_API_KEY=your-key-here
```

### Backend
1. Navigate to the backend directory:
```bash
cd Guess-the-Rule-LLM-Benchmark/backend
```
2. Install the required libraries:
```bash
pip install -r requirements.txt
```
3. Run the backend server:
```bash
python app/main.py
```
The backend will start on http://localhost:8000. **Important:** The frontend is configured to communicate with this port only, so ensure the backend is running on port 8000.

### Frontend
1. Navigate to the frontend directory:
```bash
cd ../frontend
```
2. Install the required libraries:
```bash
npm i
```
3. Start the frontend server:
```bash
npm run dev
```
The frontend will be accessible at http://localhost:8080/. Open this URL in your browser to interact with the benchmark games, either playing them yourself or observing LLM gameplay.

## Web Application UI
Below are some screenshots showcasing the web application interface and its features:
1. **Landing Page**
![](/docs/landing-page.png)

2. **Docs Page**
![](/docs/docs.png)

3. **Game Play**

Either start a new game or load existing game using an already generated game UUID.
![](/docs/choose-gameplay.png)

Select the game configurations to start a new game.
![](/docs/start-new-game.png)

Game play UI.
![](/docs/play.png)

## Benchmark Experiment Results Screenshot
Win rate of different models across games and difficulty levels. Bold values highlight the best performances
in their respective columns.
![](/docs/evaluation-results.png)

## Feedback and Contribution
If you have any suggestions, issues, or contributions, please feel free to open an issue or submit a pull request. We appreciate your interest and support in improving GuessTheRuleBench.