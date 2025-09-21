"use client"

import Link from "next/link"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { AuthHeader } from "~/feature/auth/ui/auth-header"
import { SignUpForm } from "~/feature/auth/ui/sign-up-form"

export default function SignUpPage() {
  const handleSuccess = () => {
    window.location.href = '/sign-in';
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        <AuthHeader />

        <Card className="border-border shadow-lg">
          <CardHeader className="space-y-2 text-center">
            <CardTitle className="text-2xl font-semibold text-balance">Create your account</CardTitle>
            <CardDescription className="text-muted-foreground text-balance">
              Join thousands of businesses finding their perfect funding match
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-4">
            <SignUpForm onSuccess={handleSuccess} />

            <div className="text-center text-sm text-muted-foreground">
              Already have an account?{" "}
              <Link href="/sign-in" className="text-accent hover:text-accent/80 font-medium">
                Sign in
              </Link>
            </div>
          </CardContent>
        </Card>

        <div className="text-center text-xs text-muted-foreground">
          By signing up, you agree to our{" "}
          <Link href="/terms" className="underline hover:text-foreground">
            Terms of Service
          </Link>{" "}
          and{" "}
          <Link href="/privacy" className="underline hover:text-foreground">
            Privacy Policy
          </Link>
        </div>
      </div>
    </div>
  )
}
