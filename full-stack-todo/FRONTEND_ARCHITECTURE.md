## Directory Structure
```
 Directory of D:\VScode\GitHub\From_Console_to_Cloud\full-stack-todo

.next/
app/
components/
context/
lib/
node_modules/
public/
.env
.gitignore
eslint.config.mjs
next-env.d.ts
next.config.ts
package.json
pnpm-lock.yaml
postcss.config.mjs
tsconfig.json
types.ts
```

# app\api\auth\[...betterauth]\route.ts
```typescript
import { auth } from "../../../../lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export const { GET, POST } = toNextJsHandler(auth);
```

# lib\api.ts
```typescript
const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL!;

async function request<T>(path: string, options: RequestInit = {}) {
  const token =
    typeof window !== "undefined"
      ? localStorage.getItem("auth_token")
      : null;

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });

  if (!res.ok) throw new Error("API error");
  const json = await res.json();
  return json.data as T;
}

export const api = {
  getTasks: () => request("/api/tasks"),

  createTask: (data: any) =>
    request("/api/tasks", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateTask: (id: number, data: any) =>
    request(`/api/tasks/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  deleteTask: (id: number) =>
    request(`/api/tasks/${id}`, {
      method: "DELETE",
    }),

  toggleComplete: (id: number) =>
    request(`/api/tasks/${id}/complete`, {
      method: "PATCH",
    }),
};

```

# lib\auth.ts
```typescript
import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { Pool } from "pg";

export const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET!,
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false,
  },
  // We use a manual Pool here to bypass the "Failed to initialize" error
  database: new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: {
      rejectUnauthorized: false, // Required for Neon in some Node environments
    },
  }),
  plugins: [
    jwt()
  ]
});
```

# next-env.d.ts
```typescript
/// <reference types="next" />
/// <reference types="next/image-types/global" />
import "./.next/dev/types/routes.d.ts";

// NOTE: This file should not be edited
// see https://nextjs.org/docs/app/api-reference/config/typescript for more information.

```

# next.config.ts
```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
};

export default nextConfig;

```

# types.ts
```typescript
// types.ts
export interface Task {
  id: number;
  user_id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority: 'low' | 'medium' | 'high';
  category?: string;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: 'low' | 'medium' | 'high';
  category?: string;
  tags?: string[];
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  priority?: 'low' | 'medium' | 'high';
  category?: string;
  tags?: string[];
  completed?: boolean;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
}
```

# app\auth\signin\page.tsx
```tsx
'use client';

import { useState, type FormEvent } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { createAuthClient } from 'better-auth/client';

const auth = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:3000',
});

export default function SignInPage() {
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const router = useRouter();

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const res = await auth.signIn.email({
      email,
      password,
    });

    if (res.error) {
      setError(res.error.message ?? 'Sign in failed');
      setLoading(false);
      return;
    }

    if (res.data?.session?.token) {
      localStorage.setItem('auth_token', res.data.session.token);
      // Hard redirect to clear any state issues
      window.location.href = '/dashboard';
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-black py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-white">
            Sign in to your account
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="text-sm text-red-700">{error}</div>
            </div>
          )}

          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="email" className="sr-only">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div className="-mt-px">
              <label htmlFor="password" className="sr-only">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="text-sm">
              <a href="#" className="font-medium text-indigo-600 hover:text-indigo-500">
                Forgot your password?
              </a>
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </div>
        </form>
        <div className="text-center text-sm text-gray-600">
          Don't have an account?{' '}
          <Link href="/auth/signup" className="font-medium text-indigo-600 hover:text-indigo-500">
            Sign up
          </Link>
        </div>
      </div>
    </div>
  );
}
```

# app\auth\signup\page.tsx
```tsx
'use client';

import { useState, type FormEvent } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { createAuthClient } from 'better-auth/client';

const auth = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:3000',
});

