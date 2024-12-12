import time
from typing import Any, Dict, List, Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid

import requests

# Import your existing functions
from dynamic_rule_generator import (
    request_game_instance,
    request_more_examples,
    request_guess_validation,
    get_llm_response
)

app = FastAPI()

BASE_URL = "http://localhost:8000"
CREATE_GAME_URL = f"{BASE_URL}/create_game/"
GET_MORE_EXAMPLES_URL = f"{BASE_URL}/examples/"
VALIDATE_GUESS_URL = f"{BASE_URL}/validate_guess/"

# Model for creating a game instance
class GameRequest(BaseModel):
    domain: str = None
    difficulty: str = None
    init_examples: str = None
    use_llm: bool = False

# Model for guess validation
class GuessRequest(BaseModel):
    game_id: uuid.UUID
    guess: str

@app.post("/create_game/")
async def create_game(game_request: GameRequest):
    """Create a new game instance."""
    try:
        game_id = request_game_instance(
            domain=game_request.domain,
            difficulty=game_request.difficulty,
            init_examples=game_request.init_examples,
            use_llm=game_request.use_llm
        )
        return {"game_id": game_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/examples/{game_id}")
async def get_more_examples(game_id: Union[uuid.UUID, str], n_examples: int = 5):
    """Get more examples from the game."""
    if type(game_id) is str:
        game_id = uuid.UUID(game_id)
    print('dsfsdfsfssdf')
    try:
        examples = request_more_examples(game_id, n_examples=n_examples)
        return {"examples": examples}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/validate_guess/")
async def validate_guess(guess_request: GuessRequest):
    """Validate a guess against the game instance."""
    try:
        is_correct = request_guess_validation(guess_request.game_id, guess_request.guess)
        return {"is_correct": is_correct}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

#region benchmark API call
@app.post("/benchmark")
def benchmark_models(
    valid_difficulties: List[str],
    max_turns: List[int],
    total_iterations: int,
    llm_models: Dict[str, List[str]],
) -> List[Dict[str, Any]]:
    results = []

    def create_game(difficulty: str):
        response = requests.post(CREATE_GAME_URL, json={"difficulty": difficulty})
        if response.status_code == 200:
            return response.json()
        raise HTTPException(status_code=response.status_code, detail=response.text)

    def get_more_examples(game_id: str, num_examples: int):
        url = GET_MORE_EXAMPLES_URL + game_id
        # response = requests.post(GET_MORE_EXAMPLES_URL, json={"game_id": game_id, "num_examples": num_examples})
        response = requests.get(
            GET_MORE_EXAMPLES_URL + game_id,
            params={'n_examples': 5},
            headers={'accept': 'application/json'}
        )
        if response.status_code == 200:
            return response.json()
        raise HTTPException(status_code=response.status_code, detail=response.text)

    def validate_guess(game_id: str, guess: str):
        response = requests.post(VALIDATE_GUESS_URL, json={"game_id": game_id, "guess": guess})
        if response.status_code == 200:
            return response.json()
        raise HTTPException(status_code=response.status_code, detail=response.text)

    for platform in llm_models:
        for model in llm_models[platform]:
            for difficulty in valid_difficulties:
                for curr_max_turns in max_turns:
                    for iteration in range(total_iterations):
                        start_time = time.time()
                        try:
                            game = create_game(difficulty)
                            game_id = game["game_id"]

                            turns = 0
                            history = {"positives": set(), "negatives": set()}
                            llm_won = False
                            total_pos_examples_shown = 0
                            total_neg_examples_shown = 0
                            num_examples = 2
                            while turns < curr_max_turns:
                                turns += 1
                                examples = get_more_examples(game_id, num_examples)
                                print(examples)
                                positives = [item[0] for item in examples['examples'] if item[1] is True]
                                negatives = [item[0] for item in examples['examples'] if item[1] is False]
                                total_pos_examples_shown += len(positives)
                                total_neg_examples_shown += len(negatives)
                                history["positives"].update(positives)
                                history["negatives"].update(negatives)

                                llm_action = "guess: rule_example"  # Replace with LLM decision-making logic

                                if "guess:" in llm_action:
                                    guess = llm_action.replace("guess:", "").strip()
                                    validation = validate_guess(game_id, guess)
                                    if validation["correct"]:
                                        llm_won = True
                                        break
                                elif "more" in llm_action:
                                    num_examples += int(llm_action.split()[-1])  # Adjust based on LLM input
                                else:
                                    break

                            end_time = time.time()
                            duration = end_time - start_time
                            results.append({
                                "Model": model,
                                "Win": 1 if llm_won else 0,
                                "Difficulty": difficulty,
                                "Max Turns": curr_max_turns,
                                "Iteration": iteration + 1,
                                "Rule": rule_description,
                                "Turns Taken": turns,
                                "Duration (s)": round(duration, 2),
                                "Positive Examples Shown": total_pos_examples_shown,
                                "Negative Examples Shown": total_neg_examples_shown,
                            })
                        except Exception as e:
                            print(f"Error during benchmark: {e}")

    return results
#endregion


# Run the application (only if running directly, otherwise use Uvicorn from CLI)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)