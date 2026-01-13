# Phase III: AI-Powered Todo Chatbot with MCP Architecture - Specification

## 1. Problem Statement

Transform the existing web-based todo application into an AI-powered conversational interface using OpenAI ChatKit, OpenAI Agents SDK, and MCP (Model Context Protocol) server architecture. The application should maintain all functionality of Phase I and II while adding natural language interaction capabilities, enabling users to manage their todos through conversational commands with intelligent assistance.

## 2. User Stories

### 2.1 AI Chatbot Interaction
- **As an authenticated user**, I want to interact with an AI chatbot through natural language so that I can manage my todos conversationally
- **As an authenticated user**, I want the AI chatbot to understand my intent when I say things like "add a task to buy groceries" so that I don't need to use specific command formats
- **As an authenticated user**, I want the AI chatbot to maintain context of our conversation so that I can refer to previous interactions naturally
- **As an authenticated user**, I want the AI chatbot to confirm important actions like deletions so that I don't accidentally lose important tasks

### 2.2 Core Todo Functionality via Chat
- **As an authenticated user**, I want to create new todos by telling the AI "add a task to call mom" so that I can add tasks without clicking through forms
- **As an authenticated user**, I want to see my pending tasks by asking "what's pending?" so that I can quickly check my upcoming tasks
- **As an authenticated user**, I want to mark tasks as completed by saying "mark task 3 as complete" so that I can check items off efficiently
- **As an authenticated user**, I want to update existing tasks by saying "change task 1 to 'Call mom tonight'" so that I can modify details conversationally
- **As an authenticated user**, I want to delete tasks by saying "delete the meeting task" so that I can remove irrelevant items easily

### 2.3 Conversation Management
- **As an authenticated user**, I want to continue conversations across sessions so that I can pick up where I left off
- **As an authenticated user**, I want to start new conversations when needed so that I can organize my discussions
- **As an authenticated user**, I want my conversation history to be private and secure so that others cannot access my interactions

## 3. Functional Requirements

### 3.1 AI Agent System
- **Natural Language Processing**: AI agent must understand natural language commands related to todo management
- **Intent Recognition**: AI agent must recognize user intent (create, list, complete, delete, update) from natural language
- **MCP Integration**: AI agent must use MCP tools to perform todo operations
- **Response Generation**: AI agent must provide helpful, contextual responses to user queries
- **Action Confirmation**: AI agent must confirm destructive actions (deletions, completions) with the user

### 3.2 MCP Server Architecture
- **MCP Tools Exposure**: MCP server must expose standardized tools for todo operations
- **Tool Specifications**: MCP tools must follow the specified interface for add_task, list_tasks, complete_task, delete_task, update_task
- **Stateless Operation**: MCP server must be stateless, storing all state in the database
- **User Isolation**: MCP tools must enforce user isolation, only allowing operations on user's own data
- **Error Handling**: MCP tools must provide clear error responses for invalid operations

### 3.3 Chat API Endpoints
- **POST /api/{user_id}/chat**: Receive user message and return AI response with tool calls
- **Request Body**: Must accept conversation_id (optional) and message (required)
- **Response Format**: Must return conversation_id, response text, and tool_calls array
- **Conversation Management**: Must create new conversation if none provided
- **Message Persistence**: Must store user and assistant messages in database

### 3.4 MCP Tools Specification
- **add_task Tool**: Create new task with user_id, title (required), description (optional); return task_id, status, title
- **list_tasks Tool**: Retrieve tasks with user_id (required), status filter (optional: all, pending, completed); return array of task objects
- **complete_task Tool**: Mark task as complete with user_id (required), task_id (required); return task_id, status, title
- **delete_task Tool**: Remove task with user_id (required), task_id (required); return task_id, status, title
- **update_task Tool**: Modify task with user_id (required), task_id (required), title/description (optional); return task_id, status, title

### 3.5 Data Persistence
- **Conversation Storage**: Chat conversations stored persistently in Neon Serverless PostgreSQL
- **Message History**: Individual messages stored with user_id, conversation_id, role (user/assistant), content
- **State Management**: Conversation state stored in database, not server memory
- **User Association**: All chat data linked to specific users via user_id
- **Data Recovery**: Conversations persist across application restarts and user sessions

### 3.6 Frontend Integration
- **Chat Interface**: OpenAI ChatKit integration for conversational UI
- **Domain Allowlist**: Proper OpenAI domain key configuration for ChatKit security
- **JWT Integration**: Chat interface must maintain user authentication
- **Real-time Updates**: Interface must display AI responses in real-time

## 4. Non-Functional Requirements

### 4.1 Performance
- AI response time should be under 3 seconds for typical queries
- MCP tool calls should execute within 500ms
- Database operations should complete within 200ms
- Chat interface should handle typing indicators and streaming responses

### 4.2 Usability
- Conversational interface should feel natural and intuitive
- AI should handle common variations of commands (synonyms, different phrasing)
- Clear feedback when actions are taken or errors occur
- Graceful handling of ambiguous or unclear user requests

### 4.3 Reliability
- Stateless server architecture with database-persisted state
- MCP tools must be reliable and consistently available
- Conversation continuity across server restarts
- Proper error handling and graceful degradation

### 4.4 Security
- All MCP tool calls must be authenticated and enforce user isolation
- JWT token validation for all chat endpoints
- MCP tools must only operate on user's own data
- Secure domain configuration for ChatKit integration
- No exposure of sensitive data in chat responses

