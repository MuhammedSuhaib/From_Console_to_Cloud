import { CheckCircle2, Circle, Edit3, Trash2, Calendar, RefreshCw } from 'lucide-react';
import { SmallSpinner } from "./../LoadingSpinner";

export default function TaskCard({ todo, onToggle, onEdit, onDelete, isLoading }: any) {
  return (
    <div className={`group relative flex items-center p-4 rounded-2xl transition-all border backdrop-blur-md ${
      todo.completed ? "bg-slate-900/20 border-slate-800/30 opacity-50" : "bg-slate-800/40 border-slate-700/50 focus-within:border-indigo-500/40 active:border-indigo-500/40 shadow-xl"
    }`}>
      <div className={`absolute left-0 top-0 bottom-0 w-1 rounded-l-2xl ${
        todo.priority === "high" ? "bg-red-500" : todo.priority === "medium" ? "bg-amber-500" : "bg-emerald-500"
      }`} />

      <button
        onClick={() => onToggle(todo.id)}
        className={`h-6 w-6 shrink-0 transition-all flex items-center justify-center ${todo.completed ? "text-indigo-500" : "text-slate-600 focus:text-indigo-400 active:text-indigo-400"}`}
        disabled={isLoading}
      >
        {isLoading ? <SmallSpinner /> : (todo.completed ? <CheckCircle2 size={24} /> : <Circle size={24} />)}
      </button>

      <div className="flex-1 ml-4 min-w-0 cursor-pointer" onClick={() => onEdit(todo)}>
        <h3 className={`font-bold truncate text-sm sm:text-base ${todo.completed ? "text-slate-600 line-through" : "text-white"}`}>
          {todo.title}
        </h3>
        <div className="flex flex-wrap gap-2 mt-1">
          {todo.due_date && (
            <span className="flex items-center gap-1 text-[9px] text-indigo-300 bg-indigo-500/10 px-1.5 py-0.5 rounded">
              <Calendar size={10} /> {new Date(todo.due_date).toLocaleDateString()}
            </span>
          )}
          {todo.is_recurring && (
            <span className="flex items-center gap-1 text-[9px] text-emerald-300 bg-emerald-500/10 px-1.5 py-0.5 rounded">
              <RefreshCw size={10} /> {todo.recurrence_pattern}
            </span>
          )}
        </div>
      </div>

      <div className="flex gap-1 ml-2 opacity-0 group-focus-within:opacity-100 group-active:opacity-100 sm:group-hover:opacity-100 transition-opacity">
        <button
          onClick={() => onEdit(todo)}
          className="p-2 text-slate-500 focus:text-indigo-400 active:text-indigo-400"
          disabled={isLoading}
        >
          <Edit3 size={16} />
        </button>
        <button
          onClick={() => onDelete(todo.id)}
          className="p-2 text-slate-500 focus:text-red-500 active:text-red-500"
          disabled={isLoading}
        >
          {isLoading ? <SmallSpinner /> : <Trash2 size={16} />}
        </button>
      </div>
    </div>
  );
}