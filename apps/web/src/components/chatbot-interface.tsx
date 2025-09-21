"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import { ScrollArea } from "~/components/ui/scroll-area";
import { Badge } from "~/components/ui/badge";
import { Separator } from "~/components/ui/separator";
import { RotateCcw, Send, Bot, User, Loader2, Sparkles } from "lucide-react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: string[];
}

const AI_API_BASE = "http://localhost:8000";

const getCookie = (name: string): string | null => {
  if (typeof document === "undefined") return null;
  
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    return parts.pop()?.split(';').shift() || null;
  }
  return null;
};

const getStoredTokens = () => {
  if (typeof window === "undefined") return null;

  try {
    // Check cookies first (like the working chat-test)
    const authToken = getCookie("auth-token");
    if (authToken) {
      return {
        AccessToken: authToken,
        IdToken: getCookie("id-token") || "",
        RefreshToken: getCookie("refresh-token") || "",
      };
    }

    // Fallback to localStorage
    const tokens = localStorage.getItem("cognito_tokens");
    if (tokens) {
      return JSON.parse(tokens);
    }

    const accessToken = localStorage.getItem("accessToken");
    if (accessToken) {
      return {
        AccessToken: accessToken,
        IdToken: localStorage.getItem("idToken") || "",
        RefreshToken: localStorage.getItem("refreshToken") || "",
      };
    }

    return null;
  } catch {
    return null;
  }
};

