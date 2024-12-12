interface ChatMessageProps {
  content: string;
  sender: string;
  index: number;
}

export const ChatMessage = ({ content, sender, index }: ChatMessageProps) => {
  return (
    <div
      className={`message-bubble ${
        sender === "user" 
          ? "ml-auto bg-[#9b87f5] text-white" 
          : "mr-auto bg-gray-200/90"
      } animate-fade-in`}
      style={{ animationDelay: `${index * 0.1}s` }}
    >
      <div className={`text-xs font-medium mb-1 ${sender === "user" ? "text-white/80" : "text-gray-500"}`}>
        {sender}
      </div>
      <div className="text-sm">{content}</div>
    </div>
  );
};