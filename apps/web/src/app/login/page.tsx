"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '~/feature/auth/model/AuthContext';

export default function LoginPage() {
  const { user, loading, error, signUp, confirmSignUp, signIn, getCurrentUser, forgotPassword, confirmForgotPassword } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmationCode, setConfirmationCode] = useState('');
  const [mode, setMode] = useState<'signin' | 'signup' | 'confirm' | 'forgot' | 'reset'>('signin');
  const [message, setMessage] = useState('');
  const router = useRouter();

  useEffect(() => {
    getCurrentUser();
  }, []);

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await signUp(email, password);
    if (result.success) {
      setMessage('Check your email for confirmation code');
      setMode('confirm');
    }
  };

  const handleConfirm = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await confirmSignUp(email, confirmationCode);
    if (result.success) {
      setMessage('Account confirmed! You can now sign in.');
      setMode('signin');
    }
  };

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await signIn(email, password);
    if (result.success) {
      router.push('/');
    }
  };

  const handleForgotPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await forgotPassword(email);
    if (result.success) {
      setMessage('Check your email for reset code');
      setMode('reset');
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await confirmForgotPassword(email, confirmationCode, newPassword);
    if (result.success) {
      setMessage('Password reset successful! You can now sign in.');
      setMode('signin');
    }
  };

  if (user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="w-full max-w-md space-y-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-gray-900">Welcome!</h2>
            <p className="mt-2 text-gray-600">Signed in as {user.email}</p>
          </div>
          <button
            onClick={() => router.push('/')}
            className="w-full rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
          >
            Go to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900">
            {mode === 'signin' && 'Sign In'}
            {mode === 'signup' && 'Sign Up'}
            {mode === 'confirm' && 'Confirm Account'}
            {mode === 'forgot' && 'Forgot Password'}
            {mode === 'reset' && 'Reset Password'}
          </h2>
        </div>

        {error && (
          <div className="rounded-md bg-red-50 p-4 text-red-700">{error}</div>
        )}

        {message && (
          <div className="rounded-md bg-green-50 p-4 text-green-700">{message}</div>
        )}

        {mode === 'signin' && (
          <form onSubmit={handleSignIn} className="space-y-4">
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-md border px-3 py-2"
              required
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-md border px-3 py-2"
              required
            />
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Signing In...' : 'Sign In'}
            </button>
            <button
              type="button"
              onClick={() => setMode('signup')}
              className="w-full text-blue-600 hover:text-blue-800"
            >
              Need an account? Sign Up
            </button>
            <button
              type="button"
              onClick={() => setMode('forgot')}
              className="w-full text-gray-600 hover:text-gray-800"
            >
              Forgot Password?
            </button>
          </form>
        )}

        {mode === 'signup' && (
          <form onSubmit={handleSignUp} className="space-y-4">
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-md border px-3 py-2"
              required
            />
            <input
              type="password"
              placeholder="Password (min 8 chars, uppercase, lowercase, number, symbol)"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-md border px-3 py-2"
              required
            />
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700 disabled:opacity-50"
            >
              {loading ? 'Creating Account...' : 'Sign Up'}
            </button>
            <button
              type="button"
              onClick={() => setMode('signin')}
              className="w-full text-blue-600 hover:text-blue-800"
            >
              Already have an account? Sign In
            </button>
          </form>
        )}

        {mode === 'confirm' && (
          <form onSubmit={handleConfirm} className="space-y-4">
            <input
              type="text"
              placeholder="Confirmation Code"
              value={confirmationCode}
              onChange={(e) => setConfirmationCode(e.target.value)}
              className="w-full rounded-md border px-3 py-2"
              required
            />
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Confirming...' : 'Confirm Account'}
            </button>
          </form>
        )}

        {mode === 'forgot' && (
          <form onSubmit={handleForgotPassword} className="space-y-4">
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-md border px-3 py-2"
              required
            />
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Sending...' : 'Send Reset Code'}
            </button>
            <button
              type="button"
              onClick={() => setMode('signin')}
              className="w-full text-blue-600 hover:text-blue-800"
            >
              Back to Sign In
            </button>
          </form>
        )}

        {mode === 'reset' && (
          <form onSubmit={handleResetPassword} className="space-y-4">
            <input
              type="text"
              placeholder="Reset Code"
              value={confirmationCode}
              onChange={(e) => setConfirmationCode(e.target.value)}
              className="w-full rounded-md border px-3 py-2"
              required
            />
            <input
              type="password"
              placeholder="New Password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="w-full rounded-md border px-3 py-2"
              required
            />
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Resetting...' : 'Reset Password'}
            </button>
          </form>
        )}

        <button
          onClick={() => router.push('/')}
          className="w-full rounded-md bg-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-400"
        >
          Back to Home
        </button>
      </div>
    </div>
  );
}
