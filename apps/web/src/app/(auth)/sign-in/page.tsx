"use client"

import Link from "next/link"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { AuthHeader } from "~/feature/auth/ui/auth-header"
import { SignInForm } from "~/feature/auth/ui/sign-in-form"

export default function SignInPage() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        <AuthHeader />

        <Card className="border-border shadow-lg">
          <CardHeader className="space-y-2 text-center">
            <CardTitle className="text-2xl font-semibold text-balance">Welcome back</CardTitle>
            <CardDescription className="text-muted-foreground text-balance">
              Sign in to your account to access funding opportunities
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-4">
            <SignInForm />

            <div className="flex items-center justify-between">
              <div className="text-sm">
                <Link href="/forgot-password" className="text-accent hover:text-accent/80 font-medium">
                  Forgot password?
                </Link>
              </div>
            </div>

            <div className="text-center text-sm text-muted-foreground">
              {"Don't have an account? "}
              <Link href="/sign-up" className="text-accent hover:text-accent/80 font-medium">
                Sign up
              </Link>
            </div>
          </CardContent>
        </Card>

        <div className="text-center text-xs text-muted-foreground">
          By signing in, you agree to our{" "}
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
