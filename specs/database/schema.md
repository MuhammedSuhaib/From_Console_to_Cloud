# Database Schema

## Tables

### users (managed by Better Auth)
- id: string (primary key) - Better Auth user ID
- email: string (unique) - User's email address
- name: string (nullable) - User's display name
- created_at: timestamp - Account creation time

### tasks (managed by our application)
- id: integer (primary key, auto-increment) - Task unique identifier
- user_id: string (foreign key -> users.id) - Owner of the task
- title: string (not null, 1-200 characters) - Task title
- description: text (nullable, max 1000 characters) - Task description
- completed: boolean (default false) - Completion status
- priority: string enum ('low', 'medium', 'high', default 'medium') - Task priority
- category: string (nullable, max 50 characters) - Task category
- tags: jsonb (default empty array) - Array of task tags
- created_at: timestamp (default current timestamp) - Creation time
- updated_at: timestamp (default current timestamp) - Last update time

## Indexes

### Primary Keys
- users.id
- tasks.id

### Foreign Key Constraints
- tasks.user_id references users.id - Enforces referential integrity

### Additional Indexes
- tasks.user_id (for efficient filtering by user)
- tasks.completed (for status filtering)
- tasks.priority (for priority filtering)
- tasks.created_at (for chronological sorting)

## Relationships
- One user to many tasks (one-to-many)
- Tasks are owned by a single user (user_id field)

## Constraints
- tasks.title must be between 1-200 characters
- tasks.description must be max 1000 characters if provided
- tasks.category must be max 50 characters if provided
- tasks.priority must be one of 'low', 'medium', 'high'
- tasks.user_id must reference a valid user in the users table
- Cascade delete on user deletion would remove all their tasks (optional depending on requirements)

## Notes
- The users table is primarily managed by Better Auth
- Our application will only read from the users table to validate user existence
- The tasks table is fully managed by our application
- All timestamps use ISO 8601 format (UTC)