"use client";

import { useState, useEffect, useCallback } from "react";
import { useAuth } from "./../../context/AuthContext";
import { api } from "./../../lib/api";
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
} from "lucide-react";
import { StatBox, PriorityBtn } from "./../../components/DashboardUI";

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
                        : "text-slate-100"
                    }`}
                  >
                    {todo.title}
                  </h3>
                  {todo.description && (
                    <p className="text-[10px] mt-1 truncate text-slate-500 font-medium">
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
      <button
        title="Add Task"
        aria-label="Add Task"
        className="fixed bottom-10 right-8 h-16 w-16 bg-indigo-600 rounded-2xl shadow-xl flex items-center justify-center hover:scale-110 active:scale-95 transition-all z-50 border-t border-white/20"
        onClick={() => {
          closeModal();
          setShowModal(true);
        }}
      >
        <Plus size={32} className="text-white" strokeWidth={3} />
      </button>

      {showModal && (
        <div className="fixed inset-0 z-60 flex items-end sm:items-center justify-center p-0 sm:p-6">
          <div
            className="absolute inset-0 bg-black/80 backdrop-blur-sm"
            onClick={closeModal}
          />
          <div className="relative w-full max-w-md bg-slate-900 border-t sm:border border-slate-800 rounded-t-3xl sm:rounded-3xl p-8 animate-in slide-in-from-bottom-10 duration-300">
            <h2 className="text-2xl font-black text-white mb-6">
              {editingTodo ? "Refine Task" : "New Task"}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <input
                required
                autoFocus
                value={input}
                onChange={(e) => setInput(e.target.value)}
                className="w-full bg-slate-800 border-slate-700 rounded-xl px-4 py-4 text-white focus:ring-2 focus:ring-indigo-500 outline-none font-bold"
                placeholder="Task name..."
              />
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full bg-slate-800 border-slate-700 rounded-xl px-4 py-4 text-white focus:ring-2 focus:ring-indigo-500 outline-none text-sm"
                placeholder="Details..."
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
                type="submit"
                disabled={isSubmitting || !input.trim()}
                className="w-full bg-indigo-600 hover:bg-indigo-500 py-4 rounded-xl font-black text-white transition-all disabled:opacity-40"
              >
                {isSubmitting
                  ? "Syncing..."
                  : editingTodo
                  ? "Update"
                  : "Create"}
              </button>
            </form>
          </div>
        </div>
      )}
    </main>
  );
}
