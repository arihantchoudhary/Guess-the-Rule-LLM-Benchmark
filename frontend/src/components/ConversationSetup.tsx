import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Info } from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useState } from "react";

const GAME_OPTIONS = [
  { id: "static_picnic", name: "Static Picnic", description: "Classic picnic game with predefined rules" },
  { id: "dynamic_picnic", name: "Dynamic Picnic", description: "Picnic game with dynamic rule and data generation" },
  { id: "code_functions_picnic", name: "Code Functions Picnic", description: "Picnic game with code functions based rules" },
  { id: "math", name: "Math", description: "Mathematical rule-based game" },
];

const PLAYER_OPTIONS = [
  { id: "user", name: "User (Self)", description: "Play the game yourself" },
  { id: "gpt-4o", name: "GPT-4o", description: "Most capable OpenAI model" },
  { id: "gpt-4o-mini", name: "GPT-4o Mini", description: "Faster OpenAI model" },
  // { id: "claude-3-haiku", name: "Claude 3 Haiku", description: "Fast and efficient" },
  // { id: "claude-3.5-haiku", name: "Claude 3.5 Haiku", description: "Latest Anthropic model" },
];

const DIFFICULTY_OPTIONS = [
  { id: "l1", name: "L1", description: "Basic difficulty" },
  { id: "l2", name: "L2", description: "Intermediate difficulty" },
  { id: "l3", name: "L3", description: "Advanced difficulty" },
];

const EXAMPLES_OPTIONS = [
  { value: "1", label: "1 Example" },
  { value: "2", label: "2 Examples" },
  { value: "3", label: "3 Examples" },
  { value: "4", label: "4 Examples" },
  { value: "5", label: "5 Examples" },
];

interface ConversationSetupProps {
  onStart: (game: string, difficulty: string, player: string, initialExamples: number) => void;
}

export const ConversationSetup = ({ onStart }: ConversationSetupProps) => {
  const [selectedGame, setSelectedGame] = useState("");
  const [difficulty, setDifficulty] = useState("");
  const [selectedPlayer, setSelectedPlayer] = useState("");
  const [initialExamples, setInitialExamples] = useState("2");

  const handleStart = () => {
    if (selectedGame && difficulty && selectedPlayer) {
      onStart(selectedGame, difficulty, selectedPlayer, parseInt(initialExamples));
    }
  };

  const isPlayerEnabled = (playerId: string) => {
    if (selectedGame === "static_picnic") return true;
    return playerId === "user";
  };

  const isDifficultyEnabled = (difficultyId: string) => {
    if (selectedGame === "code_functions_picnic") {
      return difficultyId === "l1";
    }
    return true;
  };

  const isExamplesInputEnabled = () => {
    // return selectedGame !== "dynamic_picnic";
    return true;
  };

  const renderTooltip = (children: React.ReactNode, disabled: boolean) => {
    if (!disabled) return children;

    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <div>{children}</div>
          </TooltipTrigger>
          <TooltipContent>
            <p>Option not currently enabled for this game</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  };

  return (
    <div className="animate-fade-in-slow space-y-6 w-full max-w-md mx-auto p-6 glass-panel hover:shadow-lg transition-shadow duration-300 bg-white/30 backdrop-blur-md border border-white/20">
      <h1 className="text-3xl font-bold text-center mb-8 bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
        Guess the Rule Bench
      </h1>

      <div className="space-y-2">
        <label className="text-sm font-medium">Game</label>
        <Select value={selectedGame} onValueChange={(value) => {
          setSelectedGame(value);
          if (value !== "static_picnic" && selectedPlayer !== "user") {
            setSelectedPlayer("user");
          }
          if (value === "code_functions_picnic" && difficulty !== "l1") {
            setDifficulty("l1");
          }
        }}>
          <SelectTrigger className="bg-white/50 backdrop-blur-sm hover:bg-white/80 transition-all text-left">
            <SelectValue placeholder="Select game" />
          </SelectTrigger>
          <SelectContent>
            {GAME_OPTIONS.map((option) => (
              <SelectItem key={option.id} value={option.id} className="text-left">
                <div className="flex flex-col">
                  <span>{option.name}</span>
                  <span className="text-xs text-muted-foreground">{option.description}</span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium">Difficulty</label>
        <Select value={difficulty} onValueChange={setDifficulty}>
          <SelectTrigger className="bg-white/50 backdrop-blur-sm hover:bg-white/80 transition-all text-left">
            <SelectValue placeholder="Select difficulty" />
          </SelectTrigger>
          <SelectContent>
            {DIFFICULTY_OPTIONS.map((option) => (
              renderTooltip(
                <SelectItem 
                  key={option.id} 
                  value={option.id} 
                  className={`text-left ${!isDifficultyEnabled(option.id) ? 'opacity-50 cursor-not-allowed' : ''}`}
                  disabled={!isDifficultyEnabled(option.id)}
                >
                  <div className="flex flex-col">
                    <span>{option.name}</span>
                    <span className="text-xs text-muted-foreground">{option.description}</span>
                  </div>
                </SelectItem>,
                !isDifficultyEnabled(option.id)
              )
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium">Select Player</label>
        <Select value={selectedPlayer} onValueChange={setSelectedPlayer}>
          <SelectTrigger className="bg-white/50 backdrop-blur-sm hover:bg-white/80 transition-all text-left">
            <SelectValue placeholder="Choose who will play" />
          </SelectTrigger>
          <SelectContent>
            {PLAYER_OPTIONS.map((player) => (
              renderTooltip(
                <SelectItem 
                  key={player.id} 
                  value={player.id} 
                  className={`text-left ${!isPlayerEnabled(player.id) ? 'opacity-50 cursor-not-allowed' : ''}`}
                  disabled={!isPlayerEnabled(player.id)}
                >
                  <div className="flex flex-col">
                    <span>{player.name}</span>
                    <span className="text-xs text-muted-foreground">{player.description}</span>
                  </div>
                </SelectItem>,
                !isPlayerEnabled(player.id)
              )
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium">Number of Initial Examples</label>
        <Select 
          value={initialExamples} 
          onValueChange={setInitialExamples}
          disabled={!isExamplesInputEnabled()}
        >
          <SelectTrigger className={`bg-white/50 backdrop-blur-sm hover:bg-white/80 transition-all ${!isExamplesInputEnabled() ? 'opacity-50 cursor-not-allowed' : ''}`}>
            <SelectValue placeholder="Select number of examples" />
          </SelectTrigger>
          <SelectContent>
            {EXAMPLES_OPTIONS.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <Button 
        onClick={handleStart}
        disabled={!selectedGame || !difficulty || !selectedPlayer}
        className="w-full transition-all hover:scale-[1.02] active:scale-[0.98] bg-primary/90 hover:bg-primary"
      >
        Start Game
      </Button>
    </div>
  );
};