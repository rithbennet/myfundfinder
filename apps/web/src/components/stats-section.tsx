export function StatsSection() {
  const stats = [
    { value: "£2.5B+", label: "Funding Facilitated" },
    { value: "15,000+", label: "SMEs Funded" },
    { value: "500+", label: "Lending Partners" },
    { value: "72hrs", label: "Average Approval Time" },
  ]

  return (
    <section className="py-20 sm:py-32 bg-primary text-primary-foreground">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">{"Trusted by Growing Businesses"}</h2>
          <p className="mt-4 text-lg text-primary-foreground/80">
            {"Join thousands of SMEs who have successfully secured funding through our platform."}
          </p>
        </div>

        <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
          {stats.map((stat, index) => (
            <div key={index} className="text-center">
              <div className="text-4xl font-bold sm:text-5xl">{stat.value}</div>
              <div className="mt-2 text-sm font-medium text-primary-foreground/80 sm:text-base">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
