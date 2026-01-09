# Phase II - Full-Stack Todo Application Guidelines

## Project Overview
This is a monorepo using GitHub Spec-Kit for spec-driven development. This is the root CLAUDE.md file that provides an overview of the entire project.

## Spec-Kit Structure
Specifications are organized in `specs/`:
- `specs/overview.md` - Project overview
- `specs/features/` - Feature specs (what to build)
- `specs/api/` - API endpoint and MCP tool specs
- `specs/database/` - Schema and model specs
- `specs/ui/` - Component and page specs

## How to Use Specs
1. Always read relevant spec before implementing
2. Reference specs with: `@specs/features/task-crud.md`
3. Update specs if requirements change

## Project Structure
- `frontend/` - Next.js 16+ application
- `backend/` - Python FastAPI server
- `specs/002-web-todo/` - Phase II specifications

## Development Workflow
1. Read spec: `@specs/002-web-todo/spec.md`
2. Review plan: `@specs/002-web-todo/plan.md`
3. Follow tasks: `@specs/002-web-todo/tasks.md`
4. Implement backend: `@backend/CLAUDE.md`
5. Implement frontend: `@frontend/CLAUDE.md`
6. Test and iterate

## Commands
- Frontend: `cd frontend && npm run dev`
- Backend: `cd backend && uvicorn main:app --reload`
- Both: `docker-compose up`

## Technology Stack
- Frontend: Next.js 16+, TypeScript, Tailwind CSS, Better Auth
- Backend: FastAPI, SQLModel, Pydantic, JWT
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth with JWT tokens


## PHR (Prompt History Record) Guidelines
When creating PHRs, follow these rules:
1. Use the standard template from `.specify/templates/phr-template.prompt.md`
2. Include proper model name (Claude Sonnet 4.5) and user name (get username from git config)
3. Follow the correct naming convention: `NNNN-title.stage.prompt.md`
4. Check that the ID number is not already used by another agent by using `list_directory` in the PHR folder
5. Use proper YAML front matter with all required fields
6. Include proper links to related specifications
7. List all relevant files in the `files:` section
8. Fix grammar and spelling in the content


## Key Learnings from PHR Creation
- Model name must be "Claude Sonnet 4.5", not "Qwen"
- User name is "giaic" as found in git config
- Files are stored in `history/prompts/002-web-todo/` directory with sequential numbering
- Stage labels should reflect the development phase (deployment, debugging, etc.)
- Proper surface area assessment (small, medium, large) is important
- Feature and branch information should be accurately reflected
- Labels should categorize the work appropriately
- Tests section should outline verification steps
