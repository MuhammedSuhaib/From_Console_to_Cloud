# Docker Compose Configuration for Full-Stack Todo Application

This document provides instructions for setting up and running the Full-Stack Todo Application using Docker Compose for local development.

## Overview

The Docker Compose configuration sets up a complete development environment with:
- Frontend: Next.js application running on port 3000
- Backend: FastAPI server running on port 8000
- Database: PostgreSQL server running on port 5432
- Cache: Redis server running on port 6379 (optional)

## Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose v2+
- At least 4GB of free RAM recommended

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd From_Console_to_Cloud
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
# .env
SECRET_KEY=your_very_long_random_secret_key_for_development
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

### 3. Build and Start Services

```bash
# Build and start all services in detached mode
docker compose up --build -d

# Or start without detached mode to see logs
docker compose up --build
```

### 4. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Backend Documentation: http://localhost:8000/docs (if enabled in development)

## Service Configuration

### Backend Service

- **Port**: 8000 (accessible from host)
- **Container Port**: 7860 (internal container port)
- **Build Context**: `./backend`
- **Environment Variables**:
  - `DATABASE_URL`: PostgreSQL connection string
  - `SECRET_KEY`: JWT secret key
  - `ENVIRONMENT`: Set to "development"
  - `LOG_LEVEL`: Set to "DEBUG" for development

### Frontend Service

- **Port**: 3000 (accessible from host)
- **Build Context**: `./full-stack-todo`
- **Environment Variables**:
  - `NEXT_PUBLIC_API_URL`: Backend API URL
  - `NEXT_PUBLIC_BETTER_AUTH_URL`: Authentication URL

### Database Service

- **Port**: 5432 (accessible from host)
- **Image**: postgres:15
- **Database**: `todo_app`
- **User**: `postgres`
- **Password**: `postgres`
- **Initialization**: Runs `init.sql` on first startup

### Redis Service (Optional)

- **Port**: 6379 (accessible from host)
- **Image**: redis:7-alpine
- **Purpose**: Caching and session management

## Development Commands

### Build Services
```bash
# Build all services
docker compose build

# Build specific service
docker compose build backend
docker compose build frontend
```

### Start/Stop Services
```bash
# Start all services in detached mode
docker compose up -d

# Stop all services
docker compose down

# Stop specific service
docker compose stop backend

# Restart services
docker compose restart
```

### View Logs
```bash
# View logs for all services
docker compose logs

# View logs for specific service
docker compose logs backend
docker compose logs frontend
docker compose logs db

# Follow logs in real-time
docker compose logs -f backend
```

### Execute Commands in Containers
```bash
# Access backend container
docker compose exec backend bash

# Access frontend container
docker compose exec frontend sh

# Access database container
docker compose exec db psql -U postgres -d todo_app
```

## Development Workflow

### With Docker Compose

1. **Initial Setup**:
   ```bash
   docker compose build
   docker compose up -d
   ```

2. **During Development**:
   - The backend service is configured with `--reload` for hot reloading
   - Code changes in `./backend` are reflected in the container
   - Frontend changes require rebuilding the container

3. **Database Operations**:
   ```bash
   # Run migrations (execute inside backend container)
   docker compose exec backend python -m alembic upgrade head

   # Connect to database
   docker compose exec db psql -U postgres -d todo_app
   ```

### Alternative Development Approach

For active frontend development, you might prefer running the frontend locally:

1. **Start only backend and database**:
   ```bash
   docker compose up -d backend db
   ```

2. **Run frontend locally**:
   ```bash
   cd full-stack-todo
   pnpm install
   pnpm dev
   ```

## Environment Variables

### Root .env File

Create a `.env` file in the project root:

```env
# JWT Secret (at least 32 characters for production)
SECRET_KEY=very_long_random_string_for_development

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000

# Database (only needed if overriding defaults)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/todo_app
```

### Per-Service Environment Files

You can also create environment files for specific services:
- `./backend/.env` - Backend-specific variables
- `./full-stack-todo/.env` - Frontend-specific variables

## Database Initialization

The database is initialized with the `init.sql` file on first startup. This file creates:
- `users` table
- `tasks` table
- Required indexes
- Sample data (optional)

If you modify `init.sql`, you'll need to recreate the database container:
```bash
# Remove database volume (WARNING: This deletes all data!)
docker compose down
docker volume rm from_console_to_cloud_postgres_data
docker compose up -d
```

## Troubleshooting

### Common Issues

#### Port Already in Use
If you get "port already in use" errors:
1. Check if services are already running: `docker compose ps`
2. Stop conflicting services or change ports in `docker-compose.yml`

#### Dependency Installation Issues
If dependencies fail to install:
1. Clear Docker build cache: `docker builder prune`
2. Rebuild with: `docker compose build --no-cache`

#### Database Connection Issues
If the backend can't connect to the database:
1. Check that the database service is running: `docker compose ps`
2. Verify the `DATABASE_URL` environment variable
3. Check database logs: `docker compose logs db`

### Useful Commands

```bash
# Check running services
docker compose ps

# Check resource usage
docker stats

# Clean up unused resources
docker system prune

# Remove all containers, networks, images, and volumes
docker compose down -v
docker system prune -a
```

## Production Considerations

### Differences from Production

This development configuration includes:
- Hot reloading capabilities
- Direct volume mounts for live code updates
- Less restrictive security settings
- Development-focused logging

### Production Setup

For production deployment, consider:
- Using a production-ready reverse proxy (nginx)
- SSL termination
- Separate build and runtime images
- Proper secrets management
- Database backup strategies
- Monitoring and alerting

## Customization

### Changing Ports

Modify the port mappings in `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "8001:7860"  # Change host port from 8000 to 8001
  frontend:
    ports:
      - "3001:3000"  # Change host port from 3000 to 3001
```

### Adding Services

To add new services (like Elasticsearch, RabbitMQ, etc.), add them to `docker-compose.yml`:

```yaml
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    ports:
      - "9200:9200"
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
```

## Docker Compose Profiles

Different configurations are available:

- **Default** (`docker compose up`): Full development stack
- **Development** (`docker compose -f docker-compose.dev.yml up`): Development-specific configuration

## Cleanup

To completely clean up Docker resources:

```bash
# Stop and remove containers, networks, and volumes
docker compose down -v

# Remove associated images (optional)
docker compose down --rmi all

# Clean up unused Docker resources
docker system prune
```

This Docker Compose setup provides a complete local development environment that mirrors production as closely as possible while enabling rapid development and iteration.