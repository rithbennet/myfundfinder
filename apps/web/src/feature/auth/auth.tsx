"use client";

import Link from 'next/link';
import { useAuth } from '~/feature/auth/model/AuthContext';

export function AuthButton() {
  const { user, loading, signOut } = useAuth();

  if (loading) return <div className="text-white">Loading...</div>;

  if (user) {
    return (
      <div className="flex items-center gap-4">
        <span className="text-white">Welcome, {user.email}</span>
        <button
          onClick={signOut}
          className="rounded bg-red-500 px-4 py-2 text-white hover:bg-red-600"
        >
          Sign Out
        </button>
      </div>
    );
  }

  return (
    <Link
      href="/login"
      className="rounded bg-blue-500 px-4 py-2 text-white hover:bg-blue-600"
    >
      Sign In
    </Link>
  );
}
