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

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "API error");
  }
  
  const json = await res.json();
  return json.data as T;
}

export const api = {
  getTasks: () => request<any[]>("/api/tasks"),

  createTask: (data: any) =>
    request<any>("/api/tasks", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateTask: (id: number, data: any) =>
    request<any>(`/api/tasks/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  deleteTask: (id: number) =>
    request<any>(`/api/tasks/${id}`, {
      method: "DELETE",
    }),

  toggleComplete: (id: number) =>
    request<any>(`/api/tasks/${id}/complete`, {
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
import { createAuthClient } from 'better-auth/client';

const auth = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:3000',
});

export default function SignInPage() {
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await auth.signIn.email({ email, password });

      if (res.error) {
        setError(res.error.message ?? 'Sign in failed');
        setLoading(false);
        return;
      }

      const token = res.data?.token;

      if (token) {
        localStorage.setItem('auth_token', token);
        window.location.href = '/dashboard';
      }
    } catch (err) {
      console.error("Signin error:", err);
      setLoading(false);
      setError("An error occurred during sign in.");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-black py-12 px-4 sm:px-6 lg:px-8 text-gray-900">
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

          <div className="rounded-md shadow-sm -space-y-px bg-white">
            <div>
              <input
                type="email"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <input
                type="password"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
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
              className="w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50"
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </div>
        </form>
        <div className="text-center text-sm text-gray-400">
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

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      console.log("Attempting signup for:", email);
      const res = await auth.signUp.email({
        email,
        password,
        name,
      });

      console.log("Signup Response:", res);

      if (res.error) {
        setError(res.error.message ?? 'Sign up failed');
        setLoading(false);
        return;
      }

      // Fixed: Accessing token directly as per the error message
      const token = res.data?.token;

      if (token) {
        localStorage.setItem('auth_token', token);
        console.log("Token saved, performing hard redirect...");
        window.location.href = '/dashboard';
      } else {
        console.warn("User created but no session token found. Redirecting to sign-in.");
        window.location.href = '/auth/signin';
      }
    } catch (err) {
      console.error("Critical Signup Error:", err);
      setLoading(false);
      setError("An unexpected error occurred. Please try signing in.");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-black py-12 px-4 sm:px-6 lg:px-8 text-gray-900">
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
              <input
                type="text"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Full Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
            <div>
              <input
                type="email"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <input
                type="password"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
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
        <div className="text-center text-sm text-gray-400">
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
import { useAuth } from "./../../context/AuthContext";
import { api } from "./../../lib/api";
import { LogOutIcon } from "lucide-react";

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
  const [loading, setLoading] = useState(true);

  // Form States
  const [input, setInput] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<"low" | "medium" | "high">("medium");

  // UI States
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingTodo, setEditingTodo] = useState<Todo | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const loadTodos = useCallback(async () => {
    try {
      const fetchedTodos = await api.getTasks();
      setTodos(Array.isArray(fetchedTodos) ? fetchedTodos : []);
    } catch (error) {
      console.error("API Error:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTodos();
  }, [loadTodos]);

  const handleAddTodo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    setIsSubmitting(true);
    try {
      const newTodo = await api.createTask({
        title: input,
        description,
        priority,
        tags: [],
      });
      setTodos((prev) => [newTodo, ...prev]);
      resetForm();
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdateTodo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingTodo || !input.trim()) return;
    setIsSubmitting(true);
    try {
      const updated = await api.updateTask(editingTodo.id, {
        title: input,
        description,
        priority,
      });
      setTodos((prev) =>
        prev.map((t) => (t.id === editingTodo.id ? updated : t))
      );
      resetForm();
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const toggleTodo = async (id: number) => {
    try {
      const updated = await api.toggleComplete(id);
      setTodos((prev) => prev.map((t) => (t.id === id ? updated : t)));
    } catch (err) {
      console.error(err);
    }
  };

  const deleteTodo = async (id: number) => {
    if (!confirm("Delete this task?")) return;
    try {
      await api.deleteTask(id);
      setTodos((prev) => prev.filter((t) => t.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  const openEditModal = (todo: Todo) => {
    setEditingTodo(todo);
    setInput(todo.title);
    setDescription(todo.description || "");
    setPriority(todo.priority);
    setShowAddModal(true);
  };

  const resetForm = () => {
    setInput("");
    setDescription("");
    setPriority("medium");
    setEditingTodo(null);
    setShowAddModal(false);
  };

  const completedCount = todos.filter((t) => t.completed).length;

  if (loading)
    return (
      <div className="flex justify-center items-center min-h-screen bg-[#020617]">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-indigo-500 border-t-transparent" />
      </div>
    );

  return (
    <main className="min-h-screen bg-[#020617] text-slate-200 pb-24 font-sans">
      {/* Visual Background Glows */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-indigo-600/10 blur-[120px] rounded-full" />
        <div className="absolute bottom-[10%] right-[-5%] w-[40%] h-[40%] bg-purple-600/10 blur-[100px] rounded-full" />
      </div>

      <div className="max-w-xl mx-auto px-5 pt-10 relative z-10">
        {/* Header */}
        <header className="flex justify-between items-center mb-10">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-white">
              Focus
            </h1>
            <p className="text-slate-500 text-sm font-medium">
              Hello, {user?.name?.split(" ")[0] || "Achiever"}
            </p>
          </div>
          <button
            onClick={signOut}
            className="bg-slate-800/50 p-2 rounded-lg border border-slate-700/50 hover:bg-red-500/10 hover:border-red-500/50 transition-all"
            title="Sign out"
            aria-label="Sign out"
          >
            <LogOutIcon />
          </button>
        </header>

        {/* Stats Row */}
        <div className="grid grid-cols-3 gap-4 mb-10">
          <StatBox label="Total" val={todos.length} color="text-indigo-400" />
          <StatBox
            label="Active"
            val={todos.length - completedCount}
            color="text-amber-400"
          />
          <StatBox label="Done" val={completedCount} color="text-emerald-400" />
        </div>

        {/* Task List */}
        <section className="space-y-4">
          <h2 className="text-xs font-bold uppercase tracking-[0.2em] text-slate-500 mb-6">
            Upcoming Tasks
          </h2>
          {todos.length === 0 ? (
            <div className="text-center py-20 bg-slate-900/20 rounded-3xl border border-dashed border-slate-800">
              <p className="text-slate-500 italic">You're all caught up! ☕</p>
            </div>
          ) : (
            todos.map((todo) => (
              <div
                key={todo.id}
                className={`group relative overflow-hidden flex items-center p-4 rounded-xl transition-all border backdrop-blur-md ${
                  todo.completed
                    ? "bg-slate-900/20 border-slate-800/50"
                    : "bg-slate-800/40 border-slate-700/50 shadow-lg"
                }`}
              >
                {/* Priority Indicator Line */}
                <div
                  className={`absolute left-0 top-0 bottom-0 w-1.5 ${
                    todo.priority === "high"
                      ? "bg-red-500"
                      : todo.priority === "medium"
                      ? "bg-amber-500"
                      : "bg-emerald-500"
                  }`}
                />

                <button
                  onClick={() => toggleTodo(todo.id)}
                  className={`h-7 w-7 rounded-xl border-2 flex items-center justify-center transition-all ${
                    todo.completed
                      ? "bg-indigo-600 border-indigo-600"
                      : "border-slate-600 hover:border-indigo-500"
                  }`}
                >
                  {todo.completed && (
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-4 w-4 text-white"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                </button>

                <div
                  className="flex-1 ml-4 min-w-0"
                  onClick={() => openEditModal(todo)}
                >
                  <h3
                    className={`font-bold truncate ${
                      todo.completed
                        ? "text-slate-600 line-through"
                        : "text-white"
                    }`}
                  >
                    {todo.title}
                  </h3>
                  {todo.description && (
                    <p className="text-xs text-slate-500 truncate mt-0.5">
                      {todo.description}
                    </p>
                  )}
                </div>

                <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    title="openEditModal"
                    aria-label="openEditModal"
                    onClick={() => openEditModal(todo)}
                    className="p-2 text-slate-400 hover:text-indigo-400"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-5 w-5"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
                      />
                    </svg>
                  </button>
                  <button
                    title="deleteTodo"
                    aria-label="deleteTodo"
                    onClick={() => deleteTodo(todo.id)}
                    className="p-2 text-slate-400 hover:text-red-500"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-5 w-5"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                      />
                    </svg>
                  </button>
                </div>
              </div>
            ))
          )}
        </section>
      </div>

      {/* Mobile FAB */}
      <button
        title="resetForm"
        aria-label="resetForm"
        onClick={() => {
          resetForm();
          setShowAddModal(true);
        }}
        className="fixed bottom-8 right-8 h-16 w-16 bg-indigo-600 rounded-full shadow-[0_10px_30px_rgba(79,70,229,0.4)] flex items-center justify-center hover:scale-110 active:scale-95 transition-all z-50"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-8 w-8 text-white"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={3}
            d="M12 4v16m8-8H4"
          />
        </svg>
      </button>

      {/* Add/Edit Modal Overlay */}
      {showAddModal && (
        <div className="fixed inset-0 z-60 flex items-end sm:items-center justify-center p-0 sm:p-4">
          <div
            className="absolute inset-0 bg-[#020617]/80 backdrop-blur-sm"
            onClick={resetForm}
          />
          <div className="relative w-full max-w-lg bg-slate-900 border-t sm:border border-slate-800 rounded-t-[40px] sm:rounded-[40px] p-8 animate-in slide-in-from-bottom-10 duration-300">
            <div className="w-12 h-1.5 bg-slate-800 rounded-full mx-auto mb-8 sm:hidden" />
            <h2 className="text-2xl font-bold text-white mb-6">
              {editingTodo ? "Edit Task" : "New Task"}
            </h2>

            <form
              onSubmit={editingTodo ? handleUpdateTodo : handleAddTodo}
              className="space-y-5"
            >
              <div>
                <label className="text-xs font-bold text-slate-500 uppercase ml-1">
                  Title
                </label>
                <input
                  required
                  autoFocus
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  className="w-full mt-2 bg-slate-800 border-none rounded-2xl px-5 py-4 text-white focus:ring-2 focus:ring-indigo-500 outline-none"
                  placeholder="What needs doing?"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-slate-500 uppercase ml-1">
                  Notes
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full mt-2 bg-slate-800 border-none rounded-2xl px-5 py-4 text-white focus:ring-2 focus:ring-indigo-500 outline-none"
                  placeholder="Additional details..."
                  rows={3}
                />
              </div>

              <div className="flex gap-3">
                <PriorityBtn
                  label="Low"
                  current={priority}
                  set={setPriority}
                  val="low"
                  color="bg-emerald-500"
                />
                <PriorityBtn
                  label="Mid"
                  current={priority}
                  set={setPriority}
                  val="medium"
                  color="bg-amber-500"
                />
                <PriorityBtn
                  label="High"
                  current={priority}
                  set={setPriority}
                  val="high"
                  color="bg-red-500"
                />
              </div>

              <button
                type="submit"
                disabled={isSubmitting || !input.trim()}
                className="w-full bg-indigo-600 hover:bg-indigo-500 py-4 rounded-2xl font-bold text-white shadow-lg transition-all active:scale-95 disabled:opacity-50 mt-4"
              >
                {isSubmitting
                  ? "Saving..."
                  : editingTodo
                  ? "Update Task"
                  : "Create Task"}
              </button>
            </form>
          </div>
        </div>
      )}
    </main>
  );
}

// Components
function StatBox({
  label,
  val,
  color,
}: {
  label: string;
  val: number;
  color: string;
}) {
  return (
    <div className="bg-slate-800/30 border border-slate-800/50 p-4 rounded-2xl text-center backdrop-blur-sm">
      <p className={`text-2xl font-black ${color}`}>{val}</p>
      <p className="text-[10px] font-bold uppercase tracking-widest text-slate-500 mt-1">
        {label}
      </p>
    </div>
  );
}

function PriorityBtn({ label, current, set, val, color }: any) {
  const active = current === val;
  return (
    <button
      type="button"
      onClick={() => set(val)}
      className={`flex-1 py-3 rounded-xl text-xs font-bold uppercase tracking-wider transition-all border-2 ${
        active
          ? `${color} border-transparent text-white`
          : "bg-transparent border-slate-800 text-slate-500 hover:border-slate-700"
      }`}
    >
      {label}
    </button>
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
    <html lang="en" suppressHydrationWarning={true}>
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

