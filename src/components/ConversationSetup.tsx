import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useState } from "react";

const PLAYER_OPTIONS = [
  { id: "user", name: "User (Self)", description: "Play the game yourself" },
  { id: "gpt4o", name: "GPT-4o", description: "Most capable OpenAI model" },
  { id: "gpt4o-mini", name: "GPT-4o Mini", description: "Faster OpenAI model" },
  { id: "claude-3-haiku", name: "Claude 3 Haiku", description: "Fast and efficient" },
  { id: "claude-3.5-haiku", name: "Claude 3.5 Haiku", description: "Latest Anthropic model" },
];

interface ConversationSetupProps {
  onStart: (topic: string, player: string) => void;
}

export const ConversationSetup = ({ onStart }: ConversationSetupProps) => {
  const [topic, setTopic] = useState("");
  const [selectedPlayer, setSelectedPlayer] = useState("");

  const handleStart = () => {
    if (topic && selectedPlayer) {
      onStart(topic, selectedPlayer);
    }
  };

  return (
    <div className="animate-fade-in-slow space-y-6 w-full max-w-md mx-auto p-6 glass-panel">
      <div className="space-y-2">
        <label className="text-sm font-medium">Conversation Topic</label>
        <Input
          placeholder="Enter a topic for discussion..."
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          className="bg-white bg-opacity-50"
        />
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium">Select Player</label>
        <Select value={selectedPlayer} onValueChange={setSelectedPlayer}>
          <SelectTrigger className="bg-white bg-opacity-50">
            <SelectValue placeholder="Choose who will play" />
          </SelectTrigger>
          <SelectContent>
            {PLAYER_OPTIONS.map((player) => (
              <SelectItem key={player.id} value={player.id}>
                <div className="flex flex-col">
                  <span>{player.name}</span>
                  <span className="text-xs text-muted-foreground">{player.description}</span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <Button 
        onClick={handleStart}
        disabled={!topic || !selectedPlayer}
        className="w-full transition-all hover:scale-[1.02] active:scale-[0.98]"
      >
        Start Game
      </Button>
    </div>
  );
};