const formatMessage = (content: string) => {
  // Enhanced formatting for better readability
  let formatted = content
    // Headers
    .replace(/^### (.+)$/gm, '<h3 class="text-lg font-semibold text-gray-800 mt-4 mb-2 border-b border-gray-200 pb-1">$1</h3>')
    .replace(/^## (.+)$/gm, '<h2 class="text-xl font-bold text-gray-900 mt-4 mb-3">$2</h2>')
    // Bold text
    .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>')
    // Numbered lists with better styling
    .replace(/^(\d+)\.\s\*\*(.*?)\*\*$/gm, '<div class="flex items-start gap-3 my-3 p-3 bg-blue-50 rounded-lg border-l-4 border-blue-400"><span class="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-medium flex-shrink-0 mt-0.5">$1</span><div class="flex-1"><strong class="text-blue-900 font-semibold">$2</strong></div></div>')
    // Regular numbered lists
    .replace(/^(\d+)\.\s(.+)$/gm, '<div class="flex items-start gap-2 my-2"><span class="bg-gray-100 text-gray-700 rounded-full w-6 h-6 flex items-center justify-center text-sm font-medium flex-shrink-0 mt-0.5">$1</span><span class="flex-1">$2</span></div>')
    // Bullet points
    .replace(/^[\-\*]\s(.+)$/gm, '<div class="flex items-start gap-2 my-1"><span class="text-blue-500 mt-1.5 w-1.5 h-1.5 bg-blue-500 rounded-full flex-shrink-0"></span><span class="flex-1">$1</span></div>')
    // Amount highlighting
    .replace(/(RM[\d,]+(?:\.\d{2})?(?:\s?(?:million|thousand|k))?)/gi, '<span class="bg-green-100 text-green-800 px-2 py-0.5 rounded font-medium">$1</span>')
    // Line breaks
    .replace(/\n/g, '<br>');

  return formatted;
};

const suggestedPrompts = [
  "What digital grants are available?",
  "Tell me about SME automation grants",
  "Tourism funding options",
  "Green technology grants",
  "Export grants for my business"
];

export function ChatbotInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "👋 **Welcome to MyFundFinder!**\n\nI'm your AI funding assistant. I can help you find grants, understand eligibility requirements, and guide you through application processes.\n\n**Ready to get started?** Try one of the suggestions below or ask me anything about funding opportunities!"
    }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (messageText?: string) => {
    const message = messageText || input;
    if (!message.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: message
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const tokens = getStoredTokens();
      
      if (!tokens?.AccessToken) {
        throw new Error("Please sign in to use the chat feature");
      }

      const response = await fetch(`${AI_API_BASE}/chat/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${tokens.AccessToken}`,
        },
        body: JSON.stringify({ message })
      });

      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }

      const data = await response.json();
      
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.response,
        sources: data.sources
      };
      
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `❌ **Connection Error**\n\nI'm having trouble connecting. Please check:\n• You're signed in\n• Server is running\n\nTry again in a moment.`
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await sendMessage();
  };

  const restartChat = () => {
    setMessages([
      {
        id: "welcome-" + Date.now(),
        role: "assistant",
        content: "👋 **Chat restarted!**\n\nI'm ready to help you find funding opportunities. What would you like to know about grants and funding?"
      }
    ]);
    setInput("");
  };

  const showSuggestions = messages.length <= 1;

  return (
    <div className="max-w-4xl mx-auto">
      <Card className="h-[700px] flex flex-col shadow-lg">
        <CardHeader className="border-b bg-gradient-to-r from-blue-50 to-indigo-50 flex-shrink-0">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <div className="bg-blue-500 p-2 rounded-full">
                <Bot className="h-5 w-5 text-white" />
              </div>
              <div>
                <span className="text-xl">MyFundFinder Assistant</span>
                <div className="text-sm text-gray-600 font-normal flex items-center gap-1">
                  <Sparkles className="h-3 w-3" />
                  AI-powered grant recommendations
                </div>
              </div>
            </CardTitle>
            <Button 
              onClick={restartChat}
              variant="outline" 
              size="sm"
              className="flex items-center gap-2"
            >
              <RotateCcw className="h-4 w-4" />
              Restart
            </Button>
          </div>
        </CardHeader>
        
        <CardContent className="flex-1 flex flex-col p-0 min-h-0">
          {/* Messages Area - Fixed height with scroll */}
          <div className="flex-1 overflow-hidden">
            <ScrollArea className="h-full">
              <div className="p-4 space-y-4">
                {messages.map((message) => (
                  <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                    <div className="flex items-start gap-3 max-w-[85%]">
                      {message.role === "assistant" && (
                        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-100 text-gray-600">
                          <Bot className="h-4 w-4" />
                        </div>
                      )}
                      <div
                        className={`rounded-2xl px-4 py-3 ${
                          message.role === "user"
                            ? "bg-blue-500 text-white"
                            : "bg-gray-50 border"
                        }`}
                      >
                        {message.role === "assistant" ? (
                          <div 
                            className="prose prose-sm max-w-none text-gray-800"
                            dangerouslySetInnerHTML={{ 
                              __html: formatMessage(message.content) 
                            }}
                          />
                        ) : (
                          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                        )}
                        
                        {message.sources && message.sources.length > 0 && (
                          <div className="mt-3 pt-2 border-t border-gray-200">
                            <div className="text-xs text-gray-500 mb-1">Sources:</div>
                            <div className="flex flex-wrap gap-1">
                              {message.sources.map((source, index) => (
                                <Badge key={index} variant="secondary" className="text-xs">
                                  {source}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                      {message.role === "user" && (
                        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-500 text-white">
                          <User className="h-4 w-4" />
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="flex items-start gap-3">
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-100">
                        <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
                      </div>
                      <div className="bg-gray-50 border rounded-2xl px-4 py-3">
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <div className="flex space-x-1">
                            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                          </div>
                          <span>Analyzing your request...</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>
            </ScrollArea>
          </div>
          
          {/* Suggested Prompts */}
          {showSuggestions && (
            <div className="px-4 pb-2 flex-shrink-0">
              <div className="text-sm text-gray-600 mb-2">💡 Try these questions:</div>
              <div className="flex flex-wrap gap-2">
                {suggestedPrompts.map((prompt, idx) => (
                  <Button
                    key={idx}
                    variant="outline"
                    size="sm"
                    onClick={() => sendMessage(prompt)}
                    className="text-xs h-8 hover:bg-blue-50 hover:border-blue-300"
                    disabled={isLoading}
                  >
                    {prompt}
                  </Button>
                ))}
              </div>
              <Separator className="mt-3" />
            </div>
          )}
          
          {/* Input Area - Fixed at bottom */}
          <div className="border-t bg-white p-4 flex-shrink-0">
            <form onSubmit={handleSubmit} className="flex gap-3">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about grants, funding opportunities, eligibility requirements..."
                disabled={isLoading}
                className="flex-1 rounded-full border-gray-200 focus:border-blue-500 focus:ring-blue-500"
              />
              <Button 
                type="submit" 
                disabled={isLoading || !input.trim()}
                className="rounded-full bg-blue-500 hover:bg-blue-600 px-6"
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </form>
            <div className="text-xs text-gray-500 mt-2 text-center">
              Press Enter to send • Shift+Enter for new line
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
