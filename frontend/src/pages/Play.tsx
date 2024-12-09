import { ConversationSetup } from "@/components/ConversationSetup";
import { ConversationDisplay } from "@/components/ConversationDisplay";
import { useState } from "react";
import { startGame, getExamples, validateGuess } from "@/lib/api";
import { useToast } from "@/components/ui/use-toast";

console.log('Hello, world!');

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
      console.log("Starting game with params:", { domain, difficulty, player, initialExamples, isDynamic });
      setIsLoading(true);
      const response = await startGame({
        domain,
        difficulty,
        player,
        num_init_examples: initialExamples.toString(),
        game_gen_type: isDynamic ? "dynamic" : "static"
      });

      console.log("Game start response:", response);

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

      console.log("Setting initial message:", initialMessage);
      setMessages([initialMessage]);

    } catch (error) {
      console.error("Error starting game:", error);
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to start the game. Please try again.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    console.log("Resetting game state");
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
    try {
      console.log("Handling message:", message);
      setIsLoading(true);

      // Add user message to chat
      const userMessage: Message = {
        id: Date.now().toString(),
        content: message,
        sender: "user"
      };
      console.log("Adding user message:", userMessage);
      setMessages(prev => [...prev, userMessage]);

      let response;
      // Check if the message is requesting examples
      const examplesMatch = message.match(/^More (\d+) examples?$/);
      
      if (examplesMatch) {
        const numExamples = parseInt(examplesMatch[1]);
        console.log("Requesting examples:", numExamples);
        response = await getExamples(gameDetails.gameId, numExamples);
      } else {
        console.log("Validating guess:", message);
        response = await validateGuess(gameDetails.gameId, message);
      }

      console.log("Backend response:", response);

      // Add system response to chat
      const systemMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.system_message,
        sender: "system"
      };
      console.log("Adding system message:", systemMessage);
      setMessages(prev => [...prev, systemMessage]);

      setGameDetails(prev => ({
        ...prev,
        turnsTaken: prev.turnsTaken + 1
      }));

    } catch (error) {
      console.error("Error handling message:", error);
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to process your message. Please try again.",
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
            isUserPlaying={isUserPlaying}
            gameDetails={gameDetails}
            onSendMessage={handleMessage}
          />
        )}
      </div>
    </div>
  );
};

export default Play;