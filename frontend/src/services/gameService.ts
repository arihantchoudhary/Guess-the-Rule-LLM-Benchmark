import { StartGamePayload, StartGameResponse, GuessResponse } from "@/lib/api";

const API_BASE_URL = 'http://0.0.0.0:8000/guess-the-rule';

export const handleApiError = async (response: Response) => {
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'An unexpected error occurred');
  }
  return response.json();
};

export const startGameService = async (payload: StartGamePayload): Promise<StartGameResponse> => {
  const response = await fetch(`${API_BASE_URL}/game`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  
  return handleApiError(response);
};

export const getExamplesService = async (gameId: string, numExamples: number): Promise<GuessResponse> => {
  const response = await fetch(
    `${API_BASE_URL}/game/${gameId}/examples?n_examples=${numExamples}`,
    {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );
  
  return handleApiError(response);
};

export const validateGuessService = async (gameId: string, guess: string): Promise<GuessResponse> => {
  const response = await fetch(`${API_BASE_URL}/game/validate_guess`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ game_id: gameId, guess }),
  });
  
  return handleApiError(response);
};

export const loadGameService = async (gameId: string): Promise<StartGameResponse> => {
  const response = await fetch(`${API_BASE_URL}/game/${gameId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  
  return handleApiError(response);
};