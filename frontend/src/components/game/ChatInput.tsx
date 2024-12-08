import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useState } from "react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
}

export const ChatInput = ({ onSendMessage }: ChatInputProps) => {
  const [inputMode, setInputMode] = useState<"guess" | "examples">("guess");
  const [userInput, setUserInput] = useState("");
  const [exampleCount, setExampleCount] = useState("1");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputMode === "examples") {
      onSendMessage(`More ${exampleCount} examples`);
    } else if (userInput.trim()) {
      onSendMessage(userInput);
    }
    setUserInput("");
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="flex gap-4 items-center">
        <Select value={inputMode} onValueChange={(value: "guess" | "examples") => setInputMode(value)}>
          <SelectTrigger className="w-[200px] bg-white/50 backdrop-blur-sm hover:bg-white/80 transition-all">
            <SelectValue placeholder="Select input type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="guess">Make a guess</SelectItem>
            <SelectItem value="examples">Request examples</SelectItem>
          </SelectContent>
        </Select>

        {inputMode === "examples" && (
          <Select value={exampleCount} onValueChange={setExampleCount}>
            <SelectTrigger className="w-[150px] bg-white/50 backdrop-blur-sm hover:bg-white/80 transition-all">
              <SelectValue placeholder="Number of examples" />
            </SelectTrigger>
            <SelectContent>
              {[1, 2, 3, 4, 5].map((num) => (
                <SelectItem key={num} value={num.toString()}>
                  {num} example{num > 1 ? "s" : ""}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
      </div>

      {inputMode === "guess" && (
        <div className="flex gap-4">
          <Input
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="Type your guess..."
            className="flex-1 bg-white/50 backdrop-blur-sm focus:bg-white/80 transition-all"
          />
        </div>
      )}

      <Button 
        type="submit" 
        disabled={(inputMode === "guess" && !userInput.trim()) || (inputMode === "examples" && !exampleCount)}
        className="w-full transition-all hover:scale-105 active:scale-95"
      >
        {inputMode === "examples" ? `Request ${exampleCount} Example${parseInt(exampleCount) > 1 ? "s" : ""}` : "Send Guess"}
      </Button>
    </form>
  );
};