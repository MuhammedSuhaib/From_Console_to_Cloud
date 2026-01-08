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