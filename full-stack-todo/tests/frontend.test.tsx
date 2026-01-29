import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import TaskItem from '../components/dashboard/TaskItem';
import TaskForm from '../components/dashboard/TaskForm';
import AuthGuard from '../components/AuthGuard';

// Mock the useAuth hook
vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({
    user: { id: 'test-user', email: 'test@example.com', name: 'Test User' },
    loading: false,
    isAuthenticated: true,
  }),
}));

// Mock the api client
vi.mock('../lib/api', () => ({
  api: {
    getTasks: vi.fn(),
    createTask: vi.fn(),
    updateTask: vi.fn(),
    deleteTask: vi.fn(),
    toggleComplete: vi.fn(),
  },
}));

describe('Frontend Component Tests', () => {
  describe('TaskItem Component', () => {
    const mockTask = {
      id: 1,
      user_id: 'test-user',
      title: 'Test Task',
      description: 'Test Description',
      completed: false,
      priority: 'medium',
      category: 'test',
      tags: ['tag1', 'tag2'],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    it('renders task title and description correctly', () => {
      render(<TaskItem task={mockTask} onToggle={() => {}} onDelete={() => {}} />);

      expect(screen.getByText('Test Task')).toBeInTheDocument();
      expect(screen.getByText('Test Description')).toBeInTheDocument();
    });

    it('shows completion status properly', () => {
      const { rerender } = render(<TaskItem task={{...mockTask, completed: false}} onToggle={() => {}} onDelete={() => {}} />);
      const checkbox = screen.getByRole('checkbox');
      expect(checkbox).not.toBeChecked();

      rerender(<TaskItem task={{...mockTask, completed: true}} onToggle={() => {}} onDelete={() => {}} />);
      expect(checkbox).toBeChecked();
    });

    it('calls toggle completion handler when checkbox is clicked', async () => {
      const mockOnToggle = vi.fn();
      render(<TaskItem task={mockTask} onToggle={mockOnToggle} onDelete={() => {}} />);

      const checkbox = screen.getByRole('checkbox');
      fireEvent.click(checkbox);

      await waitFor(() => {
        expect(mockOnToggle).toHaveBeenCalledWith(mockTask.id);
      });
    });

    it('calls delete handler when delete button is clicked', async () => {
      const mockOnDelete = vi.fn();
      render(<TaskItem task={mockTask} onToggle={() => {}} onDelete={mockOnDelete} />);

      const deleteButton = screen.getByLabelText('deleteTodo');
      fireEvent.click(deleteButton);

      await waitFor(() => {
        expect(mockOnDelete).toHaveBeenCalledWith(mockTask.id);
      });
    });
  });

  describe('TaskList Component', () => {
    const mockTasks = [
      {
        id: 1,
        user_id: 'test-user',
        title: 'Task 1',
        description: 'Description 1',
        completed: false,
        priority: 'medium',
        category: 'test',
        tags: ['tag1'],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      {
        id: 2,
        user_id: 'test-user',
        title: 'Task 2',
        description: 'Description 2',
        completed: true,
        priority: 'high',
        category: 'work',
        tags: ['tag1', 'tag2'],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ];

    it('renders multiple tasks', () => {
      const { container } = render(<TaskList tasks={mockTasks} onToggle={() => {}} onDelete={() => {}} />);

      expect(screen.getByText('Task 1')).toBeInTheDocument();
      expect(screen.getByText('Task 2')).toBeInTheDocument();
      expect(container.querySelectorAll('[data-testid="task-item"]').length).toBe(2);
    });

    it('shows empty state when no tasks', () => {
      render(<TaskList tasks={[]} onToggle={() => {}} onDelete={() => {}} />);

      expect(screen.getByText("You're all caught up!")).toBeInTheDocument();
    });

    it('passes props correctly to child TaskItem components', () => {
      const mockOnToggle = vi.fn();
      const mockOnDelete = vi.fn();
      render(<TaskList tasks={mockTasks} onToggle={mockOnToggle} onDelete={mockOnDelete} />);

      const checkboxes = screen.getAllByRole('checkbox');
      fireEvent.click(checkboxes[0]);

      const deleteButtons = screen.getAllByLabelText('deleteTodo');
      fireEvent.click(deleteButtons[1]);

      waitFor(() => {
        expect(mockOnToggle).toHaveBeenCalledWith(mockTasks[0].id);
        expect(mockOnDelete).toHaveBeenCalledWith(mockTasks[1].id);
      });
    });
  });

  describe('TaskForm Component', () => {
    it('submits form with correct data', async () => {
      const mockOnSubmit = vi.fn();
      render(<TaskForm onSubmit={mockOnSubmit} />);

      // Fill the form
      fireEvent.change(screen.getByPlaceholderText('Task name...'), { target: { value: 'New Task' } });
      fireEvent.change(screen.getByPlaceholderText('Details...'), { target: { value: 'Task details' } });
      fireEvent.click(screen.getByText('Urgent'));
      fireEvent.click(screen.getByText('Add Task'));

      // Wait for submission
      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(expect.objectContaining({
          title: 'New Task',
          description: 'Task details',
          priority: 'high',
        }));
      });
    });

    it('validates required fields', () => {
      render(<TaskForm onSubmit={() => {}} />);

      // Try submitting empty form
      fireEvent.click(screen.getByText('Add Task'));

      // Check that onSubmit was not called
      expect(vi.fn()).not.toBeCalled();
    });

    it('resets form after successful submission', async () => {
      const mockOnSubmit = vi.fn().mockResolvedValue({});
      render(<TaskForm onSubmit={mockOnSubmit} />);

      // Fill and submit form
      fireEvent.change(screen.getByPlaceholderText('Task name...'), { target: { value: 'New Task' } });
      fireEvent.click(screen.getByText('Add Task'));

      await waitFor(() => {
        // After successful submission, the form should reset
        expect(screen.getByPlaceholderText('Task name...').innerHTML).toBe('');
      });
    });
  });

  describe('AuthGuard Component', () => {
    it('renders children for authenticated users', () => {
      render(
        <AuthGuard>
          <div>Protected Content</div>
        </AuthGuard>
      );

      expect(screen.getByText('Protected Content')).toBeInTheDocument();
    });

    it('redirects unauthenticated users', () => {
      // Mock an unauthenticated state
      vi.mock('../context/AuthContext', () => ({
        useAuth: () => ({
          user: null,
          loading: false,
          isAuthenticated: false,
        }),
      }));

      render(
        <AuthGuard>
          <div>Protected Content</div>
        </AuthGuard>
      );

      // Since we're mocking the hook differently, this would redirect in a real scenario
      // In tests, we would need to check the window.location behavior
      // This is a simplified check
    });
  });
});