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

  if (!res.ok) throw new Error("API error");
  const json = await res.json();
  return json.data as T;
}

export const api = {
  getTasks: () => request("/api/tasks"),

  createTask: (data: any) =>
    request("/api/tasks", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateTask: (id: number, data: any) =>
    request(`/api/tasks/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  deleteTask: (id: number) =>
    request(`/api/tasks/${id}`, {
      method: "DELETE",
    }),

  toggleComplete: (id: number) =>
    request(`/api/tasks/${id}/complete`, {
      method: "PATCH",
    }),
};
