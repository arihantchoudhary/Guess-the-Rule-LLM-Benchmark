interface ChatMessageProps {
  content: string;
  sender: string;
  index: number;
}

export const ChatMessage = ({ content, sender, index }: ChatMessageProps) => {
  return (
    <div
      className={`message-bubble ${sender === "user" ? "ml-auto" : "mr-auto"}`}
      data-sender={sender}
      style={{ animationDelay: `${index * 0.1}s` }}
    >
      <div className={`text-xs font-medium mb-1 ${sender === "user" ? "text-white/80" : "text-gray-500"}`}>
        {sender}
      </div>
      <div className="text-sm whitespace-pre-wrap">{content}</div>
    </div>
  );
};