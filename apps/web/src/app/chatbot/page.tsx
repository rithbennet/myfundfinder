import { Header } from "~/components/header"
import { ChatbotInterface } from "~/components/chatbot-interface"
import { Footer } from "~/components/footer"

export const metadata = {
  title: "AI Funding Assistant - MyFundFinder",
  description: "Get personalized grant recommendations with our AI-powered assistant. Upload business documents and receive detailed funding opportunities.",
}

export default function ChatbotPage() {
  return (
    <main className="min-h-screen bg-background">
      <Header />
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold tracking-tight text-foreground mb-4">
            AI Funding Assistant
          </h1>
          <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
            Upload your business documents and get personalized grant recommendations. 
            Our AI assistant analyzes your company profile and matches you with the most relevant funding opportunities.
          </p>
        </div>
        <ChatbotInterface />
      </div>
      <Footer />
    </main>
  )
}