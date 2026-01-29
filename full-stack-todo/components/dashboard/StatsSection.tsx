import { ListTodo, CheckSquare, Clock } from "lucide-react";
import { StatBox } from "./DashboardUI";

interface StatsSectionProps {
  todos: any[];
  doneCount: number;
}

export function StatsSection({ todos, doneCount }: StatsSectionProps) {
  return (
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
  );
}