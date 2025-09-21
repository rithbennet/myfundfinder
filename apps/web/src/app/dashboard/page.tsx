"use client";

import { ProtectedRoute } from '~/components/ProtectedRoute';
import { useAuth } from '~/feature/auth/model/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { getUserCompanies } from './actions';

interface Company {
  companies: {
    id: number;
    company_name: string;
    company_id: string | null;
    sector: string | null;
    location: string | null;
    revenue: number | null;
    employees: number | null;
  }
}

export default function DashboardPage() {
  const { user, signOut } = useAuth();
  const router = useRouter();
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchCompanies() {
      if (!user?.id) return;
      
      const result = await getUserCompanies(user.id);
      if (result.success) {
        setCompanies(result.data as Company[]);
      } else {
        setError(result.error || 'Failed to load companies');
      }
      setLoading(false);
    }

    fetchCompanies();
  }, [user?.id]);

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

          {/* Companies Section */}
          <div className="mb-8 rounded-lg bg-white p-6 shadow">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-xl font-semibold">Your Companies</h2>
              <button
                onClick={() => router.push('/dashboard/onboard')}
                className="rounded bg-blue-500 px-4 py-2 text-white hover:bg-blue-600"
              >
                Add New Company
              </button>
            </div>

            {loading ? (
              <div className="text-center text-gray-500">Loading...</div>
            ) : error ? (
              <div className="text-center text-red-500">{error}</div>
            ) : companies.length === 0 ? (
              <div className="text-center text-gray-500">
                No companies found. Add your first company to get started!
              </div>
            ) : (
              <div className="grid gap-4">
                {companies.map((userCompany) => (
                  <div
                    key={userCompany.companies.id}
                    className="rounded-lg border border-gray-200 p-4 hover:border-blue-500"
                  >
                    <h3 className="text-lg font-medium">{userCompany.companies.company_name}</h3>
                    <div className="mt-2 grid grid-cols-2 gap-4 text-sm text-gray-600">
                      {userCompany.companies.company_id && (
                        <div>
                          <span className="font-medium">Registration No:</span>{' '}
                          {userCompany.companies.company_id}
                        </div>
                      )}
                      {userCompany.companies.sector && (
                        <div>
                          <span className="font-medium">Sector:</span>{' '}
                          {userCompany.companies.sector}
                        </div>
                      )}
                      {userCompany.companies.location && (
                        <div>
                          <span className="font-medium">Location:</span>{' '}
                          {userCompany.companies.location}
                        </div>
                      )}
                      {userCompany.companies.employees && (
                        <div>
                          <span className="font-medium">Employees:</span>{' '}
                          {userCompany.companies.employees}
                        </div>
                      )}
                      {userCompany.companies.revenue && (
                        <div>
                          <span className="font-medium">Revenue:</span> RM{' '}
                          {userCompany.companies.revenue.toLocaleString()}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Protected Content Section */}
          <div className="rounded-lg bg-white p-6 shadow">
            <h2 className="mb-4 text-xl font-semibold">Protected Content</h2>
            <p className="text-gray-600">
              This page is only accessible to authenticated users.
              You can only see this because you&apos;re signed in!
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