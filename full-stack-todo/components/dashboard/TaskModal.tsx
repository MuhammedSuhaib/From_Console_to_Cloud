import { PriorityBtn } from './DashboardUI';
import { X } from 'lucide-react';

export default function TaskModal({
  show,
  editing,
  onClose,
  onSubmit,
  state,
  setState,
  isSubmitting
}: any) {
  if (!show) return null;

  const handleInputChange = (field: string, value: any) => {
    // Check if setState accepts a function (functional update) or an object
    if (typeof setState === 'function') {
      setState((prevState: any) => ({
        ...prevState,
        [field]: value
      }));
    } else {
      // If setState is not a function, it's probably a setter function itself
      setState({
        ...state,
        [field]: value
      });
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4">
      <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-md bg-slate-900 border border-slate-800 rounded-t-3xl sm:rounded-3xl p-8 animate-in slide-in-from-bottom-10 shadow-2xl">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-black text-white uppercase tracking-tighter">
            {editing ? "Refine Segment" : "New Segment"}
          </h2>
          <button onClick={onClose} className="text-slate-500 hover:text-white focus:text-white active:text-white"><X size={20}/></button>
        </div>

        <form onSubmit={(e) => {
          e.preventDefault();
          onSubmit(e);
        }} className="space-y-4">
          <input
            title="Task Name"
            required
            value={state.title}
            onChange={(e) => handleInputChange('title', e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-4 text-white focus:ring-2 focus:ring-indigo-500 outline-none font-bold"
            placeholder="What needs doing?"
          />

          <textarea
            title="Task Description"
            value={state.description}
            onChange={(e) => handleInputChange('description', e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-indigo-500 outline-none"
            placeholder="Optional details..."
            rows={2}
          />

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-[10px] font-bold text-slate-500 uppercase ml-1">Due Date</label>
              <input
                type="date"
                value={state.due_date}
                onChange={(e) => handleInputChange('due_date', e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white outline-none"
              />
            </div>
            <div className="space-y-1">
              <label className="text-[10px] font-bold text-slate-500 uppercase ml-1">Recurrence</label>
              <select
                value={state.recurrence_pattern}
                onChange={(e) => handleInputChange('recurrence_pattern', e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white outline-none"
              >
                <option value="">None</option>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>
          </div>

          <div className="flex gap-2">
            <PriorityBtn label="Low" current={state.priority} set={(v: any) => handleInputChange('priority', v)} val="low" color="bg-emerald-500" />
            <PriorityBtn label="Mid" current={state.priority} set={(v: any) => handleInputChange('priority', v)} val="medium" color="bg-amber-500" />
            <PriorityBtn label="Urgent" current={state.priority} set={(v: any) => handleInputChange('priority', v)} val="high" color="bg-red-500" />
          </div>

          <button
            type="submit"
            disabled={isSubmitting || !state.title.trim()}
            className="w-full bg-indigo-600 hover:bg-indigo-500 py-4 rounded-2xl font-black text-white transition-all disabled:opacity-40 active:scale-95 uppercase tracking-widest text-xs"
          >
            {isSubmitting ? "Syncing..." : editing ? "Update Task" : "Create Task"}
          </button>
        </form>
      </div>
    </div>
  );
}