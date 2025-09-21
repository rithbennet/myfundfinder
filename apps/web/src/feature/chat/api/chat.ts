import { getStoredTokens } from "@/lib/auth";

const AI_API_BASE = process.env.NEXT_PUBLIC_AI_API_URL || "http://localhost:8000";

export interface ChatRequest {
  message: string;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  sources: string[];
}

export const chatApi = {
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const tokens = getStoredTokens();
    
    if (!tokens?.AccessToken) {
      throw new Error("No authentication token found");
    }

    const response = await fetch(`${AI_API_BASE}/chat/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${tokens.AccessToken}`,
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Chat request failed: ${response.statusText}`);
    }

    return response.json();
  },
};
