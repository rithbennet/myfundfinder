"use client";

import { useState } from 'react';
import { authApi } from '../api/auth';
import { tokenStorage } from '../lib/storage';

export const useAuthActions = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const signUp = async (email: string, password: string) => {
    setLoading(true);
    setError('');
    try {
      const result = await authApi.signUp(email, password);
      if (!result.success) setError(result.error);
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
      const result = await authApi.confirmSignUp(email, code);
      if (!result.success) setError(result.error);
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
      const result = await authApi.signIn(email, password);
      if (result.success && result.tokens) {
        tokenStorage.set(result.tokens);
        // Set auth cookie
        document.cookie = `auth-token=${result.tokens.AccessToken}; path=/; max-age=3600; secure; samesite=strict`;
        window.location.href = '/dashboard';
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
      const result = await authApi.forgotPassword(email);
      if (!result.success) setError(result.error);
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
      const result = await authApi.confirmForgotPassword(email, code, newPassword);
      if (!result.success) setError(result.error);
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
    tokenStorage.clear();
    // Clear auth cookie
    document.cookie = 'auth-token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
    window.location.href = '/sign-out';
  };

  return {
    signUp,
    confirmSignUp,
    signIn,
    forgotPassword,
    confirmForgotPassword,
    signOut,
    loading,
    error,
  };
};
