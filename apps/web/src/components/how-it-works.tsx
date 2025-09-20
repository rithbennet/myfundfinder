import { Card, CardContent } from "./ui/card"

export function HowItWorks() {
  const steps = [
    {
      step: "01",
      title: "Complete Your Profile",
      description:
        "Tell us about your business, funding needs, and financial situation through our secure 5-minute application.",
    },
    {
      step: "02",
      title: "Get Matched Instantly",
      description:
        "Our AI analyzes your profile and matches you with the most suitable funding options from our network of verified lenders.",
    },
    {
      step: "03",
      title: "Compare & Choose",
      description:
        "Review personalized offers, compare terms, and select the funding option that best fits your business needs.",
    },
    {
      step: "04",
      title: "Secure Your Funding",
      description:
        "Complete the application process with your chosen lender and receive funding approval in as little as 72 hours.",
    },
  ]

  return (
    <section id="how-it-works" className="py-20 sm:py-32 bg-background">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">{"How FundMatch Works"}</h2>
          <p className="mt-4 text-lg text-muted-foreground">
            {"Get matched with the right funding in four simple steps."}
          </p>
        </div>

        <div className="mx-auto mt-16 grid max-w-6xl grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-4">
          {steps.map((step, index) => (
            <Card key={index} className="border-border bg-card relative">
              <CardContent className="p-8">
                <div className="absolute -top-4 left-8">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-accent text-accent-foreground text-sm font-bold">
                    {step.step}
                  </div>
                </div>
                <h3 className="text-xl font-semibold text-card-foreground mb-4 mt-4">{step.title}</h3>
                <p className="text-muted-foreground leading-relaxed">{step.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
