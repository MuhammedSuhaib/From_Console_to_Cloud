import { useRef, useEffect } from "react";
import {
  Send,
  X,
  Plus,
  History,
  Trash,
  ChevronLeft,
  ChevronRight
} from "lucide-react";
import { ConversationsSidebar } from "./ConversationsSidebar";

interface ChatInterfaceProps {
  isChatOpen: boolean;
  setIsChatOpen: (open: boolean) => void;
  user: any;
  chatMessages: any[];
  setChatMessages: (messages: any[]) => void;
  chatInput: string;
  setChatInput: (input: string) => void;
  isChatLoading: boolean;
  toolStatus: string | null;
  hasMoreMessages: boolean;
  messageOffset: number;
  loadChatHistory: (offset?: number) => void;
  convId: number | null;
  setConvId: (id: number | null) => void;
  setMessageOffset: (offset: number) => void;
  handleChatSubmit: () => void;
  showConversations: boolean;
  setShowConversations: (show: boolean) => void;
  loadAllConversations: () => void;
  conversationsLoading: boolean;
  allConversations: any[];
  loadSpecificConversation: (id: number) => void;
  deleteSpecificConversation: (id: number) => void;
  deleteChatHistory: () => void;
}

export function ChatInterface({
  isChatOpen,
  setIsChatOpen,
  user,
  chatMessages,
  setChatMessages,
  chatInput,
  setChatInput,
  isChatLoading,
  toolStatus,
  hasMoreMessages,
  messageOffset,
  loadChatHistory,
  convId,
  setConvId,
  setMessageOffset,
  handleChatSubmit,
  showConversations,
  setShowConversations,
  loadAllConversations,
  conversationsLoading,
  allConversations,
  loadSpecificConversation,
  deleteSpecificConversation,
  deleteChatHistory
}: ChatInterfaceProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (isChatOpen && messageOffset === 0) scrollToBottom();
  }, [chatMessages, toolStatus, isChatOpen, messageOffset]);

  return (
    <>
      {/* Chat Interface Drawer */}
      {isChatOpen && (
        <div className="fixed inset-0 sm:inset-auto sm:bottom-20 sm:left-8 sm:w-80 bg-slate-900 border-0 sm:border sm:border-slate-800 sm:rounded-xl shadow-2xl z-50 flex flex-col sm:h-112.5 h-full animate-in slide-in-from-bottom-2 overflow-hidden">
          <div className="p-4 sm:p-3 border-b border-slate-800 flex justify-between items-center bg-slate-900/50">
            <h4 className="font-black text-[10px] uppercase tracking-widest text-indigo-400">
              Micro Task AI
            </h4>
            <div className="flex gap-3 sm:gap-2">
              <button
                title="Older Messages"
                aria-label="Older Messages"
                disabled={!hasMoreMessages}
                onClick={() => loadChatHistory(messageOffset + 20)}
                className="text-slate-500 hover:text-indigo-400 focus:text-indigo-400 active:text-indigo-400 disabled:opacity-30"
              >
                <ChevronLeft size={16} />
              </button>
              <button
                title="Newer Messages"
                aria-label="Newer Messages"
                disabled={messageOffset === 0}
                onClick={() => loadChatHistory(Math.max(0, messageOffset - 20))}
                className="text-slate-500 hover:text-indigo-400 focus:text-indigo-400 active:text-indigo-400 disabled:opacity-30"
              >
                <ChevronRight size={16} />
              </button>
              <button
                title="New Conversation"
                aria-label="New Conversation"
                onClick={() => {
                  setConvId(null);
                  setChatMessages([]);
                  setMessageOffset(0);
                }}
                className="text-slate-500 hover:text-indigo-400 focus:text-indigo-400 active:text-indigo-400"
              >
                <Plus size={16} />
              </button>
              <button
                title="View Conversations"
                aria-label="View Conversations"
                onClick={async () => {
                  // Show the conversations panel immediately
                  setShowConversations(true);
                  // Load the conversations in the background
                  await loadAllConversations();
                }}
                className="text-slate-500 hover:text-indigo-400 focus:text-indigo-400 active:text-indigo-400"
              >
                <History size={16} />
              </button>
              <button
                title="Clear History"
                aria-label="Clear History"
                onClick={deleteChatHistory}
                className="text-slate-500 hover:text-red-500 focus:text-red-500 active:text-red-500"
              >
                <Trash size={16} />
              </button>
              <button
                title="Close"
                aria-label="Close"
                onClick={() => setIsChatOpen(false)}
                className="text-slate-500 hover:text-white focus:text-white active:text-white"
              >
                <X size={18} />
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4 text-[12px] bg-slate-950 scrollbar-none [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
            {chatMessages.length === 0 && (
              <div className="p-4 bg-slate-800/40 rounded-xl text-slate-300 leading-relaxed">
                Hello{" "}
                <span className="text-[#00ff41] font-bold">
                  {user?.name || "User"}
                </span>
                ! I'm your Micro Task assistant. How can I help you today?
              </div>
            )}
            {chatMessages.map((m, i) => (
              <div
                key={i}
                className={m.role === "user" ? "text-right" : "text-left"}
              >
                {m.content?.trim() && (
                  <span
                    className={`inline-block px-4 py-2.5 rounded-xl max-w-[85%] ${
                      m.role === "user"
                        ? "bg-indigo-600/20 text-indigo-100 border border-indigo-500/20"
                        : "bg-slate-800/40 text-slate-200"
                    }`}
                  >
                    {m.content}
                  </span>
                )}
              </div>
            ))}
            {isChatLoading && !toolStatus && (
              <div className="text-indigo-500 animate-fade ml-1">
                Wait! I am typing...
              </div>
            )}
            {toolStatus && (
              <div className="text-indigo-500 animate-fade ml-1">
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

      <ConversationsSidebar
        showConversations={showConversations}
        setShowConversations={setShowConversations}
        loadAllConversations={loadAllConversations}
        conversationsLoading={conversationsLoading}
        allConversations={allConversations}
        loadSpecificConversation={loadSpecificConversation}
        deleteSpecificConversation={deleteSpecificConversation}
      />
    </>
  );
}