"use client";

import { useState, useEffect, useCallback } from "react";
import { useAuth } from "./../../context/AuthContext";
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

  const loadTodos = useCallback(async () => {
    let token = localStorage.getItem("auth_token");

    // Wait slightly if token is still being written to storage
    if (!token) {
      await new Promise((resolve) => setTimeout(resolve, 500));
      token = localStorage.getItem("auth_token");
    }

    if (!token) {
      console.error("No token found, redirecting...");
      window.location.href = "/auth/signin";
      return;
    }

    try {
      const fetchedTodos = (await api.getTasks()) as Todo[];
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

  const addTodo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    setAddingTodo(true);
    try {
      const newTodo = (await api.createTask({
        title: input,
        description,
        priority: "medium",
        tags: [],
      })) as Todo;
      setTodos((prev: Todo[]) => [...prev, newTodo]);
      setInput("");
      setDescription("");
    } catch (error) {
      console.error("Error adding todo:", error);
    } finally {
      setAddingTodo(false);
    }
  };

  const toggleTodo = async (id: number) => {
    setUpdatingTodo(id);
    try {
      const updated = (await api.toggleComplete(id)) as Todo;
      setTodos((prev: Todo[]) => prev.map((t) => (t.id === id ? updated : t)));
    } catch (error) {
      console.error("Error toggling todo:", error);
    } finally {
      setUpdatingTodo(null);
    }
  };

  const deleteTodo = async (id: number) => {
    if (!confirm("Delete this task?")) return;
    setDeletingTodo(id);
    try {
      await api.deleteTask(id);
      setTodos((prev: Todo[]) => prev.filter((t) => t.id !== id));
    } catch (error) {
      console.error("Error deleting todo:", error);
    } finally {
      setDeletingTodo(null);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen bg-black">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
      </div>
    );
  }

  return (
    <main className="max-w-4xl mx-auto p-6 min-h-screen text-gray-100">
      <header className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Todo Dashboard</h1>
        <div className="flex items-center gap-4">
          <span className="text-sm">Logged in as {user?.email}</span>
          <button
            onClick={signOut}
            className="px-4 py-2 bg-red-600 rounded-lg text-sm"
          >
            Sign Out
          </button>
        </div>
      </header>

      <section className="mb-10 p-6 bg-white rounded-xl shadow-xl">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">New Task</h2>
        <form onSubmit={addTodo} className="flex flex-col gap-4">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="What's next?"
            className="w-full px-4 py-2 border border-gray-300 text-gray-900 rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
          />
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Details (Optional)"
            className="w-full px-4 py-2 border border-gray-300 text-gray-900 rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={addingTodo}
            className="self-end px-6 py-2 bg-blue-600 text-white rounded-lg"
          >
            {addingTodo ? "Adding..." : "Add Task"}
          </button>
        </form>
      </section>

      <section>
        <ul className="grid gap-4 text-gray-900">
          {todos.map((todo) => (
            <li
              key={todo.id}
              className="flex items-center p-4 bg-white border border-gray-200 rounded-xl"
            >
              <input
                placeholder="checkbox"
                type="checkbox"
                checked={todo.completed}
                onChange={() => toggleTodo(todo.id)}
                className="h-5 w-5 mr-4"
              />
              <div className="flex-1">
                <h3
                  className={`font-semibold ${
                    todo.completed ? "line-through text-gray-400" : ""
                  }`}
                >
                  {todo.title}
                </h3>
                <p className="text-sm text-gray-500">{todo.description}</p>
              </div>
              <button
                onClick={() => deleteTodo(todo.id)}
                className="ml-4 text-red-500"
              >
                Delete
              </button>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
