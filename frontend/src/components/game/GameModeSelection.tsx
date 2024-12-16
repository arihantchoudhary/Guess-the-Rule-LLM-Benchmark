import { Button } from "@/components/ui/button";

interface GameModeSelectionProps {
  onSelectMode: (mode: "new" | "load") => void;
}

export const GameModeSelection = ({ onSelectMode }: GameModeSelectionProps) => {
  return (
    <div className="min-h-[80vh] flex items-center justify-center">
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-center mb-8 bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
          Guess the Rule Bench
        </h1>
        <div className="flex flex-col items-center gap-4">
          <Button onClick={() => onSelectMode("new")} size="lg" className="w-64">
            Start New Game
          </Button>
          <Button onClick={() => onSelectMode("load")} variant="outline" size="lg" className="w-64">
            Load Existing Game
          </Button>
        </div>
      </div>
    </div>
  );
};