import { useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Copy, Clock, RotateCcw } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { Input } from "@/components/ui/input";
import { useState } from "react";

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
}

interface ConversationDisplayProps {
  messages: Message[];
  isLoading: boolean;
  onReset: () => void;
  isUserPlaying: boolean;
  gameDetails: GameDetails;
}

export const ConversationDisplay = ({ 
  messages, 
  isLoading, 
  onReset,
  isUserPlaying,
  gameDetails
}: ConversationDisplayProps) => {
  const { toast } = useToast();
  const bottomRef = useRef<HTMLDivElement>(null);
  const [userInput, setUserInput] = useState("");
  const [elapsedTime, setElapsedTime] = useState("0:00");

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date();
      const diff = now.getTime() - gameDetails.startTime.getTime();
      const minutes = Math.floor(diff / 60000);
      const seconds = Math.floor((diff % 60000) / 1000);
      setElapsedTime(`${minutes}:${seconds.toString().padStart(2, '0')}`);
    }, 1000);

    return () => clearInterval(interval);
  }, [gameDetails.startTime]);

  const copyConversation = () => {
    const text = messages
      .map((msg) => `${msg.sender}: ${msg.content}`)
      .join("\n\n");
    navigator.clipboard.writeText(text);
    toast({
      description: "Conversation copied to clipboard",
      duration: 2000,
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!userInput.trim()) return;
    console.log("Sending message:", userInput);
    setUserInput("");
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "ongoing":
        return "text-blue-600";
      case "won":
        return "text-green-600";
      case "lost":
        return "text-red-600";
      default:
        return "text-gray-600";
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Game Details Panel */}
        <div className="glass-panel p-4 space-y-2">
          <h3 className="font-semibold text-lg mb-2">Game Details</h3>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <span className="text-muted-foreground">Domain:</span>
            <span>{gameDetails.domain}</span>
            <span className="text-muted-foreground">Difficulty:</span>
            <span>{gameDetails.difficulty}</span>
            <span className="text-muted-foreground">Dataset:</span>
            <span>{gameDetails.datasetType}</span>
            <span className="text-muted-foreground">Status:</span>
            <span className={`font-medium ${getStatusColor(gameDetails.status)}`}>
              {gameDetails.status.charAt(0).toUpperCase() + gameDetails.status.slice(1)}
            </span>
          </div>
        </div>

        {/* Game Stats Panel */}
        <div className="glass-panel p-4 space-y-2">
          <h3 className="font-semibold text-lg mb-2">Game Stats</h3>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <span className="text-muted-foreground">Start Time:</span>
            <span>{gameDetails.startTime.toLocaleTimeString()}</span>
            <span className="text-muted-foreground">Time Elapsed:</span>
            <span className="flex items-center gap-1">
              <Clock className="w-4 h-4" />
              {elapsedTime}
            </span>
            <span className="text-muted-foreground">Turns Taken:</span>
            <span>{gameDetails.turnsTaken}</span>
          </div>
        </div>
      </div>

      <div className="min-h-[400px] max-h-[600px] overflow-y-auto p-6 glass-panel space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message-bubble ${
              message.sender === "user" ? "ml-auto" : "mr-auto"
            }`}
          >
            <div className="text-xs font-medium mb-1 text-muted-foreground">
              {message.sender}
            </div>
            <div className="text-sm">{message.content}</div>
          </div>
        ))}
        {isLoading && (
          <div className="message-bubble mr-auto">
            <div className="loading-dots">
              <div></div>
              <div></div>
              <div></div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {isUserPlaying && (
        <form onSubmit={handleSubmit} className="flex gap-4">
          <Input
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="Type your guess..."
            className="flex-1"
          />
          <Button type="submit" disabled={!userInput.trim()}>
            Send
          </Button>
        </form>
      )}

      <div className="flex justify-between gap-4">
        <Button
          variant="outline"
          onClick={onReset}
          className="transition-all hover:scale-[1.02] active:scale-[0.98]"
        >
          <RotateCcw className="w-4 h-4 mr-2" />
          Reset Game
        </Button>
        <Button
          variant="outline"
          onClick={copyConversation}
          className="transition-all hover:scale-[1.02] active:scale-[0.98]"
        >
          <Copy className="w-4 h-4 mr-2" />
          Copy Conversation
        </Button>
      </div>
    </div>
  );
};