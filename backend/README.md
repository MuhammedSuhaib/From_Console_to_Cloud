---
title: Todo API
emoji: ✅
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
---

# Todo Backend API
FastAPI backend for the Todo application.
This is a FastAPI backend for a todo application, deployed on Hugging Face Spaces using Docker.

## API Endpoints

- `GET /api/tasks` - Get all tasks for the authenticated user
- `POST /api/tasks` - Create a new task (supports due dates, recurrence patterns)
- `PUT /api/tasks/{task_id}` - Update a task (supports due dates, recurrence patterns)
- `DELETE /api/tasks/{task_id}` - Delete a task
- `PATCH /api/tasks/{task_id}/complete` - Toggle task completion status
- `GET /api/tasks/search?q={keyword}` - Search tasks by keyword
- `GET /api/tasks/filter` - Filter and sort tasks (by priority, status, due date, tags)
- `POST /api/{user_id}/chat` - AI-powered task management via chat
- `GET /api/{user_id}/history` - Retrieve chat history
- `GET /api/{user_id}/conversations` - Manage chat conversations
- `DELETE /api/{user_id}/conversations/{id}` - Delete conversation
- `POST /api/{user_id}/reminders/check` - Check for due tasks (cron endpoint)
- `POST /api/{user_id}/events/publish` - Publish task events (Dapr/Kafka)

## Environment Variables

- `DATABASE_URL`: PostgreSQL database URL (Neon)
- `BETTER_AUTH_SECRET`: Secret for JWT token verification