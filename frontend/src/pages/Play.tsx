import { ConversationSetup } from "@/components/ConversationSetup";
import { ConversationDisplay } from "@/components/ConversationDisplay";
import { useState } from "react";
import { useToast } from "@/components/ui/use-toast";
import { startGameService, getExamplesService, validateGuessService } from "@/services/gameService";
import { StartGamePayload } from "@/lib/api";

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
  const [isConversationStarted, setIsConversationStarted] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentPlayer, setCurrentPlayer] = useState<string>("");
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
    domain: string, 
    difficulty: string, 
    player: string, 
    initialExamples: number, 
    isDynamic: boolean
  ) => {
    try {
      setIsLoading(true);
      const payload: StartGamePayload = {
        domain,
        difficulty,
        player,
        num_init_examples: initialExamples.toString(),
        game_gen_type: isDynamic ? "dynamic" : "static"
      };

      const response = await startGameService(payload);

      setIsConversationStarted(true);
      setCurrentPlayer(player);
      setIsUserPlaying(player === "user");
      
      setGameDetails({
        domain,
        difficulty,
        datasetType: isDynamic ? "Dynamic" : "Static",
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
      console.error("Error starting game:", error);
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
      
      const systemErrorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: error.message,
        sender: "system"
      };
      setMessages(prev => [...prev, systemErrorMessage]);
      
      toast({
        variant: "destructive",
        title: "Error",
        description: error.message,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-6 bg-gradient-to-br from-purple-50 via-white to-blue-50">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-center mb-8 bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
          Guess the Rule Game
        </h1>
        {!isConversationStarted ? (
          <ConversationSetup onStart={handleStart} />
        ) : (
          <ConversationDisplay
            messages={messages}
            isLoading={isLoading}
            onReset={handleReset}
            isUserPlaying={isUserPlaying && gameDetails.status === "ongoing"}
            gameDetails={gameDetails}
            onSendMessage={handleMessage}
          />
        )}
      </div>
    </div>
  );
};

export default Play;