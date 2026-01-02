# REST API Endpoints

## Base URL
- Development: http://localhost:8000
- Production: https://api.example.com

## Authentication
All endpoints require JWT token in header:
`Authorization: Bearer <token>`

## Endpoints

### GET /api/{user_id}/tasks
List all tasks for authenticated user.

Query Parameters:
- status: "all" | "pending" | "completed" (default: "all")
- priority: "low" | "medium" | "high" (optional filter)
- sort: "created" | "title" | "priority" (default: "created")
- page: integer (default: 1)
- limit: integer (default: 20)

Response: Array of Task objects
Status: 200 OK

### POST /api/{user_id}/tasks
Create a new task.

Request Body:
```
{
  "title": string (required, 1-200 chars),
  "description": string (optional, max 1000 chars),
  "priority": "low" | "medium" | "high" (optional, default: "medium"),
  "category": string (optional, max 50 chars),
  "tags": string[] (optional, default: [])
}
```

Response: Created Task object
Status: 201 Created

### GET /api/{user_id}/tasks/{id}
Get specific task details.

Path Parameters:
- user_id: authenticated user ID
- id: task ID

Response: Task object
Status: 200 OK | 404 Not Found | 403 Forbidden

### PUT /api/{user_id}/tasks/{id}
Update an existing task.

Path Parameters:
- user_id: authenticated user ID
- id: task ID

Request Body (all optional, partial updates allowed):
```
{
  "title": string (optional, 1-200 chars),
  "description": string (optional, max 1000 chars),
  "priority": "low" | "medium" | "high" (optional),
  "category": string (optional, max 50 chars),
  "tags": string[] (optional),
  "completed": boolean (optional)
}
```

Response: Updated Task object
Status: 200 OK | 404 Not Found | 403 Forbidden

### DELETE /api/{user_id}/tasks/{id}
Delete a specific task.

Path Parameters:
- user_id: authenticated user ID
- id: task ID

Response: { "message": "Task deleted successfully" }
Status: 200 OK | 404 Not Found | 403 Forbidden

### PATCH /api/{user_id}/tasks/{id}/complete
Toggle task completion status.

Path Parameters:
- user_id: authenticated user ID
- id: task ID

Response: Updated Task object with toggled completion status
Status: 200 OK | 404 Not Found | 403 Forbidden

## Error Response Format
All error responses follow this format:
```
{
  "detail": "Error message describing the issue"
}
```

Status Codes:
- 200 OK: Request successful
- 201 Created: Resource successfully created
- 400 Bad Request: Invalid input data
- 401 Unauthorized: Missing or invalid JWT token
- 403 Forbidden: User not authorized for this resource
- 404 Not Found: Requested resource does not exist
- 500 Internal Server Error: Server error occurred