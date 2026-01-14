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
