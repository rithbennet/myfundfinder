import { Header } from "~/components/header"
import { HeroSection } from "~/components/hero-section"
import { FeaturesSection } from "~/components/features-section"
import { StatsSection } from "~/components/stats-section"
import { HowItWorks } from "~/components/how-it-works"
import { CTASection } from "~/components/cta-section"
import { Footer } from "~/components/footer"

export default function Home() {
  return (
    <main className="min-h-screen">
      <Header />
      <HeroSection />
      <FeaturesSection />
      <HowItWorks />
      <CTASection />
      <Footer />
    </main>
  )
}