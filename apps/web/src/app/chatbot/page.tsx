import { Header } from "~/components/header"
import { ChatbotInterface } from "~/components/chatbot-interface"
import { Footer } from "~/components/footer"

export const metadata = {
  title: "Fund Matchmaker",
  description: "Get personalized funding recommendations with our AI-powered document assistant",
}

export default function ChatbotPage() {
  return (
    <main className="min-h-screen bg-background">
      <Header />
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold tracking-tight text-foreground mb-4">
            Fund Matchmaker
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Upload your business documents and get personalized funding advice. 
            Our AI assistant can help you understand funding opportunities, requirements, and more.
          </p>
        </div>
        <ChatbotInterface />
      </div>
      <Footer />
    </main>
  )
}