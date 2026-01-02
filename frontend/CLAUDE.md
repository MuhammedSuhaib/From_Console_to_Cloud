# Frontend Guidelines (Next.js Application)

## Stack
- Next.js 16+ (App Router)
- TypeScript
- Tailwind CSS
- Better Auth for authentication
- JWT tokens for API communication

## Patterns
- Use server components by default
- Client components only when needed (interactivity)
- API calls go through `/lib/api.ts`

## Component Structure
- `/app` - Pages and layouts using App Router
- `/components` - Reusable UI components
- `/lib` - Utility functions and API client
- `/styles` - Global styles

## API Client
All backend calls should use the API client:

```typescript
import { api } from '@/lib/api'
const tasks = await api.getTasks(userId)
```

## Authentication
- Integrate Better Auth for user management
- Handle JWT tokens for API authentication
- Implement auth guards for protected routes
- Securely store and manage authentication tokens

## Styling
- Use Tailwind CSS classes
- No inline styles
- Follow existing component patterns
- Implement responsive design (mobile-first)

## Best Practices
- Type safety with TypeScript interfaces
- Component reusability
- Accessibility (WCAG 2.1 AA compliance)
- Error boundaries for graceful degradation
- Proper form validation and user feedback