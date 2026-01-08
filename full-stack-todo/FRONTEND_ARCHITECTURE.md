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
.env.example
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

const handler = auth.handler;

export const GET = handler;
export const POST = handler;
export const OPTIONS = handler;

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

export const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET!,
  database: {
    uri: process.env.DATABASE_URL!,
  },
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false,
  },
  session: {
    expiresIn: 7 * 24 * 60 * 60,
  },
  cookies: {
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
  },
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

    // Store the auth token in localStorage for the API calls
    if (res.data?.session?.token) {
      localStorage.setItem('auth_token', res.data.session.token);
    }

    router.push('/dashboard');
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

    // Store the auth token in localStorage for the API calls
    if (res.data?.session?.token) {
      localStorage.setItem('auth_token', res.data.session.token);
    }

    router.push('/dashboard');
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

import { useState, useEffect } from "react";
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
  const [todos, setTodos] = useState<Todo[]>([]);
  const [input, setInput] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(true);
  const [addingTodo, setAddingTodo] = useState(false);
  const [updatingTodo, setUpdatingTodo] = useState<number | null>(null);
  const [deletingTodo, setDeletingTodo] = useState<number | null>(null);

  useEffect(() => {
    loadTodos();
  }, []);

  if (loading) return <div>Loading...</div>;

  const loadTodos = async () => {
    try {
      const fetchedTodos = await api.getTasks();
      setTodos(fetchedTodos);
    } finally {
      setLoading(false);
    }
  };

  const addTodo = async () => {
    console.log('addTodo called', { input });
    if (!input.trim()) {
      console.log('addTodo cancelled - no input', { input: input.trim() });
      return;
    }

    console.log('Starting to add todo...');
    setAddingTodo(true);
    try {
      console.log('Calling API to create task...');
      const newTodo = await api.createTask({
        title: input,
        description,
        priority: "medium",
        tags: [],
      });
      console.log('Task created successfully:', newTodo);
      setTodos([...todos, newTodo]);
      setInput("");
      setDescription("");
      console.log('State updated, input cleared');
    } catch (error) {
      console.error('Error adding todo:', error);
    } finally {
      console.log('Setting addingTodo to false');
      setAddingTodo(false);
    }
  };

  const toggleTodo = async (id: number) => {
    setUpdatingTodo(id);
    try {
      const updated = await api.toggleComplete(id);
      setTodos(todos.map((t) => (t.id === id ? updated : t)));
    } catch (error) {
      console.error('Error toggling todo:', error);
    } finally {
      setUpdatingTodo(null);
    }
  };

  const deleteTodo = async (id: number) => {
    setDeletingTodo(id);
    try {
      await api.deleteTask(id);
      setTodos(todos.filter((t) => t.id !== id));
    } catch (error) {
      console.error('Error deleting todo:', error);
    } finally {
      setDeletingTodo(null);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 min-h-screen">
      <header className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-white">Todo Dashboard</h1>
        <div className="flex items-center gap-4">
          <span className="text-white">
            Welcome, {user?.name || user?.email}
          </span>
          <button
            onClick={loadTodos}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            Refresh
          </button>
          <button
            onClick={signOut}
            className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
          >
            Sign Out
          </button>
        </div>
      </header>

      <div className="mb-8 p-6 bg-white rounded-lg shadow">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Add New Todo
        </h2>

        <div className="flex flex-col gap-4">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Add a new todo"
            className="px-4 py-2 border border-gray-300 bg-white text-gray-900 placeholder-gray-400 rounded-lg focus:ring-2 focus:ring-blue-500"
          />

          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Description (optional)"
            rows={2}
            className="px-4 py-2 border border-gray-300 bg-white text-gray-900 placeholder-gray-400 rounded-lg focus:ring-2 focus:ring-blue-500"
          />

          <button
            onClick={addTodo}
            disabled={addingTodo}
            className={`self-start px-6 py-2 rounded-lg ${
              addingTodo
                ? 'bg-blue-400 cursor-not-allowed'
                : 'bg-blue-500 hover:bg-blue-600'
            } text-white`}
          >
            {addingTodo ? 'Adding...' : 'Add Todo'}
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-10">
          <div className="h-10 w-10 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
        </div>
      ) : (
        <div>
          <h2 className="text-2xl font-semibold text-white mb-4">
            Your Todos
          </h2>

          {todos.length === 0 ? (
            <p className="text-gray-600 text-center">No todos yet.</p>
          ) : (
            <ul className="space-y-4">
              {todos.map((todo) => (
                <li
                  key={todo.id}
                  className="flex items-center p-4 bg-white text-gray-900 rounded-lg shadow"
                >
                  <input
                    placeholder="checkbox"
                    type="checkbox"
                    checked={todo.completed}
                    onChange={() => toggleTodo(todo.id)}
                    disabled={updatingTodo === todo.id}
                    className={`mr-4 h-5 w-5 ${
                      updatingTodo === todo.id ? 'cursor-not-allowed opacity-50' : 'accent-blue-600'
                    }`}
                  />

                  <div className="flex-1">
                    <p
                      className={
                        todo.completed
                          ? "line-through text-gray-400 font-medium"
                          : "font-medium text-gray-900"
                      }
                    >
                      {todo.title}
                    </p>

                    {todo.description && (
                      <p className="text-gray-700 text-sm mt-1">
                        {todo.description}
                      </p>
                    )}
                  </div>

                  <button
                    onClick={() => deleteTodo(todo.id)}
                    disabled={deletingTodo === todo.id}
                    className={`ml-4 px-4 py-2 rounded-lg ${
                      deletingTodo === todo.id
                        ? 'bg-red-400 cursor-not-allowed'
                        : 'bg-red-500 hover:bg-red-600'
                    } text-white`}
                  >
                    {deletingTodo === todo.id ? 'Deleting...' : 'Delete'}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
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
    // Get current session from Better Auth
    auth.getSession().then((session) => {
      if (session?.data?.user) {
        setUser({
          id: session.data.user.id,
          email: session.data.user.email,
          name: session.data.user.name || session.data.user.email.split('@')[0],
        });
      }
      setLoading(false);
    }).catch(() => {
      // If session is invalid, clear any stored tokens
      localStorage.removeItem('auth_token');
      setLoading(false);
    });
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
    "react": "19.2.3",
    "react-dom": "19.2.3"
  },
  "devDependencies": {
    "@tailwindcss/postcss": "^4",
    "@types/node": "^20",
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

