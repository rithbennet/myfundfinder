"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Eye, EyeOff, Check, X } from "lucide-react";
import { useAuthActions } from "../model/hooks";

export function ForgotPasswordForm() {
  const [step, setStep] = useState<"email" | "code" | "success">("email");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [formData, setFormData] = useState({
    email: "",
    code: "",
    password: "",
    confirmPassword: "",
  });

  const { forgotPassword, confirmForgotPassword, loading, error } = useAuthActions();

  const getPasswordStrength = (password: string) => {
    const checks = {
      length: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      number: /\d/.test(password),
      special: /[!@#$%^&*(),.?":{}|<>]/.test(password),
    };
    const score = Object.values(checks).filter(Boolean).length;
    return { checks, score };
  };

  const passwordStrength = getPasswordStrength(formData.password);
  const passwordsMatch = formData.password === formData.confirmPassword && formData.confirmPassword !== "";

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await forgotPassword(formData.email);
    if (result.success) {
      setStep("code");
    }
  };

  const handleCodeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await confirmForgotPassword(formData.email, formData.code, formData.password);
    if (result.success) {
      setStep("success");
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  if (step === "success") {
    return (
      <div className="text-center space-y-4">
        <h3 className="text-lg font-semibold">Password Reset Successful</h3>
        <p className="text-muted-foreground">Your password has been reset successfully.</p>
        <Button onClick={() => window.location.href = '/sign-in'} className="w-full">
          Sign In
        </Button>
      </div>
    );
  }

  if (step === "code") {
    return (
      <form onSubmit={handleCodeSubmit} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="code">Verification Code</Label>
          <Input
            id="code"
            name="code"
            placeholder="Enter 6-digit code"
            value={formData.code}
            onChange={handleInputChange}
            required
            className="text-center text-lg tracking-widest"
            maxLength={6}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="password">New Password</Label>
          <div className="relative">
            <Input
              id="password"
              name="password"
              type={showPassword ? "text" : "password"}
              placeholder="Create new password"
              value={formData.password}
              onChange={handleInputChange}
              required
              className="pr-10"
            />
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="absolute right-0 top-0 h-full px-3"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </Button>
          </div>

          {formData.password && (
            <div className="space-y-2">
              <div className="flex gap-1">
                {[1, 2, 3, 4, 5].map((level) => (
                  <div
                    key={level}
                    className={`h-1 flex-1 rounded-full ${
                      passwordStrength.score >= level
                        ? passwordStrength.score <= 2
                          ? "bg-red-500"
                          : passwordStrength.score <= 3
                            ? "bg-yellow-500"
                            : "bg-green-500"
                        : "bg-muted"
                    }`}
                  />
                ))}
              </div>
              <div className="space-y-1 text-xs">
                {Object.entries({
                  "At least 8 characters": passwordStrength.checks.length,
                  "One uppercase letter": passwordStrength.checks.uppercase,
                  "One lowercase letter": passwordStrength.checks.lowercase,
                  "One number": passwordStrength.checks.number,
                  "One special character": passwordStrength.checks.special,
                }).map(([requirement, met]) => (
                  <div key={requirement} className="flex items-center gap-2">
                    {met ? (
                      <Check className="h-3 w-3 text-green-500" />
                    ) : (
                      <X className="h-3 w-3 text-muted-foreground" />
                    )}
                    <span className={met ? "text-green-600" : "text-muted-foreground"}>
                      {requirement}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="confirmPassword">Confirm Password</Label>
          <div className="relative">
            <Input
              id="confirmPassword"
              name="confirmPassword"
              type={showConfirmPassword ? "text" : "password"}
              placeholder="Confirm new password"
              value={formData.confirmPassword}
              onChange={handleInputChange}
              required
              className="pr-10"
            />
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="absolute right-0 top-0 h-full px-3"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            >
              {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </Button>
          </div>
          {formData.confirmPassword && (
            <div className="flex items-center gap-2 text-xs">
              {passwordsMatch ? (
                <>
                  <Check className="h-3 w-3 text-green-500" />
                  <span className="text-green-600">Passwords match</span>
                </>
              ) : (
                <>
                  <X className="h-3 w-3 text-red-500" />
                  <span className="text-red-600">Passwords don't match</span>
                </>
              )}
            </div>
          )}
        </div>

        {error && <p className="text-sm text-red-500">{error}</p>}

        <Button 
          type="submit" 
          className="w-full" 
          disabled={loading || passwordStrength.score < 3 || !passwordsMatch}
        >
          {loading ? "Resetting..." : "Reset Password"}
        </Button>
      </form>
    );
  }

  return (
    <form onSubmit={handleEmailSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="email">Email address</Label>
        <Input
          id="email"
          name="email"
          type="email"
          placeholder="Enter your email"
          value={formData.email}
          onChange={handleInputChange}
          required
        />
      </div>

      {error && <p className="text-sm text-red-500">{error}</p>}

      <Button type="submit" className="w-full" disabled={loading}>
        {loading ? "Sending..." : "Send Reset Code"}
      </Button>
    </form>
  );
}
