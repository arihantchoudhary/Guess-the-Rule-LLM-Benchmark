import { useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Copy } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { Input } from "@/components/ui/input";
import { useState } from "react";

interface Message {
  id: string;
  content: string;
  sender: string;
}

interface ConversationDisplayProps {
  messages: Message[];
  isLoading: boolean;
  onReset: () => void;
  isUserPlaying: boolean;
}

export const ConversationDisplay = ({ 
  messages, 
  isLoading, 
  onReset,
  isUserPlaying 
}: ConversationDisplayProps) => {
  const { toast } = useToast();
  const bottomRef = useRef<HTMLDivElement>(null);
  const [userInput, setUserInput] = useState("");

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

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

    // TODO: Implement message sending logic
    console.log("Sending message:", userInput);
    setUserInput("");
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
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
          Reset
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