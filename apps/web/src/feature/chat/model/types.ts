export interface Message {
  id: string;
  content: string;
  role: "user" | "assistant";
  timestamp: Date;
  sources?: string[];
}

export interface ChatState {
  messages: Message[];
  isLoading: boolean;
  sessionId?: string;
}
