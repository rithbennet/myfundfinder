"use client"

import { useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { AuthHeader } from "~/feature/auth/ui/auth-header"
import { tokenStorage } from "~/feature/auth/lib/storage"

export default function SignOutPage() {
  useEffect(() => {
    // Clear tokens from sessionStorage
    tokenStorage.clear()
    
    // Clear auth cookie
    document.cookie = 'auth-token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT'
    
    // Redirect to home page after a short delay
    const timer = setTimeout(() => {
      window.location.href = '/'
    }, 2000)

    return () => clearTimeout(timer)
  }, [])

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        <AuthHeader />

        <Card className="border-border shadow-lg">
          <CardHeader className="space-y-2 text-center">
            <CardTitle className="text-2xl font-semibold text-balance">Signed out</CardTitle>
            <CardDescription className="text-muted-foreground text-balance">
              You have been successfully signed out. Redirecting to home page...
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
