"use client"

import Link from "next/link"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { AuthHeader } from "~/feature/auth/ui/auth-header"
import { ForgotPasswordForm } from "~/feature/auth/ui/forgot-password-form"
import { ArrowLeft } from "lucide-react"

export default function ForgotPasswordPage() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        <AuthHeader />

        <Card className="border-border shadow-lg">
          <CardHeader className="space-y-2 text-center">
            <CardTitle className="text-2xl font-semibold text-balance">Reset your password</CardTitle>
            <CardDescription className="text-muted-foreground text-balance">
              Enter your email address and we&apos;ll send you a verification code
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-4">
            <ForgotPasswordForm />

            <div className="text-center">
              <Link
                href="/sign-in"
                className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to sign in
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
