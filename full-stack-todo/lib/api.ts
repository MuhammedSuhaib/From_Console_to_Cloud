const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL!;

async function request<T>(path: string, options: RequestInit = {}) {
  const token =
    typeof window !== "undefined"
      ? localStorage.getItem("auth_token")
      : null;

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "API error");
  }
  
  const json = await res.json();
  return json.data as T;
}

export const api = {
  getTasks: () => request<any[]>("/api/tasks"),

  createTask: (data: any) =>
    request<any>("/api/tasks", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateTask: (id: number, data: any) =>
    request<any>(`/api/tasks/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  deleteTask: (id: number) =>
    request<any>(`/api/tasks/${id}`, {
      method: "DELETE",
    }),

  toggleComplete: (id: number) =>
    request<any>(`/api/tasks/${id}/complete`, {
      method: "PATCH",
    }),

  // Phase V: Advanced Features
  searchTasks: (keyword: string) => {
    const params = new URLSearchParams({ keyword });
    return request<any[]>(`/api/tasks/search?${params}`);
  },

  filterSortTasks: (params: any) => {
    const queryParams = new URLSearchParams();
    Object.keys(params).forEach(key => {
      if (params[key] !== undefined && params[key] !== null && params[key] !== '') {
        queryParams.append(key, params[key]);
      }
    });
    return request<any[]>(`/api/tasks/filter-sort?${queryParams}`);
  },

  markReminderSent: (id: number) =>
    request<any>(`/api/tasks/${id}/mark-reminder-sent`, {
      method: "PATCH",
    }),
};