interface ChatMessageProps {
  content: string;
  sender: string;
  index: number;
}

export const ChatMessage = ({ content, sender, index }: ChatMessageProps) => {
  return (
    <div
      className={`message-bubble ${
        sender === "user" ? "ml-auto bg-primary/10" : "mr-auto bg-white/40"
      } animate-fade-in`}
      style={{ animationDelay: `${index * 0.1}s` }}
    >
      <div className="text-xs font-medium mb-1 text-muted-foreground">
        {sender}
      </div>
      <div className="text-sm">{content}</div>
    </div>
  );
};