import { MessageSquare, Plus } from "lucide-react";

interface FloatingActionsProps {
  setIsChatOpen: React.Dispatch<React.SetStateAction<boolean>>;
  setShowModal: React.Dispatch<React.SetStateAction<boolean>>;
  closeModal: () => void;
}

export function FloatingActions({ setIsChatOpen, setShowModal, closeModal }: FloatingActionsProps) {
  return (
    <>
      {/* Floating Chat Trigger */}
      <button
        title="Toggle AI Chat"
        aria-label="Toggle AI Chat"
        onClick={() => setIsChatOpen((prev: boolean) => !prev)}
        className="fixed bottom-10 left-8 h-14 w-14 bg-slate-800 text-indigo-400 rounded-2xl shadow-xl flex items-center justify-center border border-slate-700 z-50 hover:bg-slate-700 focus:bg-slate-700 active:bg-slate-700 transition-all shadow-indigo-500/5"
      >
        <MessageSquare size={28} />
      </button>

      {/* Floating Add Trigger */}
      <button
        title="Add Task"
        aria-label="Add Task"
        className="fixed bottom-10 right-8 h-16 w-16 bg-indigo-600 text-white rounded-2xl shadow-xl flex items-center justify-center hover:scale-110 focus:scale-110 active:scale-95 transition-all z-50 border-t border-white/20"
        onClick={() => {
          closeModal();
          setShowModal(true);
        }}
      >
        <Plus size={32} className="text-white" strokeWidth={3} />
      </button>
    </>
  );
}