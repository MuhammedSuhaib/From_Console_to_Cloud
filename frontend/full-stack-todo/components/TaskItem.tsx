// frontend/full-stack-todo/components/TaskItem.tsx
import React from 'react';
import { Task } from '../types';

interface TaskItemProps {
  task: Task;
  onToggle: (taskId: number) => void;
  onDelete: (taskId: number) => void;
}

const TaskItem: React.FC<TaskItemProps> = ({ task, onToggle, onDelete }) => {
  const handleToggle = () => {
    onToggle(task.id);
  };

  const handleDelete = () => {
    onDelete(task.id);
  };

  return (
    <li
      key={task.id}
      className="flex items-center p-4 bg-gray-100 rounded-lg shadow hover:shadow-md transition"
    >
      <input
        type="checkbox"
        checked={task.completed}
        onChange={handleToggle}
        className="mr-4 h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
      />
      <div className="flex-1 min-w-0">
        <p
          className={`truncate ${
            task.completed ? 'line-through text-gray-500' : 'text-gray-900'
          }`}
        >
          {task.title}
        </p>
        {task.description && (
          <p className="text-sm text-gray-500 truncate">{task.description}</p>
        )}
        {task.category && (
          <span className="inline-block mt-1 px-2 py-0.5 text-xs bg-blue-100 text-blue-800 rounded-full">
            {task.category}
          </span>
        )}
      </div>
      <div className="ml-4 flex items-center space-x-2">
        <span className={`px-2 py-1 text-xs rounded-full ${
          task.priority === 'high' ? 'bg-red-100 text-red-800' :
          task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
          'bg-green-100 text-green-800'
        }`}>
          {task.priority}
        </span>
        <button
          onClick={handleDelete}
          className="ml-2 bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded-lg transition text-sm"
        >
          Delete
        </button>
      </div>
    </li>
  );
};

export default TaskItem;