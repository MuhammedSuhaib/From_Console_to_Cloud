import { Trash, X } from "lucide-react";

interface ConversationsSidebarProps {
  showConversations: boolean;
  setShowConversations: (show: boolean) => void;
  loadAllConversations: () => void;
  conversationsLoading: boolean;
  allConversations: any[];
  loadSpecificConversation: (id: number) => void;
  deleteSpecificConversation: (id: number) => void;
}

export function ConversationsSidebar({
  showConversations,
  setShowConversations,
  conversationsLoading,
  allConversations,
  loadSpecificConversation,
  deleteSpecificConversation
}: ConversationsSidebarProps) {
  if (!showConversations) return null;

  return (
    <div className="fixed inset-0 sm:inset-auto sm:bottom-20 sm:left-8 sm:w-80 bg-slate-900 border-0 sm:border sm:border-slate-800 sm:rounded-xl shadow-2xl z-50 flex flex-col h-full sm:h-112.5 animate-in slide-in-from-bottom-2 overflow-hidden">
      <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-900/50">
        <h4 className="font-black text-[10px] uppercase tracking-widest text-indigo-400">
          Your Conversations
        </h4>
        <button
          title="Close Conversations"
          aria-label="Close Conversations"
          onClick={() => setShowConversations(false)}
          className="text-slate-500 hover:text-white focus:text-white active:text-white"
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
              className="p-3 w-[99%] bg-slate-800/40 rounded-lg flex justify-between items-start group"
            >
              <div
                className="flex-1 cursor-pointer hover:bg-slate-700/30 focus:bg-slate-700/30 active:bg-slate-700/30 rounded p-1 -m-1"
                onClick={() => loadSpecificConversation(conv.id)}
              >
                <div className="font-medium text-white truncate">
                  {conv.preview}
                </div>
                <div className="text-[10px] text-slate-400 mt-1">
                  {new Date(conv.updated_at).toLocaleDateString()} •{" "}
                  {conv.message_count} messages
                </div>
              </div>
              <button
                title="Delete Conversation"
                aria-label="Delete Conversation"
                onClick={async (e) => {
                  e.stopPropagation(); // Prevent triggering the parent click
                  if (
                    confirm(
                      "Are you sure you want to delete this conversation?",
                    )
                  ) {
                    await deleteSpecificConversation(conv.id);
                  }
                }}
                className="text-slate-500 hover:text-red-500 focus:text-red-500 active:text-red-500 ml-2"
              >
                <Trash size={14} />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}