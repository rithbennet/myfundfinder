"use client";

import { ProtectedRoute } from '~/components/ProtectedRoute';
import { useAuth } from '~/feature/auth/model/AuthContext';
import { useRouter } from 'next/navigation';

export default function DashboardPage() {
  const { user, signOut } = useAuth();
  const router = useRouter();

  const handleSignOut = () => {
    signOut();
    router.push('/');
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="mx-auto max-w-4xl">
          <div className="mb-8 flex items-center justify-between">
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <div className="flex items-center gap-4">
              <span>Welcome, {user?.email}</span>
              <button
                onClick={handleSignOut}
                className="rounded bg-red-500 px-4 py-2 text-white hover:bg-red-600"
              >
                Sign Out
              </button>
            </div>
          </div>

          <div className="rounded-lg bg-white p-6 shadow">
            <h2 className="mb-4 text-xl font-semibold">Protected Content</h2>
            <p className="text-gray-600">
              This page is only accessible to authenticated users.
              You can only see this because you're signed in!
            </p>

            <div className="mt-6">
              <button
                onClick={() => router.push('/')}
                className="rounded bg-blue-500 px-4 py-2 text-white hover:bg-blue-600"
              >
                Back to Home
              </button>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
