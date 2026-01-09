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
- `POST /api/tasks` - Create a new task
- `PUT /api/tasks/{task_id}` - Update a task
- `DELETE /api/tasks/{task_id}` - Delete a task
- `PATCH /api/tasks/{task_id}/complete` - Toggle task completion status

## Environment Variables

- `DATABASE_URL`: PostgreSQL database URL (Neon)
- `BETTER_AUTH_SECRET`: Secret for JWT token verification