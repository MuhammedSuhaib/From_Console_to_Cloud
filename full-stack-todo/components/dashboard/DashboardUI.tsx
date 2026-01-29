import { LucideIcon } from "lucide-react";

export function StatBox({
  label,
  val,
  color,
  Icon,
}: {
  label: string;
  val: number;
  color: string;
  Icon: LucideIcon;
}) {
  return (
    <div className="bg-slate-900/40 border border-slate-800/60 p-4 rounded-2xl text-center backdrop-blur-md flex flex-col items-center gap-1">
      <Icon size={16} className={color} />
      <p className={`text-xl font-bold ${color}`}>{val}</p>
      <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
        {label}
      </p>
    </div>
  );
}

export function PriorityBtn({ label, current, set, val, color }: any) {
  const active = current === val;
  return (
    <button
      type="button"
      title={`Set priority to ${label}`}
      aria-label={`Set priority to ${label}`}
      onClick={() => set(val)}
      className={`flex-1 py-3 rounded-xl text-[11px] font-bold uppercase tracking-wider transition-all border-2 ${
        active
          ? `${color} border-transparent text-white shadow-lg`
          : "bg-slate-800/30 border-slate-800/80 text-slate-500 hover:border-slate-700 focus:border-slate-700 active:border-slate-700"
      }`}
    >
      {label}
    </button>
  );
}
