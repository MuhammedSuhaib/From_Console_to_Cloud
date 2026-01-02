# Feature: Task CRUD Operations

## User Stories

### Task Management
- As a user, I can create a new task with title and description
- As a user, I can view all my tasks with status indicators
- As a user, I can update an existing task's details
- As a user, I can delete a task from my list
- As a user, I can mark a task as completed or pending
- As a user, I can filter tasks by completion status
- As a user, I can assign priority levels (low, medium, high) to tasks
- As a user, I can categorize tasks with tags and categories

## Acceptance Criteria

### Create Task
- Title is required (1-200 characters)
- Description is optional (max 1000 characters)
- Task is associated with logged-in user
- Priority defaults to 'medium' if not specified
- Created timestamp is automatically set
- Task is marked as not completed by default

### View Tasks
- Only show tasks for current authenticated user
- Display title, status (completed/pending), priority, created date
- Support filtering by status (all, pending, completed)
- Support sorting by various fields (created date, title, priority)
- Pagination for large task lists

### Update Task
- Only allow updating tasks owned by authenticated user
- Validate title length (1-200 characters)
- Update timestamp is automatically set
- Preserve original owner and creation date
- Allow partial updates (only changed fields)

### Delete Task
- Only allow deleting tasks owned by authenticated user
- Return appropriate success confirmation
- Handle case where task doesn't exist (return 404)
- Remove task from database permanently

### Toggle Completion
- Only allow toggling tasks owned by authenticated user
- Switch completed status from true to false or vice versa
- Update timestamp is automatically set
- Return updated task with new completion status