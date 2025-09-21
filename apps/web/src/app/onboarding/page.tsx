import { Header } from "~/components/header"
import { Footer } from "~/components/footer"
import OnboardingForm from "~/components/form/onBoardingForm"

export const metadata = {
  title: "AI Assistant - FundMatch",
  description: "Onboard your company to get AI-powered funding recommendations",
}

export default function OnboardingPage() {
  return (
    <main className="min-h-screen bg-background">
      <Header />
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold tracking-tight text-foreground mb-4">
            🚀 SME Onboarding
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Upload your documents and let our AI auto-fill your company information.
          </p>
        </div>
        <OnboardingForm />
      </div>
      <Footer />
    </main>
  )
}
