"use client";

import { useState, useEffect, useCallback, useMemo, useRef } from "react";
import { useAuth } from "./../../context/AuthContext";
import { api } from "./../../lib/api";
import { useChatKit } from "@openai/chatkit-react";
import { Loader2 } from "lucide-react";
import SearchBar from "./../../components/dashboard/SearchBar";
import FilterSortControls from "./../../components/dashboard/FilterSortControls";
import TaskModal from "./../../components/dashboard/TaskModal";
import { FilterSortParams } from "./../../types";
import { Header } from "./../../components/dashboard/Header";
import { StatsSection } from "./../../components/dashboard/StatsSection";
import { TaskList } from "./../../components/dashboard/TaskList";
import { ChatInterface } from "./../../components/dashboard/ChatInterface";
import { ConversationsSidebar } from "./../../components/dashboard/ConversationsSidebar";
import { FloatingActions } from "./../../components/dashboard/FloatingActions";

// ChatKit Configuration Constants
const WORKFLOW_ID =
  process.env.NEXT_PUBLIC_CHATKIT_WORKFLOW_ID || "wf_placeholder";

export default function DashboardPage() {
  const { user, signOut, subscribeToPushNotifications } = useAuth();
  const [todos, setTodos] = useState<any[]>([]);
  const [filteredTodos, setFilteredTodos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [input, setInput] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<"low" | "medium" | "high">("medium");
  const [dueDate, setDueDate] = useState<string>("");
  const [recurrencePattern, setRecurrencePattern] = useState<string>("");
  const [showModal, setShowModal] = useState(false);
  const [editingTodo, setEditingTodo] = useState<any | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoadingTodos, setIsLoadingTodos] = useState(false);
  const [searchMode, setSearchMode] = useState<boolean>(false);
  const [currentFilters, setCurrentFilters] = useState<FilterSortParams>({});

  const [modalState, setModalState] = useState({
    title: "",
    description: "",
    priority: "medium" as "low" | "medium" | "high",
    due_date: "",
    recurrence_pattern: "",
  });

  // Chat States
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState<any[]>([]);
  const [convId, setConvId] = useState<number | null>(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("active_conv_id");
      return saved ? Number(saved) : null;
    }
    return null;
  });
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [toolStatus, setToolStatus] = useState<string | null>(null);
  const [showConversations, setShowConversations] = useState(false);
  const [allConversations, setAllConversations] = useState<any[]>([]);
  const [conversationsLoading, setConversationsLoading] = useState(false);
  
  // Pagination state for chat history
  const [messageOffset, setMessageOffset] = useState(0);
  const [hasMoreMessages, setHasMoreMessages] = useState(true);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (isChatOpen && messageOffset === 0) scrollToBottom();
  }, [chatMessages, toolStatus, isChatOpen, messageOffset]);

  // Persist convId to localStorage
  useEffect(() => {
    if (convId) {
      localStorage.setItem("active_conv_id", convId.toString());
    } else {
      localStorage.removeItem("active_conv_id");
    }
  }, [convId]);

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
          },
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
      setLoading(true);
      setIsLoadingTodos(true);
      const fetchedTodos = await api.getTasks();
      setTodos(Array.isArray(fetchedTodos) ? fetchedTodos : []);
      setFilteredTodos(Array.isArray(fetchedTodos) ? fetchedTodos : []);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
      setIsLoadingTodos(false);
    }
  }, []);

  const handleSearch = async (keyword: string) => {
    try {
      setIsLoadingTodos(true);
      const searchResults = await api.searchTasks(keyword);
      setFilteredTodos(Array.isArray(searchResults) ? searchResults : []);
      setSearchMode(true);
    } catch (error) {
      console.error("Search error:", error);
      // Fallback to original todos if search fails
      setFilteredTodos(todos);
    } finally {
      setIsLoadingTodos(false);
    }
  };

  const handleClearSearch = () => {
    setFilteredTodos(todos);
    setSearchMode(false);
  };

  const handleApplyFilters = async (filters: FilterSortParams) => {
    try {
      setIsLoadingTodos(true);
      setCurrentFilters(filters);
      const filteredResults = await api.filterSortTasks(filters);
      setFilteredTodos(Array.isArray(filteredResults) ? filteredResults : []);
      setSearchMode(true);
    } catch (error) {
      console.error("Filter error:", error);
      // Fallback to original todos if filter fails
      setFilteredTodos(todos);
    } finally {
      setIsLoadingTodos(false);
    }
  };

  const handleResetFilters = () => {
    setFilteredTodos(todos);
    setCurrentFilters({});
    setSearchMode(false);
  };

  useEffect(() => {
    loadTodos();
  }, [loadTodos]);

  // Subscribe to push notifications when user is authenticated
  useEffect(() => {
    if (user) {
      // Delay the subscription to ensure service worker is registered
      const timer = setTimeout(() => {
        subscribeToPushNotifications();
      }, 1000);

      return () => clearTimeout(timer);
    }
  }, [user, subscribeToPushNotifications]);

  // Request notification permission and set up reminder checks
  useEffect(() => {
    if ("Notification" in window && Notification.permission === "default") {
      Notification.requestPermission();
    }

    const interval = setInterval(() => {
      todos.forEach(todo => {
        if (todo.due_date && !todo.completed && !todo.reminder_sent) {
          const due = new Date(todo.due_date).getTime();
          const now = new Date().getTime();
          const timeDiff = due - now;
          const hoursDiff = Math.floor(timeDiff / (1000 * 60 * 60));

          // Show notification if task is due within 1 hour
          if (hoursDiff <= 1 && hoursDiff >= 0) {
            if (Notification.permission === "granted") {
              new Notification(`Task Reminder: ${todo.title}`, {
                body: `Your task "${todo.title}" is due soon!`,
                icon: "/favicon.ico"
              });

              // Mark the reminder as sent by calling an API endpoint
              api.markReminderSent(todo.id)
                .then(updatedTodo => {
                  // Update the todos state to reflect the change
                  setTodos(prevTodos =>
                    prevTodos.map(t => t.id === todo.id ? updatedTodo : t)
                  );
                  setFilteredTodos(prevFiltered =>
                    prevFiltered.map(t => t.id === todo.id ? updatedTodo : t)
                  );
                })
                .catch(error => {
                  console.error("Failed to mark reminder as sent:", error);
                });
            }
          }

          // Show notification if task is overdue
          if (timeDiff < 0) {
            if (Notification.permission === "granted") {
              new Notification(`Overdue Task: ${todo.title}`, {
                body: `Your task "${todo.title}" is overdue!`,
                icon: "/favicon.ico"
              });

              // Mark the reminder as sent for overdue notifications too
              api.markReminderSent(todo.id)
                .then(updatedTodo => {
                  // Update the todos state to reflect the change
                  setTodos(prevTodos =>
                    prevTodos.map(t => t.id === todo.id ? updatedTodo : t)
                  );
                  setFilteredTodos(prevFiltered =>
                    prevFiltered.map(t => t.id === todo.id ? updatedTodo : t)
                  );
                })
                .catch(error => {
                  console.error("Failed to mark reminder as sent:", error);
                });
            }
          }
        }
      });
    }, 60000); // Check every minute

    return () => clearInterval(interval);
  }, [todos]);

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
        },
      );
      const data = await res.json();
      if (data.conversations) setAllConversations(data.conversations);
    } catch (err) {
      console.error("Failed to load conversations:", err);
    } finally {
      setConversationsLoading(false);
    }
  }, [user?.id]);

  // Fetch Chat History with pagination
  const loadChatHistory = useCallback(async (offset = 0) => {
    if (!user?.id) return;

    try {
      const params = new URLSearchParams({
        limit: '20',
        offset: offset.toString()
      });

      if (convId) {
        params.append('conversation_id', convId.toString());
      } else {
        // If no convId, we have no history to load
        setChatMessages([]);
        return;
      }

      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/${user.id}/history?${params}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
          },
        },
      );
      const data = await res.json();

      if (data.messages) {
        setChatMessages(data.messages);
        setMessageOffset(offset);
        setHasMoreMessages(data.pagination.has_more);
      }
    } catch (err) {
      console.error("Failed to load chat history:", err);
    }
  }, [user?.id, convId]);

  // Load Specific Conversation
  const loadSpecificConversation = async (conversationId: number) => {
    if (!user?.id) return;

    setChatMessages([
      { role: "assistant", content: "Switching to conversation..." },
    ]);
    setConvId(conversationId);
    setShowConversations(false);
    await loadChatHistory(0);
  };

  // Delete Specific Conversation
  const deleteSpecificConversation = async (conversationId: number) => {
    if (!user?.id) return;

    setAllConversations((prev) =>
      prev.filter((conv) => conv.id !== conversationId),
    );

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/${user.id}/conversations/${conversationId}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
          },
        },
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
    setMessageOffset(0);
    setHasMoreMessages(true);

    try {
      if (currentConvId) {
        // If there's a specific conversation ID, delete that conversation
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/${user?.id}/conversations/${currentConvId}`,
          {
            method: "DELETE",
            headers: {
              Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
            },
          },
        );

        if (res.ok) {
          // Remove the conversation from the local state if it's loaded
          setAllConversations((prev) =>
            prev.filter((conv) => conv.id !== currentConvId),
          );
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
    if (isChatOpen) loadChatHistory(0);
  }, [isChatOpen, loadChatHistory]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!modalState.title.trim()) return;
    setIsSubmitting(true);
    setIsLoadingTodos(true);
    try {
      const taskData = {
        title: modalState.title,
        description: modalState.description,
        priority: modalState.priority,
        due_date: modalState.due_date || null,
        is_recurring: !!modalState.recurrence_pattern,
        recurrence_pattern: modalState.recurrence_pattern || null,
      };

      if (editingTodo) {
        const updated = await api.updateTask(editingTodo.id, taskData);
        setTodos((prev) =>
          prev.map((t) => (t.id === editingTodo.id ? updated : t)),
        );
        // Update filtered todos as well
        setFilteredTodos(prev =>
          prev.map(t => (t.id === editingTodo.id ? updated : t))
        );
      } else {
        const newTodo = await api.createTask({ ...taskData, tags: [] });
        setTodos((prev) => [newTodo, ...prev]);
        // If we're in search/filter mode, also update filtered todos
        if (searchMode) {
          setFilteredTodos(prev => [newTodo, ...prev]);
        }
      }
      closeModal();
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
      setIsLoadingTodos(false);
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
        },
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
              setToolStatus(`Tool Call 🛠:\n ${data.tool}...`);
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
              loadTodos(); // This will refresh both todos and filteredTodos
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
      setIsLoadingTodos(true);
      const updated = await api.toggleComplete(id);
      setTodos((prev) => prev.map((t) => (t.id === id ? updated : t)));
      // Update filtered todos as well
      setFilteredTodos(prev => prev.map(t => (t.id === id ? updated : t)));
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoadingTodos(false);
    }
  };

  const deleteTodo = async (id: number) => {
    if (!confirm("Delete permanently?")) return;
    try {
      setIsLoadingTodos(true);
      await api.deleteTask(id);
      setTodos((prev) => prev.filter((t) => t.id !== id));
      // Update filtered todos as well
      setFilteredTodos(prev => prev.filter(t => t.id !== id));
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoadingTodos(false);
    }
  };

  const openEditModal = (todo: any) => {
    setEditingTodo(todo);
    setModalState({
      title: todo.title,
      description: todo.description || "",
      priority: todo.priority,
      due_date: todo.due_date ? new Date(todo.due_date).toISOString().split('T')[0] : "",
      recurrence_pattern: todo.recurrence_pattern || "",
    });
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingTodo(null);
    setModalState({
      title: "",
      description: "",
      priority: "medium",
      due_date: "",
      recurrence_pattern: "",
    });
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
        <Header user={user} signOut={signOut} />

        <StatsSection todos={todos} doneCount={doneCount} />

        {/* Search Bar */}
        <SearchBar
          onSearch={handleSearch}
          onClear={handleClearSearch}
        />

        {/* Filter & Sort Controls */}
        <FilterSortControls
          onApplyFilters={handleApplyFilters}
          onResetFilters={handleResetFilters}
        />

        <TaskList
          todos={todos}
          filteredTodos={filteredTodos}
          searchMode={searchMode}
          toggleTodo={toggleTodo}
          openEditModal={openEditModal}
          deleteTodo={deleteTodo}
          loadingTodos={isLoadingTodos}
        />
      </div>

      <FloatingActions
        setIsChatOpen={setIsChatOpen}
        setShowModal={setShowModal}
        closeModal={closeModal}
      />

      <ChatInterface
        isChatOpen={isChatOpen}
        setIsChatOpen={setIsChatOpen}
        user={user}
        chatMessages={chatMessages}
        setChatMessages={setChatMessages}
        chatInput={chatInput}
        setChatInput={setChatInput}
        isChatLoading={isChatLoading}
        toolStatus={toolStatus}
        hasMoreMessages={hasMoreMessages}
        messageOffset={messageOffset}
        loadChatHistory={loadChatHistory}
        convId={convId}
        setConvId={setConvId}
        setMessageOffset={setMessageOffset}
        handleChatSubmit={handleChatSubmit}
        showConversations={showConversations}
        setShowConversations={setShowConversations}
        loadAllConversations={loadAllConversations}
        conversationsLoading={conversationsLoading}
        allConversations={allConversations}
        loadSpecificConversation={loadSpecificConversation}
        deleteSpecificConversation={deleteSpecificConversation}
        deleteChatHistory={deleteChatHistory}
      />

      <ConversationsSidebar
        showConversations={showConversations}
        setShowConversations={setShowConversations}
        loadAllConversations={loadAllConversations}
        conversationsLoading={conversationsLoading}
        allConversations={allConversations}
        loadSpecificConversation={loadSpecificConversation}
        deleteSpecificConversation={deleteSpecificConversation}
      />

      <TaskModal
        show={showModal}
        editing={!!editingTodo}
        onClose={closeModal}
        onSubmit={handleSubmit}
        state={modalState}
        setState={setModalState}
        isSubmitting={isSubmitting}
      />
    </main>
  );
}