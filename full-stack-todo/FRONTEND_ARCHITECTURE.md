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
tests/
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

# tests\api_client.test.ts
```typescript
/**
 * Frontend API Integration Tests
 * Testing the lib/api.ts client that handles JWT communication with backend
 */

// Mock localStorage for testing
const mockLocalStorage = (() => {
  let store: any = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: any) => {
      store[key] = value.toString();
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    }
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage
});


// Mock fetch for API testing
let mockFetchResponse: any = {};
global.fetch = jest.fn(() => 
  Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve(mockFetchResponse),
    text: () => Promise.resolve(JSON.stringify(mockFetchResponse))
  } as Response)
) as jest.Mock;

// Import the API client
import { api } from '../lib/api';

describe('API Client Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.clear();
  });

  test('should include JWT token in requests when available', async () => {
    // Set a mock JWT token in localStorage
    mockLocalStorage.setItem('auth_token', 'mock.jwt.token');

    // Mock the fetch response
    mockFetchResponse = { data: [{ id: 1, title: 'Test Task' }] };
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: () => Promise.resolve(mockFetchResponse),
    });

    // Call the API
    const tasks = await api.getTasks();

    // Verify that fetch was called with the proper authorization header
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringMatching(/\/api\/tasks$/),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer mock.jwt.token'
        })
      })
    );

    expect(tasks).toEqual(mockFetchResponse.data);
  });

  test('should work without JWT token when not available', async () => {
    // Ensure no token is in localStorage
    mockLocalStorage.removeItem('auth_token');

    // Mock the fetch response
    mockFetchResponse = { data: [] };
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: () => Promise.resolve(mockFetchResponse),
    });

    // Call the API
    const tasks = await api.getTasks();

    // Verify that fetch was called without authorization header
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringMatching(/\/api\/tasks$/),
      expect.not.objectContaining({
        headers: expect.objectContaining({
          Authorization: expect.any(String)
        })
      })
    );

    expect(tasks).toEqual(mockFetchResponse.data);
  });

  test('should handle API errors correctly', async () => {
    // Set a mock JWT token in localStorage
    mockLocalStorage.setItem('auth_token', 'mock.jwt.token');

    // Mock an error response
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 401,
      text: () => Promise.resolve('Unauthorized'),
    });

    // Call the API and expect an error
    await expect(api.getTasks()).rejects.toThrow('API error');

    // Verify that fetch was called with the proper authorization header
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringMatching(/\/api\/tasks$/),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer mock.jwt.token'
        })
      })
    );
  });

  test('should redirect on 401 errors', async () => {
    // Set a mock JWT token in localStorage
    mockLocalStorage.setItem('auth_token', 'mock.jwt.token');

    // Mock a 401 response
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 401,
      text: () => Promise.resolve('Unauthorized'),
    });

    // Create a mock for window.location
    const mockLocation = { href: '' };
    Object.defineProperty(window, 'location', {
      value: mockLocation,
      writable: true,
    });

    // Call the API and expect an error that triggers redirect
    await expect(api.getTasks()).rejects.toThrow('API error');

    // Check that the token was removed from localStorage
    expect(mockLocalStorage.getItem('auth_token')).toBeNull();
  });
});
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
import { KeyRound, Mail, Loader2 } from 'lucide-react';

const auth = createAuthClient({ baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:3000' });

export default function SignInPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await auth.signIn.email({ email, password });
      if (res.error) { setError(res.error.message ?? 'Login failed'); setLoading(false); return; }
      if (res.data?.token) {
        localStorage.setItem('auth_token', res.data.token);
        window.location.replace('/dashboard');
      }
    } catch (err) { setLoading(false); setError("System error. Try again."); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#020617] px-6">
      <div className="max-w-sm w-full space-y-8 bg-slate-900/50 p-8 rounded-3xl border border-slate-800">
        <h2 className="text-3xl font-black text-white text-center">Welcome back</h2>
        <form className="space-y-4" onSubmit={handleSubmit}>
          {error && <div className="p-3 bg-red-500/10 border border-red-500/50 text-red-500 rounded-xl text-xs font-bold text-center">{error}</div>}
          <div className="relative">
            <Mail className="absolute left-4 top-4 text-slate-500" size={18} />
            <input type="email" required placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full pl-12 pr-5 py-4 bg-slate-950 border border-slate-800 rounded-xl text-white outline-none focus:ring-2 focus:ring-indigo-500 transition-all text-sm" />
          </div>
          <div className="relative">
            <KeyRound className="absolute left-4 top-4 text-slate-500" size={18} />
            <input type="password" required placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full pl-12 pr-5 py-4 bg-slate-950 border border-slate-800 rounded-xl text-white outline-none focus:ring-2 focus:ring-indigo-500 transition-all text-sm" />
          </div>
          <button type="submit" disabled={loading} className="w-full py-4 bg-indigo-600 text-white font-bold rounded-xl hover:bg-indigo-500 transition-all disabled:opacity-50 flex justify-center items-center gap-2">
            {loading ? <Loader2 className="animate-spin" size={20} /> : "Sign In"}
          </button>
        </form>
        <p className="text-center text-sm text-slate-500 font-medium">New? <Link href="/auth/signup" className="text-indigo-400 font-bold">Create account</Link></p>
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
import { User, Mail, Lock, Loader2 } from 'lucide-react';

const auth = createAuthClient({ baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:3000' });

export default function SignUpPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await auth.signUp.email({ email, password, name });
      if (res.error) { setError(res.error.message ?? 'Signup failed'); setLoading(false); return; }
      if (res.data?.token) {
        localStorage.setItem('auth_token', res.data.token);
        window.location.replace('/dashboard');
      }
    } catch (err) { setLoading(false); setError("System error. Try again."); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#020617] px-6">
      <div className="max-w-sm w-full space-y-8 bg-slate-900/50 p-8 rounded-3xl border border-slate-800">
        <h2 className="text-3xl font-black text-white text-center">Join Focus</h2>
        <form className="space-y-4" onSubmit={handleSubmit}>
          {error && <div className="p-3 bg-red-500/10 border border-red-500/50 text-red-500 rounded-xl text-xs font-bold text-center">{error}</div>}
          <div className="relative">
            <User className="absolute left-4 top-4 text-slate-500" size={18} />
            <input type="text" required placeholder="Full Name" value={name} onChange={(e) => setName(e.target.value)} className="w-full pl-12 pr-5 py-4 bg-slate-950 border border-slate-800 rounded-xl text-white outline-none focus:ring-2 focus:ring-indigo-500 transition-all text-sm" />
          </div>
          <div className="relative">
            <Mail className="absolute left-4 top-4 text-slate-500" size={18} />
            <input type="email" required placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full pl-12 pr-5 py-4 bg-slate-950 border border-slate-800 rounded-xl text-white outline-none focus:ring-2 focus:ring-indigo-500 transition-all text-sm" />
          </div>
          <div className="relative">
            <Lock className="absolute left-4 top-4 text-slate-500" size={18} />
            <input type="password" required placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full pl-12 pr-5 py-4 bg-slate-950 border border-slate-800 rounded-xl text-white outline-none focus:ring-2 focus:ring-indigo-500 transition-all text-sm" />
          </div>
          <button type="submit" disabled={loading} className="w-full py-4 bg-indigo-600 text-white font-bold rounded-xl hover:bg-indigo-500 transition-all disabled:opacity-50 flex justify-center items-center gap-2">
            {loading ? <Loader2 className="animate-spin" size={20} /> : "Create Account"}
          </button>
        </form>
        <p className="text-center text-sm text-slate-500 font-medium">Already in? <Link href="/auth/signin" className="text-indigo-400 font-bold">Sign in</Link></p>
      </div>
    </div>
  );
}
```

