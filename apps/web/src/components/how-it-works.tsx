import { Card, CardContent } from "./ui/card"

export function HowItWorks() {
  const steps = [
    {
      step: "01",
      title: "Upload Your Business Info",
      description:
        "Easily provide your company profile or business plan. Our system securely extracts key details like sector, size, and funding goals.",
    },
    {
      step: "02",
      title: "AI-Powered Matching",
      description:
        "Our AI analyzes your profile and automatically matches you with the most relevant government grants and financing options.",
    },
    {
      step: "03",
      title: "Review Eligible Programs",
      description:
        "See a personalized shortlist of funding opportunities. Understand why each program is a match and what documents are required.",
    },
    {
      step: "04",
      title: "Apply with Confidence",
      description:
        "Follow guided next steps to connect with the right agency and submit your application seamlessly.",
    },
  ];


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
