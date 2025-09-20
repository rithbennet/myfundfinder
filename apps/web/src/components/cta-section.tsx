import { Button } from "./ui/button"
import { Card,  CardContent } from "./ui/card"

export function CTASection() {
  return (
    <section className="py-20 sm:py-32 bg-muted/30">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <Card className="mx-auto max-w-4xl border-border bg-card">
          <CardContent className="p-12 text-center">
            <h2 className="text-3xl font-bold tracking-tight text-card-foreground sm:text-4xl">
              {"Ready to Secure Your Business Funding?"}
            </h2>
            <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground">
              {
                "Join thousands of successful SMEs who have found the perfect funding match. Start your application today and get matched with suitable lenders in minutes."
              }
            </p>
            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button
                size="lg"
                className="bg-primary text-primary-foreground hover:bg-primary/90 px-8 py-3 w-full sm:w-auto"
              >
                {"Start Your Application"}
              </Button>
              <Button variant="outline" size="lg" className="px-8 py-3 w-full sm:w-auto bg-transparent">
                {"Speak to an Expert"}
              </Button>
            </div>
            <p className="mt-6 text-sm text-muted-foreground">
              {"No upfront fees • Secure application • 5-minute setup"}
            </p>
          </CardContent>
        </Card>
      </div>
    </section>
  )
}
