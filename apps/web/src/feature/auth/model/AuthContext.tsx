"use client";

import { createContext, useContext, useEffect, useState } from 'react';
import { authApi } from '../api/auth';
import { tokenStorage } from '../lib/storage';

interface User {
  username: string;
  email: string;
  id: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  signOut: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Cache user data to avoid repeated API calls
let userCache: User | null = null;
let lastFetchTime = 0;
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const getCurrentUser = async (forceRefresh = false) => {
    try {
      const tokens = tokenStorage.get();
      if (!tokens?.AccessToken) {
        setUser(null);
        userCache = null;
        return;
      }

      // Use cache if available and not expired
      const now = Date.now();
      if (!forceRefresh && userCache && (now - lastFetchTime) < CACHE_DURATION) {
        setUser(userCache);
        return;
      }

      const result = await authApi.getUser(tokens.AccessToken);
      if (result.success) {
        userCache = result.user;
        lastFetchTime = now;
        setUser(result.user);
      } else {
        tokenStorage.clear();
        userCache = null;
        setUser(null);
      }
    } catch {
      tokenStorage.clear();
      userCache = null;
      setUser(null);
    }
  };

  const signOut = () => {
    tokenStorage.clear();
    userCache = null;
    setUser(null);
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
    signOut,
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
