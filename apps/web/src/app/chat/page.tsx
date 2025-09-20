"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "~/components/ui/button"
import { Input } from "~/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/components/ui/card"
import { Badge } from "~/components/ui/badge"
import { Send, Bot, User, AlertTriangle, DollarSign, Calendar, CheckCircle } from "lucide-react"
import { cn } from "~/lib/utils"

interface Message {
  id: string
  type: "user" | "bot"
  content: string
  timestamp: Date
}

interface Grant {
  id: string
  title: string
  agency: string
  description: string
  fundingAmount: string
  deadline: string
  isUrgent: boolean
  eligibility: string
  matchReasons: string[]
}

const mockGrants: Grant[] = [
  {
    id: "1",
    title: "Small Business Innovation Research (SBIR)",
    agency: "National Science Foundation",
    description: "Funding for small businesses to engage in research and development with commercialization potential.",
    fundingAmount: "$50,000 - $1,750,000",
    deadline: "2024-12-15",
    isUrgent: true,
    eligibility: "Small businesses with <500 employees, US-based",
    matchReasons: ["technology development", "R&D focus", "innovation"],
  },
  {
    id: "2",
    title: "Community Development Financial Institutions Fund",
    agency: "U.S. Treasury Department",
    description:
      "Support for businesses in underserved communities through financial assistance and technical support.",
    fundingAmount: "$25,000 - $500,000",
    deadline: "2025-03-30",
    isUrgent: false,
    eligibility: "Businesses in low-income communities",
    matchReasons: ["community impact", "local business", "economic development"],
  },
  {
    id: "3",
    title: "Rural Business Development Grant",
    agency: "USDA Rural Development",
    description: "Grants to support the development of small and emerging rural businesses.",
    fundingAmount: "$10,000 - $500,000",
    deadline: "2025-01-31",
    isUrgent: false,
    eligibility: "Rural businesses with <50 employees",
    matchReasons: ["rural location", "small business", "job creation"],
  },
]

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      type: "bot",
      content:
        "Hello! I'm your funding matchmaker assistant. Tell me about your business and I'll help you find the perfect funding opportunities. What type of business do you have and what are you looking to fund?",
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [showResults, setShowResults] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: input,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    // Simulate AI processing
    setTimeout(() => {
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "bot",
        content:
          "Based on your business description, I've found the top 3 funding opportunities that match your needs. Here are my recommendations:",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, botMessage])
      setShowResults(true)
      setIsLoading(false)
    }, 2000)
  }

  const isDeadlineUrgent = (deadline: string) => {
    const deadlineDate = new Date(deadline)
    const now = new Date()
    const diffTime = deadlineDate.getTime() - now.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays <= 30
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <Bot className="w-5 h-5 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-xl font-semibold">FundMatch AI</h1>
                <p className="text-sm text-muted-foreground">Your intelligent funding assistant</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6 max-w-4xl">
        {/* Chat Messages */}
        <div className="space-y-6 mb-6">
          {messages.map((message) => (
            <div
              key={message.id}
              className={cn("flex gap-3", message.type === "user" ? "justify-end" : "justify-start")}
            >
              {message.type === "bot" && (
                <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center flex-shrink-0">
                  <Bot className="w-4 h-4 text-primary-foreground" />
                </div>
              )}
              <div
                className={cn(
                  "max-w-[80%] rounded-lg px-4 py-3",
                  message.type === "user" ? "bg-primary text-primary-foreground ml-12" : "bg-muted",
                )}
              >
                <p className="text-sm leading-relaxed">{message.content}</p>
                <p className="text-xs opacity-70 mt-2">
                  {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </p>
              </div>
              {message.type === "user" && (
                <div className="w-8 h-8 bg-muted rounded-full flex items-center justify-center flex-shrink-0">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-3 justify-start">
              <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center flex-shrink-0">
                <Bot className="w-4 h-4 text-primary-foreground" />
              </div>
              <div className="bg-muted rounded-lg px-4 py-3">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                  <div className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                  <div className="w-2 h-2 bg-muted-foreground/50 rounded-full animate-bounce"></div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Grant Results */}
        {showResults && (
          <div className="space-y-4 mb-6">
            <h3 className="text-lg font-semibold text-center mb-6">Top 3 Funding Matches</h3>
            {mockGrants.map((grant, index) => (
              <Card key={grant.id} className="relative">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <CardTitle className="text-lg">{grant.title}</CardTitle>
                      <CardDescription className="font-medium text-primary">{grant.agency}</CardDescription>
                    </div>
                    <Badge variant="secondary" className="ml-2">
                      #{index + 1} Match
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-sm text-muted-foreground leading-relaxed">{grant.description}</p>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="flex items-center gap-2">
                      <DollarSign className="w-4 h-4 text-green-600" />
                      <div>
                        <p className="text-xs text-muted-foreground">Funding Amount</p>
                        <p className="text-sm font-medium">{grant.fundingAmount}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-blue-600" />
                      <div>
                        <p className="text-xs text-muted-foreground">Deadline</p>
                        <div className="flex items-center gap-1">
                          <p className="text-sm font-medium">{new Date(grant.deadline).toLocaleDateString()}</p>
                          {isDeadlineUrgent(grant.deadline) && <AlertTriangle className="w-3 h-3 text-orange-500" />}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-green-600" />
                      <div>
                        <p className="text-xs text-muted-foreground">Eligibility</p>
                        <p className="text-sm font-medium">{grant.eligibility}</p>
                      </div>
                    </div>
                  </div>

                  {grant.isUrgent && (
                    <Badge variant="destructive" className="w-fit">
                      <AlertTriangle className="w-3 h-3 mr-1" />
                      Deadline Soon!
                    </Badge>
                  )}

                  <div className="pt-2 border-t">
                    <p className="text-xs text-muted-foreground mb-2">Why this matches you:</p>
                    <div className="flex flex-wrap gap-1">
                      {grant.matchReasons.map((reason, idx) => (
                        <Badge key={idx} variant="outline" className="text-xs">
                          {reason}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <Button className="w-full" size="sm">
                    Learn More & Apply
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Chat Input */}
        <div className="sticky bottom-0 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-t pt-4">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Describe your business and funding needs..."
              className="flex-1"
              disabled={isLoading}
            />
            <Button type="submit" disabled={isLoading || !input.trim()}>
              <Send className="w-4 h-4" />
            </Button>
          </form>
          <p className="text-xs text-muted-foreground mt-2 text-center">
            Be specific about your industry, business size, and what you need funding for
          </p>
        </div>
      </div>
    </div>
  )
}
