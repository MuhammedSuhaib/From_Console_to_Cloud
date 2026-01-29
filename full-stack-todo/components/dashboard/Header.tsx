import { LogOut } from "lucide-react";

interface HeaderProps {
  user: any;
  signOut: () => void;
}

export function Header({ user, signOut }: HeaderProps) {
  return (
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
        className="bg-slate-800/40 p-3 rounded-xl border border-slate-700/50 hover:bg-red-500/10 focus:bg-red-500/10 active:bg-red-500/10 transition-all"
      >
        <LogOut size={20} className="text-slate-400" />
      </button>
    </header>
  );
}