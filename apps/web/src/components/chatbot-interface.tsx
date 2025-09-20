"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "~/components/ui/button"
import { Input } from "~/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/components/ui/card"
import { Badge } from "~/components/ui/badge"
import { cn } from "~/lib/utils"
import { 
  Send, 
  Upload, 
  FileText, 
  Bot, 
  User, 
  Loader2,
  CheckCircle,
  XCircle,
  Database,
  MessageSquare
} from "lucide-react"

interface Message {
  id: string
  type: 'user' | 'bot'
  content: string
  timestamp: number
  searchResults?: number
  sources?: string[]
}

interface SystemStatus {
  status: string
  documents_count: number
  processed_count: number
  chat_history_length: number
  bucket: string
}

interface Document {
  name: string
  size: number
  last_modified: string
}

const CHATBOT_API_BASE = "http://localhost:9000"

export function ChatbotInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      type: "bot",
      content: "👋 Welcome to your SME Funding Assistant! Upload documents and ask questions about funding opportunities, requirements, and business advice.",
      timestamp: Date.now()
    }
  ])
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [documents, setDocuments] = useState<Document[]>([])
  const [isUploading, setIsUploading] = useState(false)
  
  const fileInputRef = useRef<HTMLInputElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // Load initial data
  useEffect(() => {
    loadSystemStatus()
    loadDocuments()
  }, [])

  const loadSystemStatus = async () => {
    try {
      const response = await fetch(`${CHATBOT_API_BASE}/status`)
      if (response.ok) {
        const data = await response.json()
        setSystemStatus(data)
      }
    } catch (error) {
      console.error("Failed to load system status:", error)
    }
  }

  const loadDocuments = async () => {
    try {
      const response = await fetch(`${CHATBOT_API_BASE}/documents`)
      if (response.ok) {
        const data = await response.json()
        setDocuments(data.documents || [])
      }
    } catch (error) {
      console.error("Failed to load documents:", error)
    }
  }

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: inputValue,
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
        },
        body: JSON.stringify({ message: inputValue })
      })

      if (response.ok) {
        const data = await response.json()
        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: "bot",
          content: data.response,
          timestamp: Date.now(),
          searchResults: data.search_results_count,
          sources: data.sources
        }
        setMessages(prev => [...prev, botMessage])
      } else {
        throw new Error(`Request failed: ${response.status}`)
      }
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "bot",
        content: `❌ Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}. Please make sure the chatbot server is running on localhost:8080.`,
        timestamp: Date.now()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setIsUploading(true)

    // Add upload notification
    const uploadMessage: Message = {
      id: Date.now().toString(),
      type: "bot",
      content: `📤 Uploading "${file.name}"...`,
      timestamp: Date.now()
    }
    setMessages(prev => [...prev, uploadMessage])

    const formData = new FormData()
    formData.append("file", file)

    try {
      const response = await fetch(`${CHATBOT_API_BASE}/upload`, {
        method: "POST",
        body: formData
      })

      const result = await response.json()
      
      const resultMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "bot",
        content: result.success 
          ? `✅ ${result.message}` 
          : `❌ Upload failed: ${result.message}`,
        timestamp: Date.now()
      }
      
      setMessages(prev => [...prev, resultMessage])
      
      if (result.success) {
        loadDocuments()
        loadSystemStatus()
      }
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        type: "bot",
        content: `❌ Upload error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: Date.now()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsUploading(false)
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ""
      }
    }
  }

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-4 gap-6">
      {/* Main Chat Area */}
      <div className="lg:col-span-3">
        <Card className="h-[600px] flex flex-col">
          <CardHeader className="border-b">
            <CardTitle className="flex items-center gap-2">
              <Bot className="h-5 w-5" />
              AI Funding Assistant
            </CardTitle>
            <CardDescription>
              Ask questions about your uploaded documents and get personalized funding advice
            </CardDescription>
          </CardHeader>
          
          {/* Messages Area */}
          <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  "flex items-start gap-3",
                  message.type === "user" ? "flex-row-reverse" : "flex-row"
                )}
              >
                <div className={cn(
                  "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
                  message.type === "user" 
                    ? "bg-primary text-primary-foreground" 
                    : "bg-secondary text-secondary-foreground"
                )}>
                  {message.type === "user" ? (
                    <User className="h-4 w-4" />
                  ) : (
                    <Bot className="h-4 w-4" />
                  )}
                </div>
                
                <div className={cn(
                  "max-w-[80%] rounded-lg px-4 py-2 text-sm",
                  message.type === "user"
                    ? "bg-primary text-primary-foreground ml-auto"
                    : "bg-muted"
                )}>
                  <div className="whitespace-pre-wrap">{message.content}</div>
                  
                  {message.searchResults !== undefined && message.searchResults > 0 && (
                    <div className="mt-2 flex items-center gap-2">
                      <Badge variant="secondary" className="text-xs">
                        📖 {message.searchResults} document{message.searchResults !== 1 ? 's' : ''} found
                      </Badge>
                    </div>
                  )}
                  
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-1 text-xs opacity-70">
                      Sources: {message.sources.join(', ')}
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex items-center gap-3">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-secondary">
                  <Loader2 className="h-4 w-4 animate-spin" />
                </div>
                <div className="text-sm text-muted-foreground">AI is thinking...</div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </CardContent>
          
          {/* Input Area */}
          <div className="border-t p-4">
            <div className="flex gap-2">
              <Input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me about your documents..."
                disabled={isLoading}
                className="flex-1"
              />
              <Button 
                onClick={sendMessage} 
                disabled={isLoading || !inputValue.trim()}
                size="icon"
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>
        </Card>
      </div>

      {/* Sidebar */}
      <div className="space-y-6">
        {/* Upload Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-4 w-4" />
              Upload Documents
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div 
              className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-6 text-center hover:border-muted-foreground/50 transition-colors cursor-pointer"
              onClick={() => fileInputRef.current?.click()}
            >
              <FileText className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
              <div className="text-sm font-medium">Click to upload</div>
              <div className="text-xs text-muted-foreground mt-1">
                Supports .txt, .md, .csv files
              </div>
            </div>
            
            <input
              ref={fileInputRef}
              type="file"
              accept=".txt,.md,.csv"
              onChange={handleFileUpload}
              className="hidden"
            />
            
            {isUploading && (
              <div className="mt-2 flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                Uploading...
              </div>
            )}
          </CardContent>
        </Card>

        {/* System Status */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-4 w-4" />
              System Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            {systemStatus ? (
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Status:</span>
                  <span className="flex items-center gap-1">
                    {systemStatus.status === 'healthy' ? (
                      <CheckCircle className="h-3 w-3 text-green-500" />
                    ) : (
                      <XCircle className="h-3 w-3 text-red-500" />
                    )}
                    {systemStatus.status}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Documents:</span>
                  <span>{systemStatus.documents_count}</span>
                </div>
                <div className="flex justify-between">
                  <span>Processed:</span>
                  <span>{systemStatus.processed_count}</span>
                </div>
                <div className="flex justify-between">
                  <span>Messages:</span>
                  <span>{systemStatus.chat_history_length}</span>
                </div>
              </div>
            ) : (
              <div className="text-sm text-muted-foreground">Loading...</div>
            )}
          </CardContent>
        </Card>

        {/* Documents List */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4" />
              Documents
            </CardTitle>
          </CardHeader>
          <CardContent>
            {documents.length > 0 ? (
              <div className="space-y-2">
                {documents.slice(0, 5).map((doc, index) => (
                  <div key={index} className="text-sm p-2 bg-muted/50 rounded">
                    <div className="font-medium truncate">{doc.name}</div>
                    <div className="text-xs text-muted-foreground">
                      {(doc.size / 1024).toFixed(1)} KB
                    </div>
                  </div>
                ))}
                {documents.length > 5 && (
                  <div className="text-xs text-muted-foreground text-center pt-2">
                    +{documents.length - 5} more documents
                  </div>
                )}
              </div>
            ) : (
              <div className="text-sm text-muted-foreground">
                No documents uploaded yet
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}