import TaskCard from "./TaskCard";
import { SmallSpinner } from "./../LoadingSpinner";

interface TaskListProps {
  todos: any[];
  filteredTodos: any[];
  searchMode: boolean;
  toggleTodo: (id: number) => void;
  openEditModal: (todo: any) => void;
  deleteTodo: (id: number) => void;
  loadingTodos?: boolean;
}

export function TaskList({ todos, filteredTodos, searchMode, toggleTodo, openEditModal, deleteTodo, loadingTodos = false }: TaskListProps) {
  const tasksToShow = searchMode ? filteredTodos : todos;

  if (loadingTodos) {
    return (
      <section className="space-y-2">
        <h2 className="text-[9px] font-black uppercase tracking-[0.3em] text-slate-500 mb-3 px-1">
          {searchMode ? "Filtered Results" : "Current Queue"}
        </h2>
        <div className="flex justify-center py-12">
          <SmallSpinner />
        </div>
      </section>
    );
  }

  return (
    <section className="space-y-2">
      <h2 className="text-[9px] font-black uppercase tracking-[0.3em] text-slate-500 mb-3 px-1">
        {searchMode ? "Filtered Results" : "Current Queue"}
      </h2>
      {tasksToShow.length === 0 ? (
        <div className="text-center py-12 bg-slate-900/10 rounded-xl border border-dashed border-slate-800">
          <p className="text-slate-600 font-bold italic text-xs">
            {searchMode ? "No tasks match your filters." : "You're all caught up! ☕"}
          </p>
        </div>
      ) : (
        tasksToShow.map((todo) => (
          <TaskCard
            key={todo.id}
            todo={todo}
            onToggle={toggleTodo}
            onEdit={openEditModal}
            onDelete={deleteTodo}
            isLoading={loadingTodos}
          />
        ))
      )}
    </section>
  );
}