### 4.5 Scalability
- Stateless architecture enables horizontal scaling
- Database-based state management supports multiple server instances
- MCP tools designed for concurrent access patterns
- Conversation state decoupled from server instance

## 5. Domain Model

Based on the constitution, extending the Phase I+II model with Phase III additions:

```
Task (Phase I + Phase II + Phase III):
  - user_id: string (foreign key for user association)
  - id: unique identifier (integer, auto-incrementing)
  - title: short description (string, required)
  - description: detailed text (string, optional)
  - completed: boolean status (default: false)
  - priority: enum (low, medium, high) - Phase II addition
  - tags: list of strings - Phase II addition
  - category: single classification - Phase II addition
  - created_at: timestamp - Phase II addition
  - updated_at: timestamp - Phase II addition
  - due_date: optional deadline - Phase III addition
  - recurrence: optional repeat pattern - Phase III addition
  - reminders: list of reminder configs - Phase III addition
  - assigned_to: user/agent reference - Phase III addition
  - parent_id: for subtasks - Phase III addition
  - conversation_id: reference for chatbot interactions - Phase III addition

Conversation (Phase III):
  - user_id: string (foreign key for user association)
  - id: unique identifier (integer, auto-incrementing)
  - created_at: timestamp
  - updated_at: timestamp

Message (Phase III):
  - user_id: string (foreign key for user association)
  - id: unique identifier (integer, auto-incrementing)
  - conversation_id: reference to Conversation
  - role: string (user/assistant)
  - content: string (message content)
  - created_at: timestamp
```

## 6. Technical Constraints

### 6.1 Platform & Architecture
- **Frontend**: OpenAI ChatKit for conversational UI integrated with Next.js
- **Backend**: Python FastAPI with OpenAI Agents SDK and Official MCP SDK
- **Database**: Neon Serverless PostgreSQL with SQLModel ORM
- **AI Framework**: OpenAI Agents SDK for AI logic
- **MCP Server**: Official MCP SDK for standardized tool interfaces
- **Authentication**: Better Auth with JWT tokens for user management

### 6.2 Dependencies
- **Frontend**: OpenAI ChatKit, Next.js, React, TypeScript, Tailwind CSS, Better Auth client
- **Backend**: FastAPI, SQLModel, Pydantic, OpenAI Agents SDK, Official MCP SDK, uv for package management
- **AI**: OpenAI API keys and domain allowlist configuration
- **Database**: Neon Serverless PostgreSQL with proper connection pooling

### 6.3 Architecture
- **Stateless Servers**: Chat endpoints hold no state, all conversation data in database
- **MCP Tool Integration**: AI agents call standardized MCP tools for todo operations
- **Database-Driven State**: Conversation state managed in PostgreSQL, not server memory
- **Security**: MCP tools enforce user isolation, JWT tokens validate all requests

## 7. Acceptance Criteria

### 7.1 AI Chatbot Functionality
- [ ] AI understands natural language commands for todo operations
- [ ] AI correctly maps user intents to appropriate MCP tool calls
- [ ] AI confirms destructive actions (deletions, completions) appropriately
- [ ] AI provides helpful responses with action confirmations
- [ ] AI handles errors gracefully with user-friendly messages

### 7.2 MCP Tools Implementation
- [ ] add_task tool creates new tasks with proper user isolation
- [ ] list_tasks tool retrieves tasks with optional status filtering
- [ ] complete_task tool marks tasks as completed
- [ ] delete_task tool removes tasks with proper validation
- [ ] update_task tool modifies task details appropriately
- [ ] All MCP tools store state in database, not server memory

### 7.3 Chat API Compliance
- [ ] POST /api/{user_id}/chat endpoint accepts and processes messages
- [ ] Conversation state properly managed and persisted
- [ ] User messages stored in database with proper metadata
- [ ] Assistant responses stored in database with proper metadata
- [ ] JWT authentication enforced on all chat endpoints

### 7.4 Frontend Integration
- [ ] OpenAI ChatKit properly integrated with domain allowlist configuration
- [ ] Chat interface displays conversation history correctly
- [ ] Real-time responses from AI displayed properly
- [ ] User authentication maintained throughout chat session

### 7.5 Performance & Security
- [ ] Chat responses delivered within 3 seconds
- [ ] MCP tool calls complete within 500ms
- [ ] User data isolation maintained across all operations
- [ ] Conversation state persists across server restarts
- [ ] MCP tools enforce user authentication and authorization

## 8. Success Metrics

- AI correctly interprets 90% of natural language commands
- Average response time under 2 seconds
- 100% user data isolation maintained across all operations
- Conversation state properly persisted and recoverable
- All MCP tools functioning with proper error handling
- User satisfaction rating of 4+ stars for conversational experience

## 9. Out of Scope

- Voice-to-text conversion (text-only chatbot initially)
- Multi-modal interactions (images, video)
- Integration with external calendar systems
- Email notifications for chatbot activities
- Advanced analytics on chatbot usage patterns
- Real-time collaborative chat between users
- Offline chatbot capabilities

## 10. Edge Cases

- Handling ambiguous or unclear user commands
- Managing very long conversations (thousands of messages)
- Handling network interruptions during chat sessions
- Recovering from AI service outages
- Managing concurrent conversations for the same user
- Handling invalid task IDs in user commands
- Graceful degradation when MCP tools are unavailable
- Rate limiting for API calls to prevent abuse