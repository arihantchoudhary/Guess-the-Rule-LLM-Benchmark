import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/use-toast";

interface LoadGameFormProps {
  onLoadGame: (gameId: string) => Promise<void>;
}

export const LoadGameForm = ({ onLoadGame }: LoadGameFormProps) => {
  const [gameId, setGameId] = useState("");
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!gameId.trim()) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "Please enter a game ID",
      });
      return;
    }
    await onLoadGame(gameId);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="flex gap-4">
        <Input
          value={gameId}
          onChange={(e) => setGameId(e.target.value)}
          placeholder="Enter Game ID"
          className="flex-1"
        />
        <Button type="submit">Load Game</Button>
      </div>
    </form>
  );
};