'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';

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
    const token = localStorage.getItem('auth_token');
    if (token) {
      // In a real app, we would validate the token with an API call
      // For now, we'll just assume the token is valid and fetch user data
      fetchUserData(token);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUserData = async (token: string) => {
    try {
      const response = await fetch('http://localhost:8000/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        setUser({
          id: userData.id,
          email: userData.email,
          name: userData.name,
        });
      } else {
        // Token is invalid, clear it
        localStorage.removeItem('auth_token');
      }
    } catch (error) {
      console.error('Error fetching user data:', error);
      localStorage.removeItem('auth_token');
    } finally {
      setLoading(false);
    }
  };

  const signIn = async (email: string, password: string) => {
    // Call the backend authentication API
    const response = await fetch('http://localhost:8000/auth/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    if (response.ok) {
      const { access_token, user } = await response.json();
      localStorage.setItem('auth_token', access_token);
      setUser(user);
      router.push('/dashboard');
    } else {
      const error = await response.json();
      throw new Error(error.detail || 'Sign in failed');
    }
  };

  const signUp = async (name: string, email: string, password: string) => {
    // Call the backend authentication API for sign up
    const response = await fetch('http://localhost:8000/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password }),
    });

    if (response.ok) {
      const { access_token, user } = await response.json();
      localStorage.setItem('auth_token', access_token);
      setUser(user);
      router.push('/dashboard');
    } else {
      const error = await response.json();
      throw new Error(error.detail || 'Sign up failed');
    }
  };

  const signOut = () => {
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