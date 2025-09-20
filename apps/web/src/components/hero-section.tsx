import { Button } from "./ui/button"
import { Badge } from "lucide-react"

export function HeroSection() {
  return (
    <section className="relative overflow-hidden bg-background py-20 sm:py-32">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-4xl text-center">
          <Badge variant="secondary" className="mb-8 inline-flex items-center gap-2 px-4 py-2">
            <div className="h-2 w-2 rounded-full bg-accent"></div>
            {"Connecting SMEs with £2.5B+ in funding opportunities"}
          </Badge>

          <h1 className="text-balance text-4xl font-bold tracking-tight text-foreground sm:text-6xl lg:text-7xl">
            {"AI-Driven Funding Matcher for "}
            <span className="text-accent">{"High-Growth SMEs"}</span>
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-muted-foreground">
            {
              "Leverage proprietary AI models that analyze your business DNA, sector dynamics, and capital landscape to deliver precision-matched funding—grants, investors, and lenders—in real time."
            }
          </p>

          <div className="mt-10 flex items-center justify-center gap-x-6">
            <Button size="lg" className="bg-primary text-primary-foreground hover:bg-primary/90 px-8 py-3">
              {"Find Funding Now"}
              <svg className="ml-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </Button>
          </div>
        </div>
      </div>
    </section>
  )
}
