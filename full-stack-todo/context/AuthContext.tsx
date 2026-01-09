'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { createAuthClient } from 'better-auth/client';

// Initialize Better Auth client
const auth = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:3000',
});

interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (name: string, email: string, password: string) => Promise<void>;
  signOut: () => void;
  getToken: () => string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  // Check for existing session on initial load
  useEffect(() => {
    async function initAuth() {
      try {
        const session = await auth.getSession();
        if (session?.data?.user) {
          // getSession usually nests token inside session, but we check both to be safe
          const token = session.data.session?.token || (session.data as any).token;
          if (token) localStorage.setItem('auth_token', token);

          setUser({
            id: session.data.user.id,
            email: session.data.user.email,
            name: session.data.user.name || session.data.user.email.split('@')[0],
          });
        }
      } catch (err) {
        console.error("Session check failed", err);
      } finally {
        setLoading(false);
      }
    }
    initAuth();
  }, []);

  const signIn = async (email: string, password: string) => {
    const result = await auth.signIn.email({ email, password });
    if (result.error) {
      throw new Error(result.error.message || 'Sign in failed');
    }

    // Per your error message, token is at the root of data for signIn
    const token = result.data?.token;
    if (token) {
      localStorage.setItem('auth_token', token);
      setUser({
        id: result.data.user.id,
        email: result.data.user.email,
        name: result.data.user.name || result.data.user.email.split('@')[0],
      });
    }

    router.push('/dashboard');
  };

  const signUp = async (name: string, email: string, password: string) => {
    const result = await auth.signUp.email({ email, password, name });
    if (result.error) {
      throw new Error(result.error.message || 'Sign up failed');
    }

    // Per your error message, token is at the root of data for signUp
    const token = result.data?.token;
    if (token) {
      localStorage.setItem('auth_token', token);
      setUser({
        id: result.data.user.id,
        email: result.data.user.email,
        name: result.data.user.name || result.data.user.email.split('@')[0],
      });
    }

    router.push('/dashboard');
  };

  const signOut = async () => {
    await auth.signOut();
    localStorage.removeItem('auth_token');
    setUser(null);
    router.push('/auth/signin');
  };

  const getToken = () => {
    return localStorage.getItem('auth_token');
  };

  const value = {
    user,
    loading,
    signIn,
    signUp,
    signOut,
    getToken,
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