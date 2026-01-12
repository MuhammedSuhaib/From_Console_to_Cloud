# Full-Stack Todo Application

A modern full-stack todo application built with Next.js 16+, FastAPI, and Better Auth for authentication. This application provides a complete task management solution with user authentication and data isolation.

## Table of Contents
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Docker Setup](#docker-setup)
- [Project Structure](#project-structure)
- [Features](#features)
- [API Endpoints](#api-endpoints)
- [Authentication Flow](#authentication-flow)
- [Development](#development)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Tech Stack

- **Frontend**: Next.js 16+ (App Router), TypeScript, Tailwind CSS
- **Backend**: FastAPI, SQLModel, Pydantic
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: Better Auth with JWT tokens
- **Styling**: Tailwind CSS

## Prerequisites

- Node.js 18+ (for frontend)
- Python 3.9+ (for backend)
- pnpm package manager
- Docker and Docker Compose (optional, for containerized setup)
- PostgreSQL-compatible database (Neon recommended)

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd From_Console_to_Cloud
```

### 2. Frontend Setup

Navigate to the frontend directory and install dependencies:

```bash
cd full-stack-todo
pnpm install
```

### 3. Backend Setup

Navigate to the backend directory and set up the Python environment:

```bash
cd ../backend
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Environment Configuration

Create `.env` files in both frontend and backend directories:

**Frontend** (`full-stack-todo/.env`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

**Backend** (`backend/.env`):
```env
DATABASE_URL=postgresql://username:password@localhost:5432/todo_db
SECRET_KEY=your-secret-key-here
NEON_DATABASE_URL=your-neon-db-url
```

### 5. Database Setup

Set up the PostgreSQL database and run migrations:

```bash
cd backend
# Run database migrations
uv run alembic upgrade head
```

### 6. Running the Application

Start both frontend and backend servers:

**Backend** (in `backend/` directory):
```bash
uvicorn main:app --reload
```

**Frontend** (in `full-stack-todo/` directory):
```bash
pnpm dev
```

The application will be available at http://localhost:3000

## Docker Setup

Alternatively, you can run the entire application using Docker Compose:

### 1. Build and Start Services

```bash
# Build and start all services in detached mode
docker compose up --build -d
```

### 2. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

### 3. View Logs

```bash
# Follow logs in real-time
docker compose logs -f
```

See [Docker Compose Setup Documentation](docs/DOCKER_COMPOSE_SETUP.md) for detailed Docker configuration and troubleshooting.

## Project Structure

```
From_Console_to_Cloud/
├── full-stack-todo/          # Next.js frontend application
│   ├── app/                  # Application pages and layouts
│   ├── components/           # Reusable UI components
│   ├── lib/                  # API client and utility functions
│   └── README.md             # This file
├── backend/                  # FastAPI backend server
│   ├── models/               # Database models
│   ├── routes/               # API route handlers
│   ├── auth/                 # Authentication middleware
│   └── main.py               # Application entry point
├── docs/                     # Documentation files
│   ├── API_DOCUMENTATION.md  # API endpoints documentation
│   ├── AUTHENTICATION_FLOW.md # Authentication flow documentation
│   ├── ENVIRONMENT_VARIABLES.md # Environment variables guide
│   ├── CONFIGURATION_GUIDE.md # Development/production configuration
│   └── DOCKER_COMPOSE_SETUP.md # Docker setup documentation
└── specs/                    # Specification files
```

## Features

- User authentication and registration
- Secure JWT-based authentication
- Task CRUD operations (Create, Read, Update, Delete)
- User data isolation (users can only access their own tasks)
- Responsive UI with Tailwind CSS
- Form validation and error handling
- Real-time task management

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Login and get JWT token |
| GET | `/api/tasks` | Get all tasks for authenticated user |
| POST | `/api/tasks` | Create a new task |
| PUT | `/api/tasks/:id` | Update an existing task |
| DELETE | `/api/tasks/:id` | Delete a task |
| PATCH | `/api/tasks/:id` | Update task status |

## Authentication Flow

1. User registers or logs in via Better Auth
2. JWT token is generated and stored in localStorage
3. Token is sent with each API request in Authorization header
4. Backend verifies token and enforces user data isolation
5. Unauthorized requests are rejected with 401 status

## Development

For development, you can run both servers simultaneously using:

```bash
# Start backend in one terminal
cd backend && uvicorn main:app --reload

# Start frontend in another terminal
cd full-stack-todo && pnpm dev
```

## Deployment

### Frontend (Vercel)
1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### Backend (Docker)
A Dockerfile is provided for containerized deployment. Use the provided docker-compose.yml for easy orchestration.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License.