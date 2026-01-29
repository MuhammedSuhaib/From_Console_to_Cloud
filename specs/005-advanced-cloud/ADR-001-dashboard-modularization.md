# ADR-001: Dashboard Component Modularization

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-01-29
- **Feature:** Phase V - Advanced Cloud Deployment
- **Context:** The dashboard page in the full-stack todo application had become monolithic with all components in a single file, making the code difficult to maintain, test, and extend.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We decided to refactor the dashboard page by:
1. Creating a dedicated `/dashboard` directory within components
2. Breaking down the monolithic dashboard page into focused, reusable components
3. Implementing proper loading states throughout the application
4. Establishing clear separation of concerns

**Components Created:**
- `Header.tsx` - User information and logout functionality
- `StatsSection.tsx` - Statistics display with Total/Active/Done counts
- `TaskList.tsx` - Task listing with loading states
- `TaskCard.tsx` - Individual task display with loading indicators
- `ChatInterface.tsx` - AI chat functionality
- `ConversationsSidebar.tsx` - Conversation history sidebar
- `FloatingActions.tsx` - Floating action buttons
- `SearchBar.tsx` - Search functionality
- `FilterSortControls.tsx` - Filtering and sorting controls
- `TaskModal.tsx` - Task creation/editing modal
- `DashboardUI.tsx` - Shared UI components (StatBox, PriorityBtn)

**Loading State Implementation:**
- Added loading states for all major operations (toggle, delete, search, filter)
- Created SmallSpinner component for inline loading indicators
- Implemented section-level loading indicators
- Proper try/finally blocks to ensure loading states are always reset

<!-- For technology stacks, list all components:
     - Framework: Next.js 14 (App Router)
     - Styling: Tailwind CSS v3
     - Deployment: Vercel
     - State Management: React Context (start simple)
-->

## Consequences

### Positive

- Improved maintainability with clear separation of concerns
- Enhanced user experience with proper loading feedback
- Better testability with smaller, focused components
- Increased code reusability
- Clearer component hierarchy and responsibilities

<!-- Example: Integrated tooling, excellent DX, fast deploys, strong TypeScript support -->

### Negative

- Increased number of files to manage
- Potential import complexity that needs to be carefully managed
- Learning curve for developers unfamiliar with the new structure

<!-- Example: Vendor lock-in to Vercel, framework coupling, learning curve -->

## Alternatives Considered

Alternative A: Keep the monolithic dashboard page with all components inline
- Why rejected: Led to poor maintainability, difficult testing, and code duplication

Alternative B: Partial modularization with only some components extracted
- Why rejected: Would not provide full benefits of separation of concerns and would create inconsistent architecture

<!-- Group alternatives by cluster:
     Alternative Stack A: Remix + styled-components + Cloudflare
     Alternative Stack B: Vite + vanilla CSS + AWS Amplify
     Why rejected: Less integrated, more setup complexity
-->

## References

- Feature Spec: @specs/005-advanced-cloud/spec.md
- Implementation Plan: @specs/005-advanced-cloud/plan.md
- Related ADRs:
- Evaluator Evidence: @history/prompts/005-advanced-cloud/0001-dashboard-modularization.phr.prompt.md