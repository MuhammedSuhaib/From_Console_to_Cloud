// lib/api.ts
import { Task, TaskCreate, TaskUpdate } from '../types';

class ApiClient {
  private baseUrl: string;
  
  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = this.getAuthToken();
    const headers = {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    };

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      // Handle unauthorized - maybe redirect to login
      console.error('Unauthorized access - redirecting to login');
      // window.location.href = '/auth/signin'; // Uncomment in actual implementation
      throw new Error('Unauthorized: Please login again');
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `API request failed: ${response.statusText}`);
    }

    return response.json();
  }

  private getAuthToken(): string | null {
    // Get JWT token from storage (could be localStorage, cookie, etc.)
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token');
    }
    return null;
  }

  async getTasks(userId: string): Promise<Task[]> {
    return this.request<Task[]>(`/api/users/${userId}/tasks`);
  }

  async createTask(userId: string, task: TaskCreate): Promise<Task> {
    return this.request<Task>(`/api/users/${userId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(task),
    });
  }

  async getTask(userId: string, taskId: number): Promise<Task> {
    return this.request<Task>(`/api/users/${userId}/tasks/${taskId}`);
  }

  async updateTask(userId: string, taskId: number, updates: TaskUpdate): Promise<Task> {
    return this.request<Task>(`/api/users/${userId}/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  async deleteTask(userId: string, taskId: number): Promise<void> {
    await this.request(`/api/users/${userId}/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }

  async toggleTaskCompletion(userId: string, taskId: number): Promise<Task> {
    return this.request<Task>(`/api/users/${userId}/tasks/${taskId}/complete`, {
      method: 'PATCH',
    });
  }
}

export const api = new ApiClient();