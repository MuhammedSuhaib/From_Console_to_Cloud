"use client";

import { useState, useEffect, useCallback, useMemo, useRef } from "react";
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
  Zap,
  History,
  Trash,
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
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [toolStatus, setToolStatus] = useState<string | null>(null);
  const [showConversations, setShowConversations] = useState(false);
  const [allConversations, setAllConversations] = useState<any[]>([]);
  const [conversationsLoading, setConversationsLoading] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (isChatOpen) scrollToBottom();
  }, [chatMessages, toolStatus, isChatOpen]);

  // ChatKit Integration
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

  // Fetch All Conversations
  const loadAllConversations = useCallback(async () => {
    if (!user?.id) return;
    setConversationsLoading(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/${user.id}/conversations`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
          },
        }
      );
      const data = await res.json();
      if (data.conversations) setAllConversations(data.conversations);
    } catch (err) {
      console.error("Failed to load conversations:", err);
    } finally {
      setConversationsLoading(false);
    }
  }, [user?.id]);

  // Fetch Chat History
  const loadChatHistory = useCallback(async () => {
    if (!user?.id) return;
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/${user.id}/history`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
          },
        }
      );
      const data = await res.json();
      if (data.messages) setChatMessages(data.messages);
    } catch (err) {
      console.error("Failed to load chat history:", err);
    }
  }, [user?.id]);

  // Load Specific Conversation
  const loadSpecificConversation = async (conversationId: number) => {
    if (!user?.id) return;

    // Show immediate loading feedback
    setChatMessages([{role: "assistant", content: "Switching to conversation..."}]);
    setConvId(conversationId);
    setShowConversations(false); // Close the conversations sidebar

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/${user.id}/history?conversation_id=${conversationId}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
          },
        }
      );
      const data = await res.json();
      if (data.messages) {
        setChatMessages(data.messages);
      }
    } catch (err) {
      console.error("Failed to load specific conversation:", err);
      setChatMessages([{role: "assistant", content: "Error loading conversation. Please try again."}]);
    }
  };

  // Delete Specific Conversation
  const deleteSpecificConversation = async (conversationId: number) => {
    if (!user?.id) return;

    // Show immediate feedback
    setAllConversations(prev => prev.filter(conv => conv.id !== conversationId));

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/${user.id}/conversations/${conversationId}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
          },
        }
      );

      if (!res.ok) {
        console.error("Failed to delete conversation:", await res.text());
        // Restore the conversation if deletion failed
        loadAllConversations(); // Reload the conversation list to restore any that failed to delete
      } else {
        // If the currently viewed conversation was deleted, reset to blank state
        if (convId === conversationId) {
          setConvId(null);
          setChatMessages([]);
        }
      }
    } catch (err) {
      console.error("Error deleting specific conversation:", err);
      // Restore the conversation if deletion failed
      loadAllConversations();
    }
  };

  // Delete Chat History
  const deleteChatHistory = async () => {
    if (!confirm("Wipe all memory of this conversation?")) return;

    // Show immediate feedback
    setChatMessages([]);
    const currentConvId = convId; // Store current convId before clearing
    setConvId(null);

    try {
      if (currentConvId) {
        // If there's a specific conversation ID, delete that conversation
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/${user?.id}/conversations/${currentConvId}`, {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
          },
        });

        if (res.ok) {
          // Remove the conversation from the local state if it's loaded
          setAllConversations(prev => prev.filter(conv => conv.id !== currentConvId));
        } else {
          console.error("Failed to delete conversation:", await res.text());
          // Reload conversations to ensure consistency
          loadAllConversations();
        }
      }
    } catch (err) {
      console.error(err);
      // Reload conversations to ensure consistency
      loadAllConversations();
    }
  };

  // Trigger history load when chat is toggled open
  useEffect(() => {
    if (isChatOpen) loadChatHistory();
  }, [isChatOpen, loadChatHistory]);

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
    setIsChatLoading(true);
    setToolStatus(null);
    try {
      const response = await fetch(
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

      if (!response.body) return;
      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      setChatMessages((prev) => [...prev, { role: "assistant", content: "" }]);

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
          const trimmedLine = line.trim();
          if (!trimmedLine || !trimmedLine.startsWith("data: ")) continue;

          try {
            const data = JSON.parse(trimmedLine.slice(6));

            if (data.tool) {
              setToolStatus(`[SYSTEM] EXECUTING: ${data.tool}...`);
            }

            if (data.chunk) {
              setIsChatLoading(false);
              setToolStatus(null);
              setChatMessages((prev) => {
                const last = prev[prev.length - 1];
                return [
                  ...prev.slice(0, -1),
                  { ...last, content: last.content + data.chunk },
                ];
              });
            }

            if (data.error) {
              setIsChatLoading(false);
              setToolStatus(null);
              setChatMessages((prev) => [
                ...prev.slice(0, -1),
                { role: "assistant", content: data.error },
              ]);
            }

            if (data.done) {
              setConvId(data.conversation_id);
              loadTodos();
            }
          } catch (e) {
            console.error("Error parsing stream chunk", e);
          }
        }
      }
    } catch (err) {
      setIsChatLoading(false);
      setToolStatus(null);
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
    <main className="min-h-screen bg-[#020617] text-slate-200 pb-20 relative overflow-x-hidden scrollbar-none">
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-[-5%] left-[-10%] w-[40%] h-[40%] bg-indigo-600/5 blur-[100px] rounded-full" />
        <div className="absolute bottom-[5%] right-[-5%] w-[30%] h-[30%] bg-purple-600/5 blur-[80px] rounded-full" />
      </div>

      <div className="max-w-xl mx-auto px-4 sm:px-6 pt-10 relative z-10">
        <header className="flex justify-between items-start mb-6">
          <div>
            <h1 className="text-xl sm:text-3xl font-black text-white tracking-tighter">
              MICRO TASK AI
            </h1>
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

        <section className="mb-6 p-4 bg-indigo-500/5 border border-indigo-500/10 rounded-xl">
          <div className="flex items-center gap-2 mb-1">
            <Zap size={14} className="text-indigo-400" />
            <h2 className="text-[10px] font-black uppercase tracking-widest text-indigo-300">
              The Micro Task Method
            </h2>
          </div>
          <p className="text-[11px] text-slate-400 leading-snug">
            Atomic segments drive maximum velocity. Use the AI to decompose complex goals into 15-minute actionable steps.
          </p>
        </section>

        <div className="grid grid-cols-3 gap-2 sm:gap-4 mb-8">
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

        <section className="space-y-2">
          <h2 className="text-[9px] font-black uppercase tracking-[0.3em] text-slate-500 mb-3 px-1">
            Current Queue
          </h2>
          {todos.length === 0 ? (
            <div className="text-center py-12 bg-slate-900/10 rounded-xl border border-dashed border-slate-800">
              <p className="text-slate-600 font-bold italic text-xs">
                You're all caught up! ☕
              </p>
            </div>
          ) : (
            todos.map((todo) => (
              <div
                key={todo.id}
                className={`group relative flex items-center p-3 sm:p-4 rounded-xl transition-all border backdrop-blur-md ${
                  todo.completed
                    ? "bg-slate-900/20 border-slate-800/30 opacity-50"
                    : "bg-slate-800/30 border-slate-700/40 hover:border-indigo-500/30"
                }`}
              >
                <div
                  className={`absolute left-0 top-0 bottom-0 w-1 rounded-l-xl ${
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
                  className={`h-5 w-5 shrink-0 transition-all ${
                    todo.completed
                      ? "text-indigo-500"
                      : "text-slate-600 hover:text-indigo-400"
                  }`}
                >
                  {todo.completed ? (
                    <CheckCircle2 size={20} />
                  ) : (
                    <Circle size={20} />
                  )}
                </button>
                <div
                  className="flex-1 ml-3 min-w-0 cursor-pointer"
                  onClick={() => openEditModal(todo)}
                >
                  <h3
                    className={`font-bold truncate text-sm leading-tight ${
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
                    title="Edit Task"
                    aria-label="Edit Task"
                    onClick={() => openEditModal(todo)}
                    className="p-1.5 text-slate-500 hover:text-indigo-400"
                  >
                    <Edit3 size={16} />
                  </button>
                  <button
                    title="Delete Task"
                    aria-label="Delete Task"
                    onClick={() => deleteTodo(todo.id)}
                    className="p-1.5 text-slate-500 hover:text-red-500"
                  >
                    <Trash2 size={16} />
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

      {/* Chat Interface Drawer */}
      {isChatOpen && (
        <div className="fixed inset-0 sm:inset-auto sm:bottom-20 sm:left-8 sm:w-80 bg-slate-900 border-0 sm:border sm:border-slate-800 sm:rounded-xl shadow-2xl z-50 flex flex-col sm:h-[450px] h-full animate-in slide-in-from-bottom-2 overflow-hidden">
          <div className="p-4 sm:p-3 border-b border-slate-800 flex justify-between items-center bg-slate-900/50">
            <h4 className="font-black text-[10px] uppercase tracking-widest text-indigo-400">
              Micro Task AI
            </h4>
            <div className="flex gap-3 sm:gap-2">
              <button
                title="New Conversation"
                aria-label="New Conversation"
                onClick={() => {
                  setConvId(null);
                  setChatMessages([]);
                }}
                className="text-slate-500 hover:text-indigo-400"
              >
                <Plus size={16} />
              </button>
              <button
                title="View Conversations"
                aria-label="View Conversations"
                onClick={async () => {
                  // Show the conversations panel immediately
                  setShowConversations(true);
                  // Set loading state to provide immediate feedback
                  setConversationsLoading(true);
                  // Then load the conversations in the background
                  await loadAllConversations();
                  // The loading state will be cleared by the loadAllConversations function
                }}
                className="text-slate-500 hover:text-indigo-400"
              >
                <History size={16} />
              </button>
              <button
                title="Clear History"
                aria-label="Clear History"
                onClick={deleteChatHistory}
                className="text-slate-500 hover:text-red-500"
              >
                <Trash size={16} />
              </button>
              <button
                title="Close"
                aria-label="Close"
                onClick={() => setIsChatOpen(false)}
                className="text-slate-500 hover:text-white"
              >
                <X size={18} />
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4 text-[12px] bg-slate-950 scrollbar-none [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
            {chatMessages.length === 0 && (
              <div className="p-4 bg-slate-800/40 rounded-xl text-slate-300 leading-relaxed">
                Hello <span className="text-[#00ff41] font-bold">{user?.name || 'User'}</span>! I'm your Micro Task assistant. How can I help you today?
              </div>
            )}
            {chatMessages.map((m, i) => (
              <div
                key={i}
                className={m.role === "user" ? "text-right" : "text-left"}
              >
                <span
                  className={`inline-block px-4 py-2.5 rounded-xl max-w-[85%] ${
                    m.role === "user"
                      ? "bg-indigo-600/20 text-indigo-100 border border-indigo-500/20"
                      : "bg-slate-800/40 text-slate-200"
                  }`}
                >
                  {m.content}
                </span>
              </div>
            ))}
            {isChatLoading && !toolStatus && (
              <div className="text-indigo-500 font-mono text-[10px] animate-pulse ml-1">
                &gt; ANALYZING INTENT...
              </div>
            )}
            {toolStatus && (
              <div className="text-[#00ff41] font-mono text-[10px] animate-pulse ml-1 whitespace-pre-wrap">
                {toolStatus}
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="p-4 sm:p-3 border-t border-slate-800 flex gap-2 bg-slate-900">
            <input
              title="Chat Input"
              aria-label="Chat Input"
              placeholder="Ask AI to add a task..."
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleChatSubmit()}
              className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-4 py-2.5 sm:py-1.5 text-sm sm:text-xs text-white outline-none focus:ring-1 focus:ring-indigo-500"
            />
            <button
              title="Send Message"
              aria-label="Send Message"
              onClick={handleChatSubmit}
              className="bg-indigo-600 px-4 rounded-lg text-white active:scale-95 transition-transform"
            >
              <Send size={14} />
            </button>
          </div>
        </div>
      )}

      {/* Conversations Sidebar */}
      {showConversations && (
        <div className="fixed inset-0 sm:inset-auto sm:bottom-20 sm:left-8 sm:w-80 bg-slate-900 border-0 sm:border sm:border-slate-800 sm:rounded-xl shadow-2xl z-50 flex flex-col h-full sm:h-[450px] animate-in slide-in-from-bottom-2 overflow-hidden">
          <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-900/50">
            <h4 className="font-black text-[10px] uppercase tracking-widest text-indigo-400">
              Your Conversations
            </h4>
            <button
              title="Close Conversations"
              aria-label="Close Conversations"
              onClick={() => setShowConversations(false)}
              className="text-slate-500 hover:text-white"
            >
              <X size={18} />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3 text-[12px] bg-slate-950">
            {conversationsLoading ? (
              <div className="flex justify-center items-center h-full">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-500"></div>
              </div>
            ) : allConversations.length === 0 ? (
              <div className="p-4 text-center text-slate-500">
                No conversations yet
              </div>
            ) : (
              allConversations.map((conv) => (
                <div
                  key={conv.id}
                  className="p-3 bg-slate-800/40 rounded-lg flex justify-between items-start group"
                >
                  <div
                    className="flex-1 cursor-pointer hover:bg-slate-700/30 rounded p-1 -m-1"
                    onClick={() => loadSpecificConversation(conv.id)}
                  >
                    <div className="font-medium text-white truncate">
                      {conv.preview}
                    </div>
                    <div className="text-[10px] text-slate-400 mt-1">
                      {new Date(conv.updated_at).toLocaleDateString()} • {conv.message_count} messages
                    </div>
                  </div>
                  <button
                    title="Delete Conversation"
                    aria-label="Delete Conversation"
                    onClick={async (e) => {
                      e.stopPropagation(); // Prevent triggering the parent click
                      if (confirm("Are you sure you want to delete this conversation?")) {
                        await deleteSpecificConversation(conv.id);
                      }
                    }}
                    className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-red-500 ml-2"
                  >
                    <Trash size={14} />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 z-60 flex items-end sm:items-center justify-center p-0 sm:p-4">
          <div
            className="absolute inset-0 bg-black/80 backdrop-blur-sm"
            onClick={closeModal}
          />
          <div className="relative w-full max-w-sm bg-slate-900 border border-slate-800 rounded-t-xl sm:rounded-xl p-6 animate-in slide-in-from-bottom-4 duration-300 shadow-2xl">
            <h2 className="text-lg font-black text-white mb-4 uppercase tracking-tighter">
              {editingTodo ? "Edit Segment" : "New Segment"}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-3">
              <input
                title="Task Name"
                aria-label="Task Name"
                required
                autoFocus
                value={input}
                onChange={(e) => setInput(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white focus:ring-1 focus:ring-indigo-500 outline-none font-bold text-sm"
                placeholder="What needs doing?"
              />
              <textarea
                title="Task Description"
                aria-label="Task Description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white focus:ring-1 focus:ring-indigo-500 outline-none text-xs"
                placeholder="Optional details..."
                rows={2}
              />
              <div className="flex gap-2">
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
                  label="Urgent"
                  current={priority}
                  set={setPriority}
                  val="high"
                  color="bg-red-500"
                />
              </div>
              <button
                title="Save"
                aria-label="Save"
                type="submit"
                disabled={isSubmitting || !input.trim()}
                className="w-full bg-indigo-600 hover:bg-indigo-500 py-3 rounded-lg font-black text-white transition-all disabled:opacity-40 text-xs uppercase tracking-widest"
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