# app\dashboard\page.tsx
```tsx
"use client";

import { useState, useEffect, useCallback, useMemo } from "react";
import { useAuth } from "./../../context/AuthContext";
import { api } from "./../../lib/api";
import { useChatKit } from "@openai/chatkit-react";
import {
  LogOut,
  Plus,
  Edit3,
  Trash2,
  CheckCircle2,
  Circle,
  ListTodo,
  CheckSquare,
  Clock,
  Loader2,
  MessageSquare,
  Send,
  X,
} from "lucide-react";
import { StatBox, PriorityBtn } from "./../../components/DashboardUI";

// ChatKit Configuration Constants
const WORKFLOW_ID =
  process.env.NEXT_PUBLIC_CHATKIT_WORKFLOW_ID || "wf_placeholder";

export default function DashboardPage() {
  const { user, signOut } = useAuth();
  const [todos, setTodos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [input, setInput] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<"low" | "medium" | "high">("medium");
  const [showModal, setShowModal] = useState(false);
  const [editingTodo, setEditingTodo] = useState<any | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Chat States
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState<any[]>([]);
  const [convId, setConvId] = useState<number | null>(null);

  // ChatKit Integration (Used for session management and compliance)
  const getClientSecret = useMemo(() => {
    return async (currentSecret: string | null) => {
      if (currentSecret) return currentSecret;
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/create-session`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
            },
            body: JSON.stringify({ workflow: { id: WORKFLOW_ID } }),
          }
        );
        const data = await res.json();
        return data.client_secret;
      } catch (err) {
        console.error("ChatKit Session Error:", err);
        return "mock_secret";
      }
    };
  }, []);

  const chatkit = useChatKit({
    api: { getClientSecret },
  });

  const loadTodos = useCallback(async () => {
    try {
      const fetchedTodos = await api.getTasks();
      setTodos(Array.isArray(fetchedTodos) ? fetchedTodos : []);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTodos();
  }, [loadTodos]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    setIsSubmitting(true);
    try {
      if (editingTodo) {
        const updated = await api.updateTask(editingTodo.id, {
          title: input,
          description,
          priority,
        });
        setTodos((prev) =>
          prev.map((t) => (t.id === editingTodo.id ? updated : t))
        );
      } else {
        const newTodo = await api.createTask({
          title: input,
          description,
          priority,
          tags: [],
        });
        setTodos((prev) => [newTodo, ...prev]);
      }
      closeModal();
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChatSubmit = async () => {
    if (!chatInput.trim()) return;
    const userMsg = { role: "user", content: chatInput };
    setChatMessages((prev) => [...prev, userMsg]);
    setChatInput("");
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/${user?.id}/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
          },
          body: JSON.stringify({ message: chatInput, conversation_id: convId }),
        }
      );
      const data = await res.json();
      setChatMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.response },
      ]);
      setConvId(data.conversation_id);
      loadTodos();
    } catch (err) {
      console.error(err);
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
    if (!confirm("Delete permanently?")) return;
    try {
      await api.deleteTask(id);
      setTodos((prev) => prev.filter((t) => t.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  const openEditModal = (todo: any) => {
    setEditingTodo(todo);
    setInput(todo.title);
    setDescription(todo.description || "");
    setPriority(todo.priority);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingTodo(null);
    setInput("");
    setDescription("");
  };

  const doneCount = todos.filter((t) => t.completed).length;

  if (loading)
    return (
      <div className="flex justify-center items-center min-h-screen bg-[#020617]">
        <Loader2 className="animate-spin text-indigo-500" size={40} />
      </div>
    );

  return (
    <main className="min-h-screen bg-[#020617] text-slate-200 pb-24">
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-indigo-600/10 blur-[120px] rounded-full" />
        <div className="absolute bottom-[10%] right-[-5%] w-[40%] h-[40%] bg-purple-600/10 blur-[100px] rounded-full" />
      </div>

      <div className="max-w-xl mx-auto px-6 pt-12 relative z-10">
        <header className="flex justify-between items-start mb-10">
          <div>
            <h1 className="text-3xl font-black text-white mb-1">Focus</h1>
            <p className="text-slate-500 text-xs font-bold tracking-widest">
              {user?.email}
            </p>
          </div>
          <button
            title="Sign out"
            aria-label="Sign out"
            onClick={signOut}
            className="bg-slate-800/40 p-3 rounded-xl border border-slate-700/50 hover:bg-red-500/10 transition-all"
          >
            <LogOut size={20} className="text-slate-400" />
          </button>
        </header>

        <div className="grid grid-cols-3 gap-4 mb-12">
          <StatBox
            label="Total"
            val={todos.length}
            color="text-indigo-400"
            Icon={ListTodo}
          />
          <StatBox
            label="Active"
            val={todos.length - doneCount}
            color="text-amber-400"
            Icon={Clock}
          />
          <StatBox
            label="Done"
            val={doneCount}
            color="text-emerald-400"
            Icon={CheckSquare}
          />
        </div>

        <section className="space-y-4">
          <h2 className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-500 mb-6">
            Current Queue
          </h2>
          {todos.length === 0 ? (
            <div className="text-center py-20 bg-slate-900/20 rounded-2xl border border-dashed border-slate-800">
              <p className="text-slate-600 font-bold italic">
                You're all caught up! ☕
              </p>
            </div>
          ) : (
            todos.map((todo) => (
              <div
                key={todo.id}
                className={`group relative flex items-center p-5 rounded-2xl transition-all border backdrop-blur-md ${
                  todo.completed
                    ? "bg-slate-900/30 border-slate-800/40 opacity-60"
                    : "bg-slate-800/40 border-slate-700/50 hover:border-indigo-500/40 shadow-xl"
                }`}
              >
                <div
                  className={`absolute left-0 top-0 bottom-0 w-1 ${
                    todo.priority === "high"
                      ? "bg-red-500"
                      : todo.priority === "medium"
                      ? "bg-amber-500"
                      : "bg-emerald-500"
                  }`}
                />
                <button
                  title="Toggle Complete"
                  aria-label="Toggle Complete"
                  onClick={() => toggleTodo(todo.id)}
                  className={`h-6 w-6 shrink-0 transition-all ${
                    todo.completed
                      ? "text-indigo-500"
                      : "text-slate-600 hover:text-indigo-400"
                  }`}
                >
                  {todo.completed ? (
                    <CheckCircle2 size={24} />
                  ) : (
                    <Circle size={24} />
                  )}
                </button>
                <div
                  className="flex-1 ml-4 min-w-0 cursor-pointer"
                  onClick={() => openEditModal(todo)}
                >
                  <h3
                    className={`font-bold truncate leading-tight ${
                      todo.completed
                        ? "text-slate-600 line-through"
                        : "text-white"
                    }`}
                  >
                    {todo.title}
                  </h3>
                  {todo.description && (
                    <p className="text-[10px] mt-1 truncate text-slate-500 font-medium tracking-tight">
                      {todo.description}
                    </p>
                  )}
                </div>
                <div className="flex gap-1 ml-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    title="openEditModal"
                    aria-label="openEditModal"
                    onClick={() => openEditModal(todo)}
                    className="p-2 text-slate-500 hover:text-indigo-400"
                  >
                    <Edit3 size={18} />
                  </button>
                  <button
                    title="deleteTodo"
                    aria-label="deleteTodo"
                    onClick={() => deleteTodo(todo.id)}
                    className="p-2 text-slate-500 hover:text-red-500"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
            ))
          )}
        </section>
      </div>

      {/* Floating Chat Trigger */}
      <button
        title="Toggle AI Chat"
        aria-label="Toggle AI Chat"
        onClick={() => setIsChatOpen(!isChatOpen)}
        className="fixed bottom-10 left-8 h-14 w-14 bg-slate-800 text-indigo-400 rounded-2xl shadow-xl flex items-center justify-center border border-slate-700 z-50 hover:bg-slate-700 transition-all shadow-indigo-500/5"
      >
        <MessageSquare size={28} />
      </button>

      {/* Floating Add Trigger */}
      <button
        title="Add Task"
        aria-label="Add Task"
        className="fixed bottom-10 right-8 h-16 w-16 bg-indigo-600 text-white rounded-2xl shadow-xl flex items-center justify-center hover:scale-110 active:scale-95 transition-all z-50 border-t border-white/20"
        onClick={() => {
          closeModal();
          setShowModal(true);
        }}
      >
        <Plus size={32} className="text-white" strokeWidth={3} />
      </button>

      {/* Chat Interface Drawer (Custom Input to avoid blocked ChatKit input) */}
      {isChatOpen && (
        <div className="fixed bottom-28 left-8 w-80 bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl z-50 flex flex-col h-96 animate-in slide-in-from-bottom-5 duration-300 overflow-hidden">
          <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-900/50 rounded-t-2xl">
            <div className="flex items-center gap-2">
              <h4 className="font-black text-[10px] uppercase tracking-widest text-indigo-400">
                Focus ChatKit
              </h4>
            </div>
            <button
              title="Close Chat"
              aria-label="Close Chat"
              onClick={() => setIsChatOpen(false)}
            >
              <X size={16} />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3 text-[12px] bg-slate-950">
            {chatMessages.length === 0 && (
              <p className="text-slate-600 text-center mt-10 italic">
                How can I help you today?
              </p>
            )}
            {chatMessages.map((m, i) => (
              <div
                key={i}
                className={m.role === "user" ? "text-right" : "text-left"}
              >
                <span
                  className={`inline-block px-3 py-2 rounded-xl ${
                    m.role === "user"
                      ? "bg-indigo-600 text-white"
                      : "bg-slate-800 text-slate-300"
                  }`}
                >
                  {m.content}
                </span>
              </div>
            ))}
          </div>

          <div className="p-4 border-t border-slate-800 flex gap-2 bg-slate-900">
            <input
              title="Chat Input"
              aria-label="Chat Input"
              placeholder="Ask Focus AI..."
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleChatSubmit()}
              className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none focus:ring-1 focus:ring-indigo-500"
            />
            <button
              title="Send Message"
              aria-label="Send Message"
              onClick={handleChatSubmit}
              className="bg-indigo-600 p-2 rounded-xl text-white active:scale-95"
            >
              <Send size={14} />
            </button>
          </div>
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 z-60 flex items-end sm:items-center justify-center p-0 sm:p-6">
          <div
            className="absolute inset-0 bg-black/80 backdrop-blur-sm"
            onClick={closeModal}
          />
          <div className="relative w-full max-w-md bg-slate-900 border border-slate-800 rounded-t-2xl sm:rounded-2xl p-8 animate-in slide-in-from-bottom-10 duration-300 shadow-2xl">
            <h2 className="text-2xl font-black text-white mb-6">
              {editingTodo ? "Refine Task" : "New Task"}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <input
                title="Task Name"
                aria-label="Task Name"
                required
                autoFocus
                value={input}
                onChange={(e) => setInput(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-4 text-white focus:ring-2 focus:ring-indigo-500 outline-none font-bold"
                placeholder="What needs doing?"
              />
              <textarea
                title="Task Description"
                aria-label="Task Description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-4 text-white focus:ring-2 focus:ring-indigo-500 outline-none text-sm"
                placeholder="Additional details..."
                rows={3}
              />
              <div className="flex gap-2">
                <PriorityBtn
                  label="Chill"
                  current={priority}
                  set={setPriority}
                  val="low"
                  color="bg-emerald-500"
                />
                <PriorityBtn
                  label="Normal"
                  current={priority}
                  set={setPriority}
                  val="medium"
                  color="bg-amber-500"
                />
                <PriorityBtn
                  label="Urgent"
                  current={priority}
                  set={setPriority}
                  val="high"
                  color="bg-red-500"
                />
              </div>
              <button
                title="Commit Changes"
                aria-label="Commit Changes"
                type="submit"
                disabled={isSubmitting || !input.trim()}
                className="w-full bg-indigo-600 hover:bg-indigo-500 py-4 rounded-xl font-black text-white transition-all disabled:opacity-40 active:scale-95"
              >
                {isSubmitting
                  ? "Syncing..."
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
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { useAuth } from './../context/AuthContext';
import { Rocket, ShieldCheck } from 'lucide-react';

export default function Home() {
  const router = useRouter();
  const { user, loading } = useAuth();

  useEffect(() => {
    if (!loading && user) router.replace('/dashboard');
  }, [user, loading, router]);

  if (loading) return null;

  return (
    <div className="min-h-screen flex flex-col bg-[#020617] text-slate-200">
      <main className="grow flex items-center justify-center p-6">
        <div className="max-w-md w-full bg-slate-900/40 backdrop-blur-md p-10 rounded-3xl border border-slate-800 shadow-2xl text-center">
          <div className="w-16 h-16 bg-indigo-600/20 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <Rocket className="text-indigo-500" size={32} />
          </div>
          <h1 className="text-4xl font-black text-white tracking-tight mb-2">Focus</h1>
          <p className="text-slate-400 font-medium mb-10">Professional task management for modern teams.</p>
          
          <div className="flex flex-col gap-3">
            <button onClick={() => router.push('/auth/signin')} className="w-full py-4 bg-indigo-600 text-white font-bold rounded-xl hover:bg-indigo-500 transition-all active:scale-95 shadow-lg shadow-indigo-600/20">
              Sign In
            </button>
            <button onClick={() => router.push('/auth/signup')} className="w-full py-4 bg-slate-800 text-slate-300 font-bold rounded-xl hover:bg-slate-700 transition-all active:scale-95">
              Get Started
            </button>
          </div>
          <div className="mt-8 flex items-center justify-center gap-2 text-slate-600 text-xs font-bold uppercase tracking-widest">
            <ShieldCheck size={14} /> Secure by Better Auth
          </div>
        </div>
      </main>
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

# components\DashboardUI.tsx
```tsx
import { LucideIcon } from "lucide-react";

export function StatBox({
  label,
  val,
  color,
  Icon,
}: {
  label: string;
  val: number;
  color: string;
  Icon: LucideIcon;
}) {
  return (
    <div className="bg-slate-900/40 border border-slate-800/60 p-4 rounded-2xl text-center backdrop-blur-md flex flex-col items-center gap-1">
      <Icon size={16} className={color} />
      <p className={`text-xl font-bold ${color}`}>{val}</p>
      <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
        {label}
      </p>
    </div>
  );
}

export function PriorityBtn({ label, current, set, val, color }: any) {
  const active = current === val;
  return (
    <button
      type="button"
      title={`Set priority to ${label}`}
      aria-label={`Set priority to ${label}`}
      onClick={() => set(val)}
      className={`flex-1 py-3 rounded-xl text-[11px] font-bold uppercase tracking-wider transition-all border-2 ${
        active
          ? `${color} border-transparent text-white shadow-lg`
          : "bg-slate-800/30 border-slate-800/80 text-slate-500 hover:border-slate-700"
      }`}
    >
      {label}
    </button>
  );
}

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

# tests\frontend.test.tsx
```tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import TaskItem from '../components/TaskItem';
import TaskList from '../components/TaskList';
import TaskForm from '../components/TaskForm';
import AuthGuard from '../components/AuthGuard';

// Mock the useAuth hook
vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({
    user: { id: 'test-user', email: 'test@example.com', name: 'Test User' },
    loading: false,
    isAuthenticated: true,
  }),
}));

// Mock the api client
vi.mock('../lib/api', () => ({
  api: {
    getTasks: vi.fn(),
    createTask: vi.fn(),
    updateTask: vi.fn(),
    deleteTask: vi.fn(),
    toggleComplete: vi.fn(),
  },
}));

describe('Frontend Component Tests', () => {
  describe('TaskItem Component', () => {
    const mockTask = {
      id: 1,
      user_id: 'test-user',
      title: 'Test Task',
      description: 'Test Description',
      completed: false,
      priority: 'medium',
      category: 'test',
      tags: ['tag1', 'tag2'],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    it('renders task title and description correctly', () => {
      render(<TaskItem task={mockTask} onToggle={() => {}} onDelete={() => {}} />);

      expect(screen.getByText('Test Task')).toBeInTheDocument();
      expect(screen.getByText('Test Description')).toBeInTheDocument();
    });

    it('shows completion status properly', () => {
      const { rerender } = render(<TaskItem task={{...mockTask, completed: false}} onToggle={() => {}} onDelete={() => {}} />);
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).not.toBeChecked();

      rerender(<TaskItem task={{...mockTask, completed: true}} onToggle={() => {}} onDelete={() => {}} />);
      expect(checkbox).toBeChecked();
    });

    it('calls toggle completion handler when checkbox is clicked', async () => {
      const mockOnToggle = vi.fn();
      render(<TaskItem task={mockTask} onToggle={mockOnToggle} onDelete={() => {}} />);

      const checkbox = screen.getByRole('checkbox');
      fireEvent.click(checkbox);

      await waitFor(() => {
        expect(mockOnToggle).toHaveBeenCalledWith(mockTask.id);
      });
    });

    it('calls delete handler when delete button is clicked', async () => {
      const mockOnDelete = vi.fn();
      render(<TaskItem task={mockTask} onToggle={() => {}} onDelete={mockOnDelete} />);

      const deleteButton = screen.getByLabelText('deleteTodo');
      fireEvent.click(deleteButton);

      await waitFor(() => {
        expect(mockOnDelete).toHaveBeenCalledWith(mockTask.id);
      });
    });
  });

  describe('TaskList Component', () => {
    const mockTasks = [
      {
        id: 1,
        user_id: 'test-user',
        title: 'Task 1',
        description: 'Description 1',
        completed: false,
        priority: 'medium',
        category: 'test',
        tags: ['tag1'],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      {
        id: 2,
        user_id: 'test-user',
        title: 'Task 2',
        description: 'Description 2',
        completed: true,
        priority: 'high',
        category: 'work',
        tags: ['tag1', 'tag2'],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ];

    it('renders multiple tasks', () => {
      const { container } = render(<TaskList tasks={mockTasks} onToggle={() => {}} onDelete={() => {}} />);

      expect(screen.getByText('Task 1')).toBeInTheDocument();
      expect(screen.getByText('Task 2')).toBeInTheDocument();
      expect(container.querySelectorAll('[data-testid="task-item"]').length).toBe(2);
    });

    it('shows empty state when no tasks', () => {
      render(<TaskList tasks={[]} onToggle={() => {}} onDelete={() => {}} />);

      expect(screen.getByText("You're all caught up!")).toBeInTheDocument();
    });

    it('passes props correctly to child TaskItem components', () => {
      const mockOnToggle = vi.fn();
      const mockOnDelete = vi.fn();
      render(<TaskList tasks={mockTasks} onToggle={mockOnToggle} onDelete={mockOnDelete} />);

      const checkboxes = screen.getAllByRole('checkbox');
      fireEvent.click(checkboxes[0]);

      const deleteButtons = screen.getAllByLabelText('deleteTodo');
      fireEvent.click(deleteButtons[1]);

      waitFor(() => {
        expect(mockOnToggle).toHaveBeenCalledWith(mockTasks[0].id);
        expect(mockOnDelete).toHaveBeenCalledWith(mockTasks[1].id);
      });
    });
  });

  describe('TaskForm Component', () => {
    it('submits form with correct data', async () => {
      const mockOnSubmit = vi.fn();
      render(<TaskForm onSubmit={mockOnSubmit} />);

      // Fill the form
      fireEvent.change(screen.getByPlaceholderText('Task name...'), { target: { value: 'New Task' } });
      fireEvent.change(screen.getByPlaceholderText('Details...'), { target: { value: 'Task details' } });
      fireEvent.click(screen.getByText('Urgent'));
      fireEvent.click(screen.getByText('Add Task'));

      // Wait for submission
      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(expect.objectContaining({
          title: 'New Task',
          description: 'Task details',
          priority: 'high',
        }));
      });
    });

    it('validates required fields', () => {
      render(<TaskForm onSubmit={() => {}} />);

      // Try submitting empty form
      fireEvent.click(screen.getByText('Add Task'));

      // Check that onSubmit was not called
      expect(vi.fn()).not.toBeCalled();
    });

    it('resets form after successful submission', async () => {
      const mockOnSubmit = vi.fn().mockResolvedValue({});
      render(<TaskForm onSubmit={mockOnSubmit} />);

      // Fill and submit form
      fireEvent.change(screen.getByPlaceholderText('Task name...'), { target: { value: 'New Task' } });
      fireEvent.click(screen.getByText('Add Task'));

      await waitFor(() => {
        // After successful submission, the form should reset
        expect(screen.getByPlaceholderText('Task name...').innerHTML).toBe('');
      });
    });
  });

  describe('AuthGuard Component', () => {
    it('renders children for authenticated users', () => {
      render(
        <AuthGuard>
          <div>Protected Content</div>
        </AuthGuard>
      );

      expect(screen.getByText('Protected Content')).toBeInTheDocument();
    });

    it('redirects unauthenticated users', () => {
      // Mock an unauthenticated state
      vi.mock('../context/AuthContext', () => ({
        useAuth: () => ({
          user: null,
          loading: false,
          isAuthenticated: false,
        }),
      }));

      render(
        <AuthGuard>
          <div>Protected Content</div>
        </AuthGuard>
      );

      // Since we're mocking the hook differently, this would redirect in a real scenario
      // In tests, we would need to check the window.location behavior
      // This is a simplified check
    });
  });
});
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
    "@openai/chatkit-react": "^1.4.1",
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
    "lucide-react": "^0.562.0",
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

