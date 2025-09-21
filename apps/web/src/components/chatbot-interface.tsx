"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "~/components/ui/button"
import { Input } from "~/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/components/ui/card"
import { Badge } from "~/components/ui/badge"
import { cn } from "~/lib/utils"
import ChatbotResponse from "./ChatbotResponse"
import SuggestedPrompts from "./SuggestedPrompts"
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
  MessageSquare,
  TestTube
} from "lucide-react"

interface Message {
  id: string
  type: 'user' | 'bot'
  content: string
  timestamp: number
  searchResults?: number
  sources?: string[]
  sessionId?: string
  isStructuredResponse?: boolean
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

// Test JSON response you provided
const TEST_RESPONSE = {
  response: "\nBased on the provided information and company profile, here are specific recommendations for grants that may be relevant for your tech startup in Kuala Lumpur with 15 employees:\n\n1. Digital Transformation Grant for SMEs: This grant provides up to RM50,000 for Malaysian SMEs to adopt digital technologies, including cloud computing, e-commerce platforms, and digital marketing tools. To be eligible, your company must be Malaysian-owned, have less than 200 employees, and have annual revenue below RM50 million. You will need to submit business registration certificate, audited financial statements for the last 2 years, and a detailed project proposal with timeline and budget breakdown. The grant covers 70% of eligible costs, including software licenses, hardware procurement, training costs, and consultant fees for digital implementation projects. The application deadline is usually around March or April each year, and you should check the official website for more information.\n\n2. Digital Transformation Grant for SMEs (Micro): This grant is specifically designed for micro-enterprises with up to 10 employees. The eligibility requirements are similar to the Digital Transformation Grant for SMEs, but the grant amount is lower, ranging from RM5,000 to RM20,000.\n\n3. Digital Transformation Grant for SMEs (SMEs): This grant is aimed at SMEs with up to 50 employees. The eligibility requirements are similar to the Digital Transformation Grant for SMEs, but the grant amount is higher, ranging from RM20,000 to RM50,000.\n\n4. Malaysia Digital Economy Corporation (MDEC) Grants: MDEC offers a range of grants and incentives to support the growth of digital businesses in Malaysia. These grants cover various areas, such as e-commerce, fintech, and cybersecurity. You should visit the MDEC website to find out more about the grants available and the eligibility requirements.\n\n5. Government-funded Research and Development Grants: Malaysia has several government-funded research and development grants that can support your tech startup's research and development efforts. These grants are typically available to companies that are working on innovative technologies or solving specific industry problems. You should visit the Ministry of Science, Technology, and Innovation website to find out more about these grants.\n\n6. Angel Investment and Venture Capital: Angel investors and venture capitalists can provide funding for your tech startup. You should reach out to local venture capital firms or angel investors to explore funding opportunities.\n\n7. Crowdfunding: Crowdfunding can be a viable option for tech startups to raise funding. You can use platforms like Kickstarter or Indiegogo to raise money from the public.\n\n8. Business Loans: Business loans can provide funding for your tech startup's operations and growth. You should check with local banks or financial institutions to see if you are eligible for a business loan.\n\n9. Government Grants for Women-Led Businesses: Malaysia has several government grants that are specifically designed for women-led businesses. These grants can provide funding for business development, training, and marketing. You should visit the Ministry of Women, Family, and Community Development website to find out more about these grants.\n\n10. Tax Incentives: Malaysia offers several tax incentives to support businesses, including tax credits, tax exemptions, and tax holidays. You should consult with a tax advisor to see if you are eligible for any of these tax incentives.\n\nIn addition to these grants, it is important to develop a strong business plan, build a strong network, and focus on delivering a high-quality product or service. You should also be prepared to adapt to changing market conditions and trends.\n\nTo prepare for applying for grants, you should gather all of the required documents, such as business registration certificate, audited financial statements, and a detailed project proposal. You should also make sure that your business plan is well-written and concise, and that your team is prepared to answer any questions that may arise during the application process.\n\nIt is important to note that the grant application process can be competitive, and it may take several months to receive funding. Therefore, it is recommended that you start planning for your grant applications early. You should also be prepared to follow up with the granting organization if you have any questions or concerns about your application.\n\nIn conclusion, there are several grants available for a tech startup in Kuala Lumpur with 15 employees. These grants can provide funding for digital transformation projects, research and development, angel investment, venture capital, crowdfunding, business loans, government grants for women-led businesses, tax incentives, and more. To be eligible for these grants, you should check the eligibility requirements and application deadlines, and prepare all of the required documents. You should also be prepared to adapt to changing market conditions and trends, and to follow up with the granting organization if you have any questions or concerns about your application.",
  session_id: "cb7fabb9-54f9-4b13-a373-a352b02bb7e5",
  sources: ["Digital Transformation Grant for SMEs","Digital Transformation Grant for SMEs","Digital Transformation Grant for SMEs","Digital Transformation Grant for SMEs","Digital Transformation Grant for SMEs"]
}

export function ChatbotInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      type: "bot",
      content: "👋 Welcome to your SME Funding Assistant! Upload documents and ask questions about funding opportunities, requirements, and business advice. Try asking: 'What grants are available for a tech startup with 15 employees in Kuala Lumpur?'",
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

