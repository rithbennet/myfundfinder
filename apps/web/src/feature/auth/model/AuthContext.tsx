"use client";

import { createContext, useContext, useEffect, useState } from 'react';
import { authApi } from '../api/auth';
import { tokenStorage } from '../lib/storage';

interface User {
  username: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const getCurrentUser = async () => {
    try {
      const tokens = tokenStorage.get();
      if (!tokens?.AccessToken) {
        setUser(null);
        return;
      }

      const result = await authApi.getUser(tokens.AccessToken);
      if (result.success) {
        setUser(result.user);
      } else {
        tokenStorage.clear();
        setUser(null);
      }
    } catch {
      tokenStorage.clear();
      setUser(null);
    }
  };

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
    isAuthenticated: !!user,
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