export default function SignUpPage() {
  const [name, setName] = useState<string>('');
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const router = useRouter();

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const res = await auth.signUp.email({
      email,
      password,
      name,
    });

    if (res.error) {
      setError(res.error.message ?? 'Sign up failed');
      setLoading(false);
      return;
    }

    if (res.data?.session?.token) {
      localStorage.setItem('auth_token', res.data.session.token);
      // Hard redirect to clear any state issues
      window.location.href = '/dashboard';
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-black py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-white">
            Create your account
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="text-sm text-red-700">{error}</div>
            </div>
          )}

          <div className="rounded-md shadow-sm -space-y-px bg-white">
            <div>
              <label htmlFor="name" className="sr-only">
                Full Name
              </label>
              <input
                id="name"
                name="name"
                type="text"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Full Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
            <div className="-mt-px">
              <label htmlFor="email" className="sr-only">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div className="-mt-px">
              <label htmlFor="password" className="sr-only">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {loading ? 'Creating account...' : 'Sign up'}
            </button>
          </div>
        </form>
        <div className="text-center text-sm text-gray-600">
          Already have an account?{' '}
          <Link href="/auth/signin" className="font-medium text-indigo-600 hover:text-indigo-500">
            Sign in
          </Link>
        </div>
      </div>
    </div>
  );
}
```

# app\dashboard\page.tsx
```tsx
"use client";

import { useState, useEffect, useCallback } from "react";
import { useAuth } from './../../context/AuthContext';
import { api } from "./../../lib/api";