  // TEST FUNCTION - Simulates your JSON response
  const sendTestResponse = () => {
    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: "What grants are available for a tech startup with 15 employees in Kuala Lumpur?",
      timestamp: Date.now()
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    // Simulate API delay
    setTimeout(() => {
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "bot",
        content: TEST_RESPONSE.response,
        timestamp: Date.now(),
        searchResults: 5,
        sources: TEST_RESPONSE.sources,
        sessionId: TEST_RESPONSE.session_id,
        isStructuredResponse: true
      }
      
      setMessages(prev => [...prev, botMessage])
      setIsLoading(false)
    }, 1500)
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
        },
        body: JSON.stringify({ message })
      })

      if (response.ok) {
        const data = await response.json()
        
        // Check if this is a structured grant recommendation response
        const isGrantRecommendation = data.response.includes("recommendations for grants") || 
                                     data.response.includes("funding opportunities") ||
                                     data.response.match(/\d+\.\s.*Grant/)
        
        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: "bot",
          content: data.response,
          timestamp: Date.now(),
          searchResults: data.search_results_count,
          sources: data.sources,
          sessionId: data.session_id,
          isStructuredResponse: isGrantRecommendation
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


  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault()
      sendMessage()
    }
  }

  const handleSendClick = () => {
    sendMessage()
  }

  const handlePromptClick = (prompt: string) => {
    sendMessage(prompt)
  }

  return (
    <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-4 gap-6">
      {/* Main Chat Area */}
      <div className="lg:col-span-3">
        <Card className="h-[700px] flex flex-col">
          <CardHeader className="border-b">
            <CardTitle className="flex items-center gap-2">
              <Bot className="h-5 w-5" />
              AI Funding Assistant
            </CardTitle>
            <CardDescription className="flex items-center justify-between">
              <span>Upload documents and get personalized grant recommendations with detailed analysis</span>
              {/* TEST BUTTON */}
              <Button 
                onClick={sendTestResponse}
                variant="outline" 
                size="sm"
                className="ml-4"
                disabled={isLoading}
              >
                <TestTube className="h-4 w-4 mr-2" />
                Test Response
              </Button>
            </CardDescription>
          </CardHeader>
          
          {/* Messages Area */}
          <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <div key={message.id}>
                {message.isStructuredResponse ? (
                  // Render structured grant recommendations
                  <ChatbotResponse 
                    response={message.content}
                    sources={message.sources}
                    sessionId={message.sessionId}
                  />
                ) : (
                  // Render regular chat message
                  <div
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
                      
                      {message.sources && message.sources.length > 0 && !message.isStructuredResponse && (
                        <div className="mt-1 text-xs opacity-70">
                          Sources: {message.sources.join(', ')}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
            
            {isLoading && (
              <div className="flex items-center gap-3">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-secondary">
                  <Loader2 className="h-4 w-4 animate-spin" />
                </div>
                <div className="text-sm text-muted-foreground">AI is analyzing your request...</div>
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
                placeholder="Ask about grants, funding opportunities, eligibility requirements..."
                disabled={isLoading}
                className="flex-1"
              />
              <Button 
                onClick={handleSendClick} 
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
    </div>
  )
}