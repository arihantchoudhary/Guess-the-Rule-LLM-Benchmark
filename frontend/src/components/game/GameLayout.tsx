import { ConversationDisplay } from "@/components/ConversationDisplay";

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

interface GameLayoutProps {
  messages: Message[];
  isLoading: boolean;
  onReset: () => void;
  isUserPlaying: boolean;
  gameDetails: GameDetails;
  onSendMessage: (message: string) => void;
}

export const GameLayout = ({
  messages,
  isLoading,
  onReset,
  isUserPlaying,
  gameDetails,
  onSendMessage,
}: GameLayoutProps) => {
  return (
    <div className="p-6 bg-gradient-to-br from-purple-50 via-white to-blue-50">
      <ConversationDisplay
        messages={messages}
        isLoading={isLoading}
        onReset={onReset}
        isUserPlaying={isUserPlaying}
        gameDetails={gameDetails}
        onSendMessage={onSendMessage}
      />
    </div>
  );
};