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
  subscribeToPushNotifications: () => Promise<void>;
  unsubscribeFromPushNotifications: () => Promise<void>;
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

  const subscribeToPushNotifications = async () => {
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
      console.warn('Push messaging is not supported');
      return;
    }

    try {
      // Register the service worker
      const registration = await navigator.serviceWorker.register('/sw.js');

      // Request notification permission
      const permission = await Notification.requestPermission();
      if (permission !== 'granted') {
        console.warn('Notification permission not granted');
        return;
      }

      // Check if VAPID key is available before subscribing
      if (!process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY) {
        console.warn('VAPID public key not configured. Push notifications will not work.');
        return;
      }

      // Subscribe to push notifications
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY),
      });

      // Send subscription to backend
      const subscriptionObj = subscription.toJSON();
      const token = getToken();
      if (token && user) {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/notifications/subscribe`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({
            endpoint: subscriptionObj.endpoint,
            p256dh: subscriptionObj.keys?.p256dh,
            auth: subscriptionObj.keys?.auth,
          }),
        });

        if (!response.ok) {
          throw new Error('Failed to subscribe to notifications');
        }

        console.log('Successfully subscribed to push notifications');
      }
    } catch (error) {
      console.error('Error subscribing to push notifications:', error);
    }
  };

  const unsubscribeFromPushNotifications = async () => {
    try {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.getSubscription();

      if (subscription) {
        await subscription.unsubscribe();

        // Remove subscription from backend
        const token = getToken();
        if (token && user) {
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/notifications/unsubscribe`, {
            method: 'DELETE',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
          });

          if (!response.ok) {
            throw new Error('Failed to unsubscribe from notifications');
          }

          console.log('Successfully unsubscribed from push notifications');
        }
      }
    } catch (error) {
      console.error('Error unsubscribing from push notifications:', error);
    }
  };

  // Helper function to convert base64 string to Uint8Array
  const urlBase64ToUint8Array = (base64String: string) => {
    const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
    const base64 = (base64String + padding)
      .replace(/-/g, '+')
      .replace(/_/g, '/');

    const rawData = atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  };

  const value = {
    user,
    loading,
    signIn,
    signUp,
    signOut,
    getToken,
    subscribeToPushNotifications,
    unsubscribeFromPushNotifications,
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