interface Todo {
  id: number;
  user_id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority: "low" | "medium" | "high";
  category?: string;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export default function DashboardPage() {
  const { user, signOut } = useAuth();
  
  // State Management
  const [todos, setTodos] = useState<Todo[]>([]);
  const [input, setInput] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(true);
  const [addingTodo, setAddingTodo] = useState(false);
  const [updatingTodo, setUpdatingTodo] = useState<number | null>(null);
  const [deletingTodo, setDeletingTodo] = useState<number | null>(null);

  /**
   * API Handlers
   */
  const loadTodos = useCallback(async () => {
    // Check if we have a token before even trying
    const token = localStorage.getItem('auth_token');
    if (!token) {
      console.error("No token found, redirecting to login");
      window.location.href = '/auth/signin';
      return;
    }

    try {
      const fetchedTodos = await api.getTasks();
      // Ensure we are working with an array (backend returns {data: []})
      setTodos(Array.isArray(fetchedTodos) ? fetchedTodos : []);
    } catch (error) {
      console.error('Error loading todos:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  const addTodo = async (e: React.FormEvent) => {
    e.preventDefault(); // Prevent page reload if using a form
    if (!input.trim()) return;

    // Check token before making API call
    const token = localStorage.getItem('auth_token');
    if (!token) {
      window.location.href = '/auth/signin';
      return;
    }

    setAddingTodo(true);
    try {
      const newTodo = await api.createTask({
        title: input,
        description,
        priority: "medium",
        tags: [],
      });
      setTodos((prev) => [...prev, newTodo]);
      setInput("");
      setDescription("");
    } catch (error) {
      console.error('Error adding todo:', error);
    } finally {
      setAddingTodo(false);
    }
  };

  const toggleTodo = async (id: number) => {
    // Check token before making API call
    const token = localStorage.getItem('auth_token');
    if (!token) {
      window.location.href = '/auth/signin';
      return;
    }

    setUpdatingTodo(id);
    try {
      const updated = await api.toggleComplete(id);
      setTodos((prev) => prev.map((t) => (t.id === id ? updated : t)));
    } catch (error) {
      console.error('Error toggling todo:', error);
    } finally {
      setUpdatingTodo(null);
    }
  };

  const deleteTodo = async (id: number) => {
    if (!confirm("Are you sure you want to delete this task?")) return;

    // Check token before making API call
    const token = localStorage.getItem('auth_token');
    if (!token) {
      window.location.href = '/auth/signin';
      return;
    }

    setDeletingTodo(id);
    try {
      await api.deleteTask(id);
      setTodos((prev) => prev.filter((t) => t.id !== id));
    } catch (error) {
      console.error('Error deleting todo:', error);
    } finally {
      setDeletingTodo(null);
    }
  };

  /**
   * Lifecycle
   */
  useEffect(() => {
    loadTodos();
  }, [loadTodos]);

  /**
   * Render Helpers
   */
  if (loading) {
    return (
      <div className="flex flex-col justify-center items-center min-h-screen gap-4">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
        <p className="text-white font-medium">Loading your tasks...</p>
      </div>
    );
  }

  return (
    <main className="max-w-4xl mx-auto p-6 min-h-screen text-gray-100">
      <header className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold">Todo Dashboard</h1>
          <p className="text-gray-400">Welcome back, {user?.name || user?.email}</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={loadTodos}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors text-sm"
          >
            Refresh
          </button>
          <button
            onClick={signOut}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition-colors text-sm font-medium"
          >
            Sign Out
          </button>
        </div>
      </header>

      {/* Input Section */}
      <section className="mb-10 p-6 bg-white rounded-xl shadow-xl border border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Create New Task</h2>
        <form onSubmit={addTodo} className="flex flex-col gap-4">
          <div className="space-y-1">
            <label htmlFor="title" className="text-sm font-medium text-gray-700">Task Title</label>
            <input
              id="title"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="What needs to be done?"
              className="w-full px-4 py-2 border border-gray-300 bg-gray-50 text-gray-900 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
            />
          </div>

          <div className="space-y-1">
            <label htmlFor="description" className="text-sm font-medium text-gray-700">Description (Optional)</label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Add some details..."
              rows={2}
              className="w-full px-4 py-2 border border-gray-300 bg-gray-50 text-gray-900 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all"
            />
          </div>

          <button
            type="submit"
            disabled={addingTodo || !input.trim()}
            className="self-end px-8 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-semibold rounded-lg transition-all shadow-md active:scale-95"
          >
            {addingTodo ? 'Adding...' : 'Add Task'}
          </button>
        </form>
      </section>

      {/* Tasks Section */}
      <section>
        <h2 className="text-2xl font-semibold mb-6 flex items-center gap-2">
          Your Tasks 
          <span className="text-sm bg-gray-800 px-2 py-0.5 rounded-full text-gray-400">
            {todos.length}
          </span>
        </h2>

        {todos.length === 0 ? (
          <article className="p-10 text-center bg-gray-800/50 rounded-xl border border-dashed border-gray-700">
            <p className="text-gray-400">No tasks found. Start by adding one above!</p>
          </article>
        ) : (
          <ul className="grid gap-4">
            {todos.map((todo) => (
              <li
                key={todo.id}
                className="group flex items-center p-4 bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md transition-all"
              >
                <div className="flex items-center h-full pr-4">
                  <input
                    type="checkbox"
                    checked={todo.completed}
                    onChange={() => toggleTodo(todo.id)}
                    disabled={updatingTodo === todo.id}
                    className="h-6 w-6 rounded-full border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer disabled:opacity-50 transition-all"
                    aria-label="Toggle task completion"
                  />
                </div>

                <div className="flex-1 min-w-0">
                  <h3 className={`text-lg font-semibold truncate ${
                    todo.completed ? "line-through text-gray-400" : "text-gray-900"
                  }`}>
                    {todo.title}
                  </h3>
                  {todo.description && (
                    <p className={`text-sm mt-0.5 line-clamp-2 ${
                      todo.completed ? "text-gray-300" : "text-gray-600"
                    }`}>
                      {todo.description}
                    </p>
                  )}
                </div>

                <div className="flex items-center gap-3 ml-4">
                  <span className={`hidden sm:block px-2.5 py-1 rounded-md text-xs font-bold uppercase tracking-wider ${
                    todo.priority === 'high' ? 'bg-red-100 text-red-700' :
                    todo.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-green-100 text-green-700'
                  }`}>
                    {todo.priority}
                  </span>
                  
                  <button
                    onClick={() => deleteTodo(todo.id)}
                    disabled={deletingTodo === todo.id}
                    className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all disabled:opacity-30"
                    title="Delete task"
                  >
                    {deletingTodo === todo.id ? (
                      <span className="text-xs">...</span>
                    ) : (
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                    )}
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
```

# app\layout.tsx
```tsx
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from './../context/AuthContext';

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Todo App",
  description: "A full-stack todo application with authentication",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased `}
      >
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}

```

# app\page.tsx
```tsx
'use client';
import Image from 'next/image';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  const handleLogin = () => {
    router.push('/auth/signin');
  };

  const handleSignup = () => {
    router.push('/auth/signup');
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Background Image */}
      <div className="absolute inset-0 -z-10">
        <Image
          src="/todo.jpg"
          alt="Background"
          layout="fill"
          objectFit="cover"
          className="opacity-20"
        />
      </div>

      <main className="flex-grow flex items-center justify-center p-4">
        <div className="max-w-md w-full space-y-8 bg-white bg-opacity-80 backdrop-blur-sm p-8 rounded-2xl shadow-lg">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Todo App
            </h1>
            <p className="text-lg text-gray-600 mb-8">
              Simple multi-user todo app
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={handleLogin}
                className="px-6 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition"
              >
                Login
              </button>
              <button
                onClick={handleSignup}
                className="px-6 py-3 bg-white text-indigo-600 font-medium rounded-lg border border-indigo-600 hover:bg-indigo-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition"
              >
                Sign Up
              </button>
            </div>
          </div>
        </div>
      </main>
      <footer className="py-4 text-center text-black text-sm bg-white/30 bg-opacity-50 backdrop-blur-sm">
        © {new Date().getFullYear()} Todo App. All rights reserved.
      </footer>
    </div>
  );
}

```

# components\AuthGuard.tsx
```tsx
// frontend/full-stack-todo/components/AuthGuard.tsx
import { usePathname, useRouter } from 'next/navigation';
import { useEffect } from 'react';

interface AuthGuardProps {
  children: React.ReactNode;
  isAuthenticated: boolean;
  onUnauthenticated?: () => void;
}

const AuthGuard: React.FC<AuthGuardProps> = ({ 
  children, 
  isAuthenticated, 
  onUnauthenticated 
}) => {
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated && pathname !== '/auth/signin' && pathname !== '/auth/signup') {
      // Redirect to sign-in page if not authenticated
      router.push('/auth/signin');
      if (onUnauthenticated) {
        onUnauthenticated();
      }
    }
  }, [isAuthenticated, pathname, router, onUnauthenticated]);

  // If not authenticated and trying to access protected route, return null
  // (the redirect effect would handle navigation)
  if (!isAuthenticated && pathname !== '/auth/signin' && pathname !== '/auth/signup') {
    return null; // or a loading component
  }

  return <>{children}</>;
};

export default AuthGuard;
```

# components\LoadingSpinner.tsx
```tsx
'use client';

export default function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-600"></div>
    </div>
  );
}
```

# components\TaskForm.tsx
```tsx
// frontend/full-stack-todo/components/TaskForm.tsx
import React, { useState } from 'react';
import { TaskCreate } from '../types';

interface TaskFormProps {
  onSubmit: (task: TaskCreate) => void;
}

const TaskForm: React.FC<TaskFormProps> = ({ onSubmit }) => {
  const [title, setTitle] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [priority, setPriority] = useState<'low' | 'medium' | 'high'>('medium');
  const [category, setCategory] = useState<string>('');
  const [tags, setTags] = useState<string>('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Create a task object with the form data
    const newTask: TaskCreate = {
      title: title.trim(),
      description: description.trim(),
      priority,
      category: category.trim(),
      tags: tags.split(',').map(tag => tag.trim()).filter(tag => tag)
    };

    // Call the parent onSubmit function with the new task
    onSubmit(newTask);

    // Reset the form
    setTitle('');
    setDescription('');
    setPriority('medium');
    setCategory('');
    setTags('');
  };

  return (
    <form onSubmit={handleSubmit} className="mb-6 p-4 bg-white rounded-lg shadow">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="md:col-span-2">
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
            Title *
          </label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter task title"
          />
        </div>

        <div className="md:col-span-2">
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter task description (optional)"
            rows={2}
          />
        </div>

        <div>
          <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
            Priority
          </label>
          <select
            id="priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value as 'low' | 'medium' | 'high')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>

        <div>
          <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-1">
            Category
          </label>
          <input
            type="text"
            id="category"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter category (optional)"
          />
        </div>

        <div className="md:col-span-2">
          <label htmlFor="tags" className="block text-sm font-medium text-gray-700 mb-1">
            Tags (comma separated)
          </label>
          <input
            type="text"
            id="tags"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter tags separated by commas (optional)"
          />
        </div>
      </div>

      <div className="mt-4">
        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Add Task
        </button>
      </div>
    </form>
  );
};

export default TaskForm;
```

# components\TaskItem.tsx
```tsx
// frontend/full-stack-todo/components/TaskItem.tsx
import React from "react";
import { Task } from "../types";

interface TaskItemProps {
  task: Task;
  onToggle: (taskId: number) => void;
  onDelete: (taskId: number) => void;
}

const TaskItem: React.FC<TaskItemProps> = ({ task, onToggle, onDelete }) => {
  const handleToggle = () => {
    onToggle(task.id);
  };

  const handleDelete = () => {
    onDelete(task.id);
  };

  return (
    <li
      key={task.id}
      className="flex items-center p-4 bg-gray-100 rounded-lg shadow hover:shadow-md transition"
    >
      <input
        placeholder="checkbox"
        type="checkbox"
        checked={task.completed}
        onChange={handleToggle}
        className="mr-4 h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
      />
      <div className="flex-1 min-w-0">
        <p
          className={`truncate ${
            task.completed ? "line-through text-gray-500" : "text-gray-900"
          }`}
        >
          {task.title}
        </p>
        {task.description && (
          <p className="text-sm text-gray-500 truncate">{task.description}</p>
        )}
        {task.category && (
          <span className="inline-block mt-1 px-2 py-0.5 text-xs bg-blue-100 text-blue-800 rounded-full">
            {task.category}
          </span>
        )}
      </div>
      <div className="ml-4 flex items-center space-x-2">
        <span
          className={`px-2 py-1 text-xs rounded-full ${
            task.priority === "high"
              ? "bg-red-100 text-red-800"
              : task.priority === "medium"
              ? "bg-yellow-100 text-yellow-800"
              : "bg-green-100 text-green-800"
          }`}
        >
          {task.priority}
        </span>
        <button
          onClick={handleDelete}
          className="ml-2 bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded-lg transition text-sm"
        >
          Delete
        </button>
      </div>
    </li>
  );
};

export default TaskItem;

```

# components\TaskList.tsx
```tsx
// components/TaskList.tsx
import React from 'react';
import { Task } from '../types';
import TaskItem from './TaskItem';

interface TaskListProps {
  tasks: Task[];
  onToggle: (taskId: number) => void;
  onDelete: (taskId: number) => void;
}

const TaskList: React.FC<TaskListProps> = ({ tasks, onToggle, onDelete }) => {
  if (tasks.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">No tasks yet. Add a new task to get started!</p>
      </div>
    );
  }

  return (
    <ul className="space-y-4">
      {tasks.map((task) => (
        <TaskItem
          key={task.id}
          task={task}
          onToggle={onToggle}
          onDelete={onDelete}
        />
      ))}
    </ul>
  );
};

export default TaskList;
```

# context\AuthContext.tsx
```tsx
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
          const token = session.data.session?.token;
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

    // Store session token for API calls
    if (result.data?.session?.token) {
      localStorage.setItem('auth_token', result.data.session.token);
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

    // Store session token for API calls
    if (result.data?.session?.token) {
      localStorage.setItem('auth_token', result.data.session.token);
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
```

# package.json
```json
{
  "name": "my-app",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint"
  },
  "dependencies": {
    "better-auth": "^1.4.10",
    "next": "16.1.1",
    "pg": "^8.16.3",
    "react": "19.2.3",
    "react-dom": "19.2.3"
  },
  "devDependencies": {
    "@tailwindcss/postcss": "^4",
    "@types/node": "^20",
    "@types/pg": "^8.16.0",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "eslint": "^9",
    "eslint-config-next": "16.1.1",
    "tailwindcss": "^4",
    "typescript": "^5"
  }
}

```

# tsconfig.json
```json
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": [
      "dom",
      "dom.iterable",
      "esnext"
    ],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "incremental": true,
    "module": "esnext",
    "esModuleInterop": true,
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "react-jsx",
    "plugins": [
      {
        "name": "next"
      }
    ]
  },
  "include": [
    "next-env.d.ts",
    ".next/types/**/*.ts",
    ".next/dev/types/**/*.ts",
    "**/*.mts",
    "**/*.ts",
    "**/*.tsx"
  ],
  "exclude": [
    "node_modules"
  ]
}

```

# app\globals.css
```css
@import "tailwindcss";

:root {
  --background: #ffffff;
  --foreground: #171717;
}

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --font-sans: var(--font-geist-sans);
  --font-mono: var(--font-geist-mono);
}

@media (prefers-color-scheme: dark) {
  :root {
    --background: #0a0a0a;
    --foreground: #ededed;
  }
}

body {
  background: var(--background);
  color: var(--foreground);
  font-family: Arial, Helvetica, sans-serif;
}

```

