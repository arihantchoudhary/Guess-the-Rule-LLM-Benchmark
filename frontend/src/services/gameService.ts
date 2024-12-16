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

export const streamLLMGameplay = async (
  game: string,
  difficulty: string,
  player: string,
  numInitExamples: number,
  onMessage: (content: string, sender: string) => void
) => {
  const url = new URL(`${API_BASE_URL}/llm-gameplay`);
  url.searchParams.append('game_name', game);
  url.searchParams.append('difficulty', difficulty);
  url.searchParams.append('player', player);
  url.searchParams.append('num_init_examples', numInitExamples.toString());

  const response = await fetch(url);
  if (!response.ok) throw new Error('Failed to start LLM gameplay');
  if (!response.body) throw new Error('No response body');

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  let buffer = '';

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // Split buffer into complete JSON messages
    const messages = buffer.split('\n').filter((line) => line.trim() !== '');
    while (messages.length > 0) {
      const message = messages.shift();
      try {
        const parsedMessage = JSON.parse(message);
        onMessage(parsedMessage.content, parsedMessage.sender.toLowerCase());
      } catch (err) {
        console.error("Error parsing message:", err);
      }
    }

    // Retain any incomplete data in the buffer
    buffer = messages.join('\n');
  }
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
