const API_BASE_URL = 'http://localhost:8000/guess-the-rule';

export interface StartGamePayload {
  domain: string;
  difficulty: string;
  player: string;
  num_init_examples: string;
  game_gen_type: string;
}

export interface StartGameResponse {
  game_uuid: string;
  domain: string;
  difficulty: string;
  game_gen_type: string;
  status: string;
  start_time: string;
  turns_taken: number;
  system_message: string;
}

export interface GuessResponse {
  game_uuid: string;
  system_message: string;
}

export const startGame = async (payload: StartGamePayload): Promise<StartGameResponse> => {
  const response = await fetch(`${API_BASE_URL}/game`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error('Failed to start game');
  }

  return response.json();
};

export const getExamples = async (gameId: string, numExamples: number): Promise<GuessResponse> => {
  const response = await fetch(
    `${API_BASE_URL}/game/${gameId}/examples?n_examples=${numExamples}`,
    {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );

  if (!response.ok) {
    throw new Error('Failed to get examples');
  }

  return response.json();
};

export const validateGuess = async (gameId: string, guess: string): Promise<GuessResponse> => {
  const response = await fetch(`${API_BASE_URL}/game/validate_guess`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ game_id: gameId, guess }),
  });

  if (!response.ok) {
    throw new Error('Failed to validate guess');
  }

  return response.json();
};