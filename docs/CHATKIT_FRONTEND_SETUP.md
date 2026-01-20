# ChatKit Frontend Setup

This document provides comprehensive instructions for setting up the ChatKit frontend integration in the AI Chatbot application. ChatKit enables seamless conversation experiences with streaming responses, typing indicators, and real-time updates.

## Overview

ChatKit is integrated into the dashboard page (`app/dashboard/page.tsx`) to provide an interactive AI chat experience. The integration connects to the backend AI endpoints and handles streaming responses with tool call indicators.

## Prerequisites

### Environment Variables
Before setting up ChatKit, ensure the following environment variables are configured:

**Frontend (.env.local):**
```
NEXT_PUBLIC_CHATKIT_WORKFLOW_ID=your-workflow-id
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_CHATKIT_DOMAIN_KEY=your-domain-key
```

**Backend (.env):**
```
OPENAI_API_KEY=your-openai-api-key
TRACING_KEY=your-tracing-key
```

### Dependencies
Ensure the following packages are installed in the frontend:

```bash
npm install @openai/chatkit-react lucide-react
```

## Installation Steps

### 1. Environment Configuration

1. Create a `.env.local` file in the `full-stack-todo` directory
2. Add the required environment variables:

```env
NEXT_PUBLIC_CHATKIT_WORKFLOW_ID=wf_your_workflow_id_here
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_CHATKIT_DOMAIN_KEY=your_domain_key_here
```

### 2. Component Integration

The ChatKit integration is already implemented in `app/dashboard/page.tsx`. Key components include:

- **useChatKit Hook**: Manages the ChatKit session and connection
- **Chat Interface**: Toggleable chat drawer with message history
- **Streaming Support**: Real-time response handling with tool call indicators
- **Conversation Management**: Browse, switch, and delete conversations

### 3. Authentication Integration

ChatKit is configured to work with the existing authentication system:

```typescript
const getClientSecret = useMemo(() => {
  return async (currentSecret: string | null) => {
    if (currentSecret) return currentSecret;
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/create-session`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
          },
          body: JSON.stringify({ workflow: { id: WORKFLOW_ID } }),
        },
      );
      const data = await res.json();
      return data.client_secret;
    } catch (err) {
      console.error("ChatKit Session Error:", err);
      return "mock_secret";
    }
  };
}, []);
```

## Configuration Options

### Workflow Configuration
- **Workflow ID**: Set via `NEXT_PUBLIC_CHATKIT_WORKFLOW_ID` environment variable
- **Domain Key**: Set via `NEXT_PUBLIC_CHATKIT_DOMAIN_KEY` environment variable
- **Session Management**: Automatic JWT token validation

### UI Components
The ChatKit integration includes several UI elements:

#### Chat Trigger
- **Location**: Bottom-left of screen
- **Icon**: MessageSquare (lucide-react)
- **Action**: Toggles chat interface

#### Chat Interface
- **Position**: Fixed overlay at bottom-left
- **Size**: 320px wide on desktop
- **Features**:
  - Message history display
  - Input field with submit button
  - Typing indicators
  - Tool call status indicators
  - Conversation management controls

#### Conversation Controls
- **New Conversation**: Creates fresh conversation context
- **View Conversations**: Shows conversation history sidebar
- **Clear History**: Wipes current conversation memory
- **Pagination Navigation**: Use left/right chevrons to navigate through message history
- **Close**: Hides chat interface

## User Experience Features

### Real-time Indicators
- **Typing Indicator**: "Wait! I am typing..." appears during AI processing
- **Tool Status**: Shows current tool being executed (e.g., "Tool Call 🛠: add_task...")
- **Loading States**: Visual feedback during operations

### Conversation Management
- **Sidebar**: Browse all user conversations
- **Preview**: First message preview with timestamp and message count
- **Deletion**: Individual conversation deletion with confirmation
- **Switching**: Instantly switch between conversations

### Responsive Design
- **Mobile**: Full-screen chat interface
- **Desktop**: Compact sidebar interface
- **Animations**: Smooth slide-in/slide-out transitions

## API Integration

### Backend Endpoints Used
- `POST /api/{user_id}/chat` - Streamed AI responses
- `GET /api/{user_id}/history` - Chat history with pagination
- `GET /api/{user_id}/conversations` - All user conversations
- `DELETE /api/{user_id}/conversations/{id}` - Delete conversation

### Request Format
Chat messages are sent with the format:
```json
{
  "message": "User's message content",
  "conversation_id": 123 (optional)
}
```

### Response Handling
The frontend handles different response types:
- **Text Chunks**: Incremental response building
- **Tool Calls**: Tool execution status updates
- **Completion**: Conversation ID and finalization
- **Errors**: Error message display

## Troubleshooting

### Common Issues

1. **ChatKit Connection Failures**
   - Verify `NEXT_PUBLIC_CHATKIT_WORKFLOW_ID` is correct
   - Check domain key validity
   - Ensure backend `/api/create-session` endpoint is accessible

2. **Authentication Problems**
   - Verify JWT token is present in localStorage
   - Check that `NEXT_PUBLIC_API_BASE_URL` matches backend URL
   - Ensure authentication headers are properly set

3. **Streaming Issues**
   - Verify backend SSE endpoint is functioning
   - Check network connectivity to backend
   - Review browser console for JavaScript errors

### Debugging Steps

1. Open browser developer tools
2. Check Network tab for API call responses
3. Verify Console for JavaScript errors
4. Confirm environment variables are properly set
5. Test backend endpoints independently

## Security Considerations

### Data Isolation
- User conversations are isolated by user ID
- JWT tokens validate user permissions
- Cross-user data access is prevented

### Token Management
- Tokens are stored securely in localStorage
- Automatic token refresh if available
- Secure transmission via HTTPS

### Input Sanitization
- User messages are sanitized before processing
- Prevents injection attacks in AI responses
- Validates all input parameters

## Customization

### Styling
The ChatKit interface uses Tailwind CSS classes that can be customized:

- **Background**: `bg-slate-900`, `bg-slate-950`
- **Borders**: `border-slate-800`
- **Text**: `text-slate-200`, `text-indigo-400`
- **Buttons**: Various hover and active states

### Branding
Update the header text "Micro Task AI" and styling to match brand requirements.

### Feature Modification
Components can be modified to add features like:
- File attachments
- Rich media responses
- Custom emoji reactions
- Advanced conversation filters