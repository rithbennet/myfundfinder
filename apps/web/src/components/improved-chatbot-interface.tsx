"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "~/components/ui/button"
import { Input } from "~/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/components/ui/card"
import { Badge } from "~/components/ui/badge"
import { Separator } from "~/components/ui/separator"
import { cn } from "~/lib/utils"
import { 
  Send, 
  Bot, 
  User, 
  Loader2,
  RotateCcw,
  MessageSquare,
  Sparkles,
  Clock,
  CheckCircle2
} from "lucide-react"

interface Message {
  id: string
  type: 'user' | 'bot'
  content: string
  timestamp: number
  sources?: string[]
  sessionId?: string
}

const CHATBOT_API_BASE = "http://localhost:8000"

export function ImprovedChatbotInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      type: "bot",
      content: "👋 **Welcome to MyFundFinder!**\n\nI'm your AI funding assistant. I can help you:\n• Find relevant grants for your business\n• Explain eligibility requirements\n• Guide you through application processes\n\n**Try asking:** \"What digital grants are available?\" or \"Tell me about SME automation grants\"",
      timestamp: Date.now()
    }
  ])
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  
  const fileInputRef = useRef<HTMLInputElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  const formatBotMessage = (content: string) => {
    // Enhanced markdown-like formatting
    let formatted = content
      // Bold text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      // Bullet points
      .replace(/^• (.+)$/gm, '<div class="flex items-start gap-2 my-1"><span class="text-blue-500 mt-1">•</span><span>$1</span></div>')
      // Numbered lists
      .replace(/^(\d+)\.\s(.+)$/gm, '<div class="flex items-start gap-2 my-2"><span class="bg-blue-100 text-blue-700 rounded-full w-6 h-6 flex items-center justify-center text-sm font-medium">$1</span><span>$2</span></div>')
      // Headers
      .replace(/^### (.+)$/gm, '<h3 class="text-lg font-semibold text-gray-800 mt-4 mb-2">$1</h3>')
      .replace(/^## (.+)$/gm, '<h2 class="text-xl font-bold text-gray-900 mt-4 mb-2">$1</h2>')
      // Line breaks
      .replace(/\n/g, '<br>')

    return formatted
  }

  const restartChat = () => {
    setMessages([
      {
        id: "welcome-" + Date.now(),
        type: "bot",
        content: "👋 **Chat restarted!**\n\nI'm ready to help you find funding opportunities. What would you like to know about grants and funding?",
        timestamp: Date.now()
      }
    ])
    setSessionId(null)
    setInputValue("")
  }

  const sendMessage = async (messageText?: string) => {
    const message = messageText || inputValue;
    if (!message.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: message,
      timestamp: Date.now()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue("")
    setIsLoading(true)

    try {
      const response = await fetch(`${CHATBOT_API_BASE}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer your-token-here" // Add if needed
        },
        body: JSON.stringify({ 
          message,
          session_id: sessionId 
        })
      })

      if (response.ok) {
        const data = await response.json()
        
        // Store session ID for conversation continuity
        if (data.session_id && !sessionId) {
          setSessionId(data.session_id)
        }
        
        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: "bot",
          content: data.response,
          timestamp: Date.now(),
          sources: data.sources,
          sessionId: data.session_id
        }
        setMessages(prev => [...prev, botMessage])
      } else {
        throw new Error(`Request failed: ${response.status}`)
      }
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "bot",
        content: `❌ **Connection Error**\n\nI'm having trouble connecting to the server. Please check:\n• Server is running on localhost:8000\n• Your internet connection\n\nTry again in a moment.`,
        timestamp: Date.now()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault()
      sendMessage()
    }
  }

  const suggestedPrompts = [
    "What digital grants are available?",
    "Tell me about SME automation grants",
    "Export grants for my business",
    "Green technology funding options"
  ]

  return (
    <div className="max-w-4xl mx-auto">
      <Card className="h-[700px] flex flex-col shadow-lg">
        <CardHeader className="border-b bg-gradient-to-r from-blue-50 to-indigo-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-blue-500 p-2 rounded-full">
                <Bot className="h-5 w-5 text-white" />
              </div>
              <div>
                <CardTitle className="text-xl">MyFundFinder Assistant</CardTitle>
                <CardDescription className="flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-blue-500" />
                  AI-powered grant recommendations
                  {sessionId && (
                    <Badge variant="secondary" className="ml-2">
                      <MessageSquare className="h-3 w-3 mr-1" />
                      Connected
                    </Badge>
                  )}
                </CardDescription>
              </div>
            </div>
            <Button 
              onClick={restartChat}
              variant="outline" 
              size="sm"
              className="flex items-center gap-2"
            >
              <RotateCcw className="h-4 w-4" />
              Restart Chat
            </Button>
          </div>
        </CardHeader>
        
        {/* Messages Area */}
        <CardContent className="flex-1 overflow-y-auto p-0">
          <div className="p-4 space-y-4">
            {messages.map((message, index) => (
              <div key={message.id} className="group">
                <div
                  className={cn(
                    "flex items-start gap-3",
                    message.type === "user" ? "flex-row-reverse" : "flex-row"
                  )}
                >
                  {/* Avatar */}
                  <div className={cn(
                    "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
                    message.type === "user" 
                      ? "bg-blue-500 text-white" 
                      : "bg-gray-100 text-gray-600"
                  )}>
                    {message.type === "user" ? (
                      <User className="h-4 w-4" />
                    ) : (
                      <Bot className="h-4 w-4" />
                    )}
                  </div>
                  
                  {/* Message Content */}
                  <div className={cn(
                    "max-w-[85%] rounded-2xl px-4 py-3",
                    message.type === "user"
                      ? "bg-blue-500 text-white ml-auto"
                      : "bg-gray-50 border"
                  )}>
                    {message.type === "bot" ? (
                      <div 
                        className="prose prose-sm max-w-none"
                        dangerouslySetInnerHTML={{ 
                          __html: formatBotMessage(message.content) 
                        }}
                      />
                    ) : (
                      <div className="whitespace-pre-wrap">{message.content}</div>
                    )}
                    
                    {/* Sources */}
                    {message.sources && message.sources.length > 0 && (
                      <div className="mt-3 pt-2 border-t border-gray-200">
                        <div className="flex items-center gap-2 text-xs text-gray-500 mb-1">
                          <CheckCircle2 className="h-3 w-3" />
                          Sources:
                        </div>
                        <div className="flex flex-wrap gap-1">
                          {message.sources.map((source, idx) => (
                            <Badge key={idx} variant="secondary" className="text-xs">
                              {source}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Timestamp */}
                <div className={cn(
                  "flex items-center gap-1 mt-1 text-xs text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity",
                  message.type === "user" ? "justify-end mr-11" : "justify-start ml-11"
                )}>
                  <Clock className="h-3 w-3" />
                  {formatTimestamp(message.timestamp)}
                </div>
              </div>
            ))}
            
            {/* Loading indicator */}
            {isLoading && (
              <div className="flex items-center gap-3">
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
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </CardContent>
        
        {/* Suggested Prompts (show when no messages except welcome) */}
        {messages.length <= 1 && (
          <div className="px-4 pb-2">
            <div className="text-sm text-gray-600 mb-2">💡 Try these questions:</div>
            <div className="flex flex-wrap gap-2">
              {suggestedPrompts.map((prompt, idx) => (
                <Button
                  key={idx}
                  variant="outline"
                  size="sm"
                  onClick={() => sendMessage(prompt)}
                  className="text-xs h-8"
                  disabled={isLoading}
                >
                  {prompt}
                </Button>
              ))}
            </div>
            <Separator className="mt-3" />
          </div>
        )}
        
        {/* Input Area */}
        <div className="border-t bg-white p-4">
          <div className="flex gap-3">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about grants, funding opportunities, eligibility requirements..."
              disabled={isLoading}
              className="flex-1 rounded-full border-gray-200 focus:border-blue-500 focus:ring-blue-500"
            />
            <Button 
              onClick={() => sendMessage()} 
              disabled={isLoading || !inputValue.trim()}
              size="icon"
              className="rounded-full bg-blue-500 hover:bg-blue-600"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
          <div className="text-xs text-gray-500 mt-2 text-center">
            Press Enter to send • Shift+Enter for new line
          </div>
        </div>
      </Card>
    </div>
  )
}
