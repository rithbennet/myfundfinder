"use client";

import { createContext, useContext, useEffect, useState } from 'react';

interface User {
  username: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string;
  signUp: (email: string, password: string) => Promise<any>;
  confirmSignUp: (email: string, code: string) => Promise<any>;
  signIn: (email: string, password: string) => Promise<any>;
  signOut: () => void;
  getCurrentUser: () => Promise<User | null>;
  forgotPassword: (email: string) => Promise<any>;
  confirmForgotPassword: (email: string, code: string, newPassword: string) => Promise<any>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const callAPI = async (action: string, data: any) => {
    const response = await fetch('/api/auth/cognito', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action, ...data })
    });
    return response.json();
  };

  const getCurrentUser = async (accessToken?: string) => {
    try {
      const token = accessToken || JSON.parse(localStorage.getItem('cognito_tokens') || '{}').AccessToken;
      if (!token) return null;

      const result = await callAPI('getUser', { accessToken: token });
      if (result.success) {
        setUser(result.user);
        return result.user;
      } else {
        localStorage.removeItem('cognito_tokens');
        setUser(null);
        return null;
      }
    } catch (err) {
      localStorage.removeItem('cognito_tokens');
      setUser(null);
      return null;
    }
  };

  const signUp = async (email: string, password: string) => {
    setLoading(true);
    setError('');
    try {
      const result = await callAPI('signUp', { email, password });
      if (!result.success) {
        setError(result.error);
      }
      return result;
    } catch (err: any) {
      const errorMsg = err.message || 'Sign up failed';
      setError(errorMsg);
      return { success: false, error: errorMsg };
    } finally {
      setLoading(false);
    }
  };

  const confirmSignUp = async (email: string, code: string) => {
    setLoading(true);
    setError('');
    try {
      const result = await callAPI('confirmSignUp', { email, code });
      if (!result.success) {
        setError(result.error);
      }
      return result;
    } catch (err: any) {
      const errorMsg = err.message || 'Confirmation failed';
      setError(errorMsg);
      return { success: false, error: errorMsg };
    } finally {
      setLoading(false);
    }
  };

  const signIn = async (email: string, password: string) => {
    setLoading(true);
    setError('');
    try {
      const result = await callAPI('signIn', { email, password });
      if (result.success && result.tokens) {
        localStorage.setItem('cognito_tokens', JSON.stringify(result.tokens));
        await getCurrentUser(result.tokens.AccessToken);
      } else {
        setError(result.error);
      }
      return result;
    } catch (err: any) {
      const errorMsg = err.message || 'Sign in failed';
      setError(errorMsg);
      return { success: false, error: errorMsg };
    } finally {
      setLoading(false);
    }
  };

  const forgotPassword = async (email: string) => {
    setLoading(true);
    setError('');
    try {
      const result = await callAPI('forgotPassword', { email });
      if (!result.success) {
        setError(result.error);
      }
      return result;
    } catch (err: any) {
      const errorMsg = err.message || 'Forgot password failed';
      setError(errorMsg);
      return { success: false, error: errorMsg };
    } finally {
      setLoading(false);
    }
  };

  const confirmForgotPassword = async (email: string, code: string, newPassword: string) => {
    setLoading(true);
    setError('');
    try {
      const result = await callAPI('confirmForgotPassword', { email, code, newPassword });
      if (!result.success) {
        setError(result.error);
      }
      return result;
    } catch (err: any) {
      const errorMsg = err.message || 'Password reset failed';
      setError(errorMsg);
      return { success: false, error: errorMsg };
    } finally {
      setLoading(false);
    }
  };

  const signOut = () => {
    localStorage.removeItem('cognito_tokens');
    setUser(null);
  };

  // Check for existing user on mount
  useEffect(() => {
    const initAuth = async () => {
      await getCurrentUser();
      setLoading(false);
    };
    initAuth();
  }, []);

  const value = {
    user,
    loading,
    error,
    signUp,
    confirmSignUp,
    signIn,
    signOut,
    getCurrentUser,
    forgotPassword,
    confirmForgotPassword
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
