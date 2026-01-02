"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";

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
    if (user) loadTodos();
  }, [user]);

  const loadTodos = async () => {
    try {
      if (!user) return;
      const fetchedTodos = await api.getTasks(user.id);
      setTodos(fetchedTodos);
    } finally {
      setLoading(false);
    }
  };

  const addTodo = async () => {
    console.log('addTodo called', { input, user });
    if (!input.trim() || !user) {
      console.log('addTodo cancelled - no input or no user', { input: input.trim(), user });
      return;
    }

    console.log('Starting to add todo...');
    setAddingTodo(true);
    try {
      console.log('Calling API to create task...');
      const newTodo = await api.createTask(user.id, {
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
    if (!user) return;

    setUpdatingTodo(id);
    try {
      const updated = await api.toggleTaskCompletion(user.id, id);
      setTodos(todos.map((t) => (t.id === id ? updated : t)));
    } catch (error) {
      console.error('Error toggling todo:', error);
    } finally {
      setUpdatingTodo(null);
    }
  };

  const deleteTodo = async (id: number) => {
    if (!user) return;

    setDeletingTodo(id);
    try {
      await api.deleteTask(user.id, id);
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
