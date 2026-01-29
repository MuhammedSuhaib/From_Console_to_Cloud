// types.ts
export interface Task {
  id: number;
  user_id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority: 'low' | 'medium' | 'high';
  category?: string;
  tags: string[];
  created_at: string;
  updated_at: string;
  // Phase V: Advanced Features
  due_date?: string; // ISO string format
  is_recurring?: boolean;
  recurrence_pattern?: string;
  reminder_sent?: boolean;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: 'low' | 'medium' | 'high';
  category?: string;
  tags?: string[];
  // Phase V: Advanced Features
  due_date?: string; // ISO string format
  is_recurring?: boolean;
  recurrence_pattern?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  priority?: 'low' | 'medium' | 'high';
  category?: string;
  tags?: string[];
  completed?: boolean;
  // Phase V: Advanced Features
  due_date?: string; // ISO string format
  is_recurring?: boolean;
  recurrence_pattern?: string;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

// Interface for filter and sort parameters
export interface FilterSortParams {
  status?: 'all' | 'pending' | 'completed';
  priority?: 'low' | 'medium' | 'high';
  tags?: string[];
  sort_by?: 'priority' | 'due_date' | 'created_at' | 'updated_at';
  sort_order?: 'asc' | 'desc';
  category?: string;
}

// Interface for search parameters
export interface SearchParams {
  keyword: string;
}