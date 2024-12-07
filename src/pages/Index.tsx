import { useState, useEffect } from "react";
import { ConversationSetup } from "@/components/ConversationSetup";
import { ConversationDisplay } from "@/components/ConversationDisplay";
import { Card, CardContent } from "@/components/ui/card";
import { MessageSquare, RefreshCw, List } from "lucide-react";
import { Progress } from "@/components/ui/progress";

interface Message {
  id: string;
  content: string;
  sender: string;
}

const MOCK_RESPONSES: { [key: string]: string[] } = {
  gpt4: [
    "Let me analyze this systematically. Is it related to objects being alive?",
    "Interesting. Could the rule involve the number of syllables?",
    "Based on previous responses, I hypothesize the rule involves consonants.",
  ],
  claude: [
    "I notice a pattern in the accepted items. Does it involve their properties?",
    "Let me test my understanding. Would a 'book' be allowed?",
    "I'm starting to see a connection. Is it about the first letter?",
  ],
  llama: [
    "What an intriguing puzzle! Could temperature be relevant?",
    "I'm exploring different angles. Would 'sunshine' be permitted?",
    "This reminds me of word patterns. Is it about vowels?",
  ],
  palm: [
    "Is size a factor in this rule?",
    "Would color make a difference here?",
    "Could the rule involve time-related aspects?",
  ],
};

const getLLMName = (id: string) => {
  const names: { [key: string]: string } = {
    gpt4: "GPT-4",
    claude: "Claude",
    llama: "LLaMA",
    palm: "PaLM",
  };
  return names[id] || id;
};

const Index = () => {
  const [isConversationStarted, setIsConversationStarted] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentParticipants, setCurrentParticipants] = useState<string[]>([]);
  const [currentSpeakerIndex, setCurrentSpeakerIndex] = useState(0);
  const [turnCount, setTurnCount] = useState(0);
  const [score, setScore] = useState(0);

  const simulateResponse = async (sender: string) => {
    setIsLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 1500));
    const responses = MOCK_RESPONSES[sender];
    const randomResponse = responses[Math.floor(Math.random() * responses.length)];
    
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now().toString(),
        content: randomResponse,
        sender: getLLMName(sender),
      },
    ]);
    setIsLoading(false);
    setTurnCount((prev) => prev + 1);
    setScore((prev) => prev + Math.random() * 20); // Simulated score increase
    
    setCurrentSpeakerIndex((prevIndex) => (prevIndex + 1) % 2);
  };

  useEffect(() => {
    if (isConversationStarted && !isLoading && currentParticipants.length === 2) {
      const timeoutId = setTimeout(() => {
        simulateResponse(currentParticipants[currentSpeakerIndex]);
      }, 2000);

      return () => clearTimeout(timeoutId);
    }
  }, [isConversationStarted, isLoading, messages, currentParticipants, currentSpeakerIndex]);

  const handleStart = async (topic: string, participants: string[]) => {
    setCurrentParticipants(participants);
    setIsConversationStarted(true);
    setCurrentSpeakerIndex(0);
    setTurnCount(0);
    setScore(0);
    setMessages([
      {
        id: Date.now().toString(),
        content: `Let's play a guess-the-rule game about: ${topic}`,
        sender: getLLMName(participants[0]),
      },
    ]);
  };

  const handleReset = () => {
    setIsConversationStarted(false);
    setMessages([]);
    setCurrentParticipants([]);
    setCurrentSpeakerIndex(0);
    setTurnCount(0);
    setScore(0);
  };

  return (
    <div className="min-h-screen p-6 bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8 animate-fade-in-slow">
          <h1 className="text-4xl font-bold mb-4">Guess the Rule Game</h1>
          <p className="text-muted-foreground">
            Test LLM agents with interactive rule-guessing challenges
          </p>
        </div>

        {isConversationStarted && (
          <div className="mb-6 grid grid-cols-3 gap-4">
            <Card className="p-4 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-primary" />
                <span className="font-medium">Messages</span>
              </div>
              <span className="text-lg font-bold">{messages.length}</span>
            </Card>

            <Card className="p-4 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <List className="w-5 h-5 text-primary" />
                <span className="font-medium">Turns</span>
              </div>
              <span className="text-lg font-bold">{turnCount}</span>
            </Card>

            <Card className="p-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-medium">Score</span>
                  <span className="text-sm text-muted-foreground">{Math.round(score)}%</span>
                </div>
                <Progress value={score} className="h-2" />
              </div>
            </Card>
          </div>
        )}

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

export default Index;