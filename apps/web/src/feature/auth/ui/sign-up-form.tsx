"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Eye, EyeOff, Check, X } from "lucide-react";
import { useAuthActions } from "../model/hooks";

interface SignUpFormProps {
  onSuccess?: () => void;
}

export function SignUpForm({ onSuccess }: SignUpFormProps) {
  const [step, setStep] = useState<"signup" | "confirm">("signup");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    code: "",
  });

  const { signUp, confirmSignUp, loading, error } = useAuthActions();

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

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await signUp(formData.email, formData.password);
    if (result.success) {
      setStep("confirm");
    }
  };

  const handleConfirm = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await confirmSignUp(formData.email, formData.code);
    if (result.success) {
      onSuccess?.();
    }
  };

  const handleResendCode = async () => {
    await signUp(formData.email, formData.password);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  if (step === "confirm") {
    return (
      <div className="space-y-4">
        <div className="text-center space-y-2">
          <h3 className="text-lg font-semibold">Verify your email</h3>
          <p className="text-sm text-muted-foreground">
            We&apos;ve sent a verification code to <strong>{formData.email}</strong>
          </p>
        </div>

        <form onSubmit={handleConfirm} className="space-y-4">
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
          {error && <p className="text-sm text-red-500">{error}</p>}
          <Button
            type="submit"
            className="w-full"
            disabled={loading || formData.code.length !== 6}
          >
            {loading ? "Verifying..." : "Verify Account"}
          </Button>
        </form>

        <div className="text-center space-y-2">
          <p className="text-sm text-muted-foreground">Didn&apos;t receive the code?</p>
          <Button variant="ghost" onClick={handleResendCode} disabled={loading}>
            Resend code
          </Button>
          <Button variant="ghost" onClick={() => setStep("signup")}>
            ← Back to sign up
          </Button>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSignUp} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="email">Email address</Label>
        <Input
          id="email"
          name="email"
          type="email"
          placeholder="john@company.com"
          value={formData.email}
          onChange={handleInputChange}
          required
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="password">Password</Label>
        <div className="relative">
          <Input
            id="password"
            name="password"
            type={showPassword ? "text" : "password"}
            placeholder="Create a password"
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
                  className={`h-1 flex-1 rounded-full ${passwordStrength.score >= level
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
        <Label htmlFor="confirmPassword">Confirm password</Label>
        <div className="relative">
          <Input
            id="confirmPassword"
            name="confirmPassword"
            type={showConfirmPassword ? "text" : "password"}
            placeholder="Confirm your password"
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
                <span className="text-red-600">Passwords don&apos;t match</span>
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
        {loading ? "Creating account..." : "Create account"}
      </Button>
    </form>
  );
}
