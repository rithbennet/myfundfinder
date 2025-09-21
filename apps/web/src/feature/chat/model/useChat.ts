import { useState } from "react";
import { chatApi, type ChatRequest } from "../api/chat";
import type { Message, ChatState } from "./types";

export const useChat = () => {
  const [state, setState] = useState<ChatState>({
    messages: [],
    isLoading: false,
  });

  const sendMessage = async (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      role: "user",
      timestamp: new Date(),
    };

    setState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isLoading: true,
    }));

    try {
      const request: ChatRequest = {
        message: content,
      };

      const response = await chatApi.sendMessage(request);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.response,
        role: "assistant",
        timestamp: new Date(),
        sources: response.sources,
      };

      setState(prev => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
        isLoading: false,
        sessionId: response.session_id,
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
      }));
      throw error;
    }
  };

  return {
    ...state,
    sendMessage,
  };
};
