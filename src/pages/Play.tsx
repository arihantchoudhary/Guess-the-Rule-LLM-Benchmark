import { ConversationSetup } from "@/components/ConversationSetup";
import { ConversationDisplay } from "@/components/ConversationDisplay";
import { useState } from "react";

interface Message {
  id: string;
  content: string;
  sender: string;
}

const Play = () => {
  const [isConversationStarted, setIsConversationStarted] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleStart = (topic: string, participants: string[]) => {
    setIsConversationStarted(true);
    setMessages([
      {
        id: Date.now().toString(),
        content: `Let's play a guess-the-rule game about: ${topic}`,
        sender: participants[0],
      },
    ]);
  };

  const handleReset = () => {
    setIsConversationStarted(false);
    setMessages([]);
  };

  return (
    <div className="min-h-screen p-6 bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-center mb-8">
          Guess the Rule Game
        </h1>
        {!isConversationStarted ? (
          <ConversationSetup onStart={handleStart} />
        ) : (
          <ConversationDisplay
            messages={messages}
            isLoading={isLoading}
            onReset={handleReset}
          />
        )}
      </div>
    </div>
  );
};

export default Play;