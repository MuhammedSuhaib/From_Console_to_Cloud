# UI Components

## Page Structure

### Dashboard Page (`/app/page.tsx`)
- Main application page showing user's tasks
- Includes authentication guard to redirect unauthenticated users
- Displays user's task list with filtering and sorting options
- Provides form for creating new tasks
- Shows user information and sign-out option

### Authentication Pages
- `/app/auth/signin/page.tsx` - Sign-in form
- `/app/auth/signup/page.tsx` - Sign-up form
- Both pages redirect authenticated users to dashboard

## Core Components

### TaskList Component (`/components/TaskList.tsx`)
- Displays list of tasks in a responsive grid or list format
- Implements filtering by completion status (all, pending, completed)
- Implements sorting options (by date, priority, title)
- Handles empty state when no tasks exist
- Provides visual indicators for task priority

### TaskItem Component (`/components/TaskItem.tsx`)
- Displays individual task information
- Shows title, description, status, priority, and category
- Provides controls to toggle completion status
- Includes edit and delete buttons
- Visual styling differs based on completion status

### TaskForm Component (`/components/TaskForm.tsx`)
- Form for creating and editing tasks
- Inputs for title (required) and description (optional)
- Priority selection dropdown (low, medium, high)
- Category input field
- Tags input with multi-select capability
- Submit and cancel buttons
- Form validation with error messages

### AuthGuard Component (`/components/AuthGuard.tsx`)
- Wrapper component that checks authentication status
- Redirects unauthenticated users to sign-in page
- Provides current user context to child components

## Layout Components

### MainLayout (`/app/layout.tsx`)
- App-wide layout with header and navigation
- Includes user authentication status
- Responsive design for mobile and desktop
- Global styles and meta information

### Header Component (`/components/Header.tsx`)
- Navigation between different sections of the app
- User profile dropdown with sign-out option
- Responsive navigation for mobile devices

## Styling

### Color Palette
- Primary: Brand color for interactive elements
- Success: Green for completed tasks and success messages
- Warning: Yellow for pending tasks
- Danger: Red for delete actions and errors
- Neutral: Gray for backgrounds and subtle elements

### Typography
- Use Tailwind CSS typography utilities for consistency
- Clear visual hierarchy with heading levels
- Accessible font sizes and contrast ratios

## Responsive Design
- Mobile-first approach with responsive breakpoints
- Grid and flexbox layouts adapt to screen size
- Touch-friendly controls for mobile devices
- Appropriate spacing on all screen sizes

## Accessibility
- Proper ARIA labels and roles
- Semantic HTML elements
- Keyboard navigable components
- Sufficient color contrast
- Screen reader support