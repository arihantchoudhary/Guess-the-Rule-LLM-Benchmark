import { useState } from "react";
import { useToast } from "@/components/ui/use-toast";
import { StartGamePayload } from "@/lib/api";
import { 
  startGameService, 
  getExamplesService, 
  validateGuessService, 
  loadGameService,
  streamLLMGameplay 
} from "@/services/gameService";
import { ConversationSetup } from "@/components/ConversationSetup";
import { GameLayout } from "@/components/game/GameLayout";
import { LoadGameForm } from "@/components/game/LoadGameForm";
import { GameModeSelection } from "@/components/game/GameModeSelection";

interface Message {
  id: string;
  content: string;
  sender: string;
}

interface GameDetails {
  domain: string;
  difficulty: string;
  datasetType: string;
  startTime: Date;
  status: "ongoing" | "won" | "lost";
  turnsTaken: number;
  gameId: string;
}

const Play = () => {
  const { toast } = useToast();
  const [gameMode, setGameMode] = useState<"new" | "load" | null>(null);
  const [isConversationStarted, setIsConversationStarted] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentPlayer, setCurrentPlayer] = useState("");
  const [isUserPlaying, setIsUserPlaying] = useState(false);
  const [gameDetails, setGameDetails] = useState<GameDetails>({
    domain: "",
    difficulty: "",
    datasetType: "",
    startTime: new Date(),
    status: "ongoing",
    turnsTaken: 0,
    gameId: ""
  });

  const handleStart = async (
    game: string, 
    difficulty: string, 
    player: string, 
    initialExamples: number
  ) => {
    try {
      setIsLoading(true);
      
      // Check if the player is an LLM
      const isLLMPlayer = player !== "user";
      
      if (isLLMPlayer) {
        // Handle LLM gameplay with streaming
        setIsConversationStarted(true);
        setCurrentPlayer(player);
        setIsUserPlaying(false);
        
        // Set initial game details based on selection
        setGameDetails({
          domain: game,
          difficulty,
          datasetType: "Dynamic",
          startTime: new Date(),
          status: "ongoing",
          turnsTaken: 0,
          gameId: `llm-${Date.now()}`  // Generate a temporary ID for LLM games
        });

        // Start streaming LLM gameplay
        await streamLLMGameplay(
          game,
          difficulty,
          player,
          initialExamples,
          (content: string, sender: string) => {
            setMessages(prev => [...prev, {
              id: Date.now().toString(),
              content,
              sender
            }]);
            
            // Update turns taken for user messages
            if (sender === "user") {
              setGameDetails(prev => ({
                ...prev,
                turnsTaken: prev.turnsTaken + 1
              }));
            }
          }
        );
      } else {
        // Handle regular user gameplay
        const payload: StartGamePayload = {
          game_name: game,
          difficulty,
          player,
          num_init_examples: initialExamples.toString()
        };

        const response = await startGameService(payload);

        setIsConversationStarted(true);
        setCurrentPlayer(player);
        setIsUserPlaying(true);
        
        setGameDetails({
          domain: response.domain,
          difficulty,
          datasetType: response.game_gen_type,
          startTime: new Date(response.start_time),
          status: response.status as "ongoing" | "won" | "lost",
          turnsTaken: response.turns_taken,
          gameId: response.game_uuid
        });

        const initialMessage = {
          id: Date.now().toString(),
          content: response.system_message,
          sender: "system"
        };

        setMessages([initialMessage]);
      }
    } catch (error: any) {
      console.error("Error starting game:", error);
      toast({
        variant: "destructive",
        title: "Error",
        description: error.message
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoadGame = async (gameId: string) => {
    try {
      setIsLoading(true);
      const response = await loadGameService(gameId);

      setIsConversationStarted(true);
      setCurrentPlayer("user");
      setIsUserPlaying(true);
      
      setGameDetails({
        domain: response.domain,
        difficulty: response.difficulty,
        datasetType: response.game_gen_type === "dynamic" ? "Dynamic" : "Static",
        startTime: new Date(response.start_time),
        status: response.status as "ongoing" | "won" | "lost",
        turnsTaken: response.turns_taken,
        gameId: response.game_uuid
      });

      const initialMessage: Message = {
        id: Date.now().toString(),
        content: response.system_message,
        sender: "system",
      };

      setMessages([initialMessage]);

    } catch (error: any) {
      console.error("Error loading game:", error);
      toast({
        variant: "destructive",
        title: "Error",
        description: error.message,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setIsConversationStarted(false);
    setMessages([]);
    setCurrentPlayer("");
    setIsUserPlaying(false);
    setGameMode(null);
    setGameDetails({
      domain: "",
      difficulty: "",
      datasetType: "",
      startTime: new Date(),
      status: "ongoing",
      turnsTaken: 0,
      gameId: ""
    });
  };

  const handleMessage = async (message: string) => {
    if (gameDetails.status !== "ongoing") {
      toast({
        title: "Game Over",
        description: "This game has ended. Please start a new game to continue playing.",
      });
      return;
    }

    try {
      setIsLoading(true);

      const userMessage: Message = {
        id: Date.now().toString(),
        content: message,
        sender: "user"
      };
      setMessages(prev => [...prev, userMessage]);

      let response;
      const examplesMatch = message.match(/^More (\d+) examples?$/);
      
      if (examplesMatch) {
        const numExamples = parseInt(examplesMatch[1]);
        response = await getExamplesService(gameDetails.gameId, numExamples);
      } else {
        response = await validateGuessService(gameDetails.gameId, message);
      }

      const systemMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.system_message,
        sender: "system"
      };
      setMessages(prev => [...prev, systemMessage]);

      if (response.status) {
        setGameDetails(prev => ({
          ...prev,
          status: response.status as "ongoing" | "won" | "lost",
          turnsTaken: prev.turnsTaken + 1
        }));
      }

    } catch (error: any) {
      console.error("Error handling message:", error);
      toast({
        variant: "destructive",
        title: "Error",
        description: error.message,
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (!isConversationStarted) {
    return (
      <div className="p-6 bg-gradient-to-br from-purple-50 via-white to-blue-50">
        <div className="max-w-4xl mx-auto">
          {!gameMode ? (
            <GameModeSelection onSelectMode={setGameMode} />
          ) : gameMode === "new" ? (
            <ConversationSetup onStart={handleStart} />
          ) : (
            <div className="p-4 glass-panel">
              <h2 className="text-xl font-semibold mb-4">Load Existing Game</h2>
              <LoadGameForm onLoadGame={handleLoadGame} />
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <GameLayout
      messages={messages}
      isLoading={isLoading}
      onReset={handleReset}
      isUserPlaying={isUserPlaying && gameDetails.status === "ongoing"}
      gameDetails={gameDetails}
      onSendMessage={handleMessage}
    />
  );
};

export default Play;