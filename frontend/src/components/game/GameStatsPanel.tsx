import { Clock } from "lucide-react";
import { useEffect, useState } from "react";

interface GameStatsPanelProps {
  startTime: Date;
  turnsTaken: number;
  gameStatus: "ongoing" | "won" | "lost";
}

export const GameStatsPanel = ({ startTime, turnsTaken, gameStatus }: GameStatsPanelProps) => {
  const [elapsedTime, setElapsedTime] = useState("0:00");

  useEffect(() => {
    if (gameStatus === "ongoing") {
      const interval = setInterval(() => {
        const now = new Date();
        const diff = now.getTime() - startTime.getTime();
        const minutes = Math.floor(diff / 60000);
        const seconds = Math.floor((diff % 60000) / 1000);
        setElapsedTime(`${minutes}:${seconds.toString().padStart(2, "0")}`);
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [startTime, gameStatus]);

  const formatDateTime = (date: Date) => {
    return date.toLocaleString("en-US", {
      month: "2-digit",
      day: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
  };

  return (
    <div className="glass-panel p-4 space-y-2 hover:shadow-lg transition-shadow duration-300 bg-gray-100/80 backdrop-blur-md border border-white/20">
      <h3 className="font-semibold text-lg mb-2 text-primary">Game Stats</h3>
      <div className="grid grid-cols-2 gap-2 text-sm">
        <span className="text-muted-foreground">Start Time:</span>
        <span className="font-medium">{formatDateTime(startTime)}</span>
        <span className="text-muted-foreground">Time Elapsed:</span>
        <span className="flex items-center gap-1 font-medium">
          <Clock className="w-4 h-4 text-primary" />
          {elapsedTime}
        </span>
        <span className="text-muted-foreground">Turns Taken:</span>
        <span className="font-medium">{turnsTaken}</span>
      </div>
    </div>
  );
};