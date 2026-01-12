# Development and Production Configuration Guide

This guide provides detailed configuration instructions for setting up the Full-Stack Todo Application in both development and production environments.

## Overview

The application consists of two main components:
- **Frontend**: Next.js 16+ application
- **Backend**: FastAPI server with PostgreSQL database

Each environment requires different configuration settings for optimal performance and security.

## Development Configuration

### Prerequisites

- Node.js 18+ with pnpm package manager
- Python 3.9+
- PostgreSQL (local installation or Docker)
- Git

### Local Development Setup

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd From_Console_to_Cloud
```

#### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd full-stack-todo

# Install dependencies
pnpm install

# Create development environment file
cp .env.example .env.local
```

#### 3. Backend Setup

```bash
# Navigate to backend directory
cd ../backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create development environment file
cp .env.example .env
```

#### 4. Database Setup

For local development, you can use either a local PostgreSQL installation or Docker:

**Option A: Local PostgreSQL**

1. Install PostgreSQL locally
2. Create a database: `CREATE DATABASE todo_dev;`
3. Update `DATABASE_URL` in `backend/.env`:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/todo_dev
   ```

**Option B: Docker PostgreSQL**

```bash
# Run PostgreSQL in Docker
docker run --name todo-postgres-dev \
  -e POSTGRES_DB=todo_dev \
  -e POSTGRES_USER=dev_user \
  -e POSTGRES_PASSWORD=dev_password \
  -p 5432:5432 \
  -d postgres:15
```

#### 5. Environment Variables for Development

**Frontend** (`full-stack-todo/.env.local`):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_DEBUG_MODE=true
```

**Backend** (`backend/.env`):
```
DATABASE_URL=postgresql://dev_user:dev_password@localhost:5432/todo_dev
SECRET_KEY=dev_secret_key_that_should_be_long_and_random_for_development_purpose_only
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ENVIRONMENT=development
LOG_LEVEL=DEBUG
NEON_DATABASE_URL=
```

#### 6. Running in Development Mode

**Backend:**
```bash
cd backend
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd full-stack-todo
pnpm dev
```

### Development-Specific Configurations

#### Next.js Configuration (`full-stack-todo/next.config.ts`)

```typescript
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  experimental: {
    typedRoutes: true,
  },
  env: {
    // Development-specific environment variables
  },
  // Enable React DevTools in development
  webpack: (config, { dev }) => {
    if (dev) {
      config.resolve.fallback = { ...config.resolve.fallback, fs: false };
    }
    return config;
  },
};

export default nextConfig;
```

#### FastAPI Development Configuration (`backend/main.py`)

```python
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging for development
if os.getenv("ENVIRONMENT") == "development":
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Todo API - Development",
    version="1.0.0",
    debug=True,  # Enable debug mode in development
)

# Allow all origins in development (not suitable for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Only in development!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Production Configuration

### Infrastructure Requirements

- Production-grade PostgreSQL database (Neon recommended)
- SSL certificate for HTTPS
- Load balancer (if scaling horizontally)
- CDN for static assets (optional but recommended)
- Monitoring and logging infrastructure

### Production Environment Setup

#### 1. Environment Variables for Production

**Frontend** (`full-stack-todo/.env.production`):
```
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_BETTER_AUTH_URL=https://yourdomain.com
NODE_ENV=production
```

**Backend** (`backend/.env.production`):
```
DATABASE_URL=postgresql://user:pass@neon-prod-host.region.provider.neon.tech/dbname
SECRET_KEY=production_secret_key_that_should_be_very_secure_and_rotated_regularly
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ENVIRONMENT=production
LOG_LEVEL=WARNING
NEON_DATABASE_URL=your_neon_connection_string
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,api.yourdomain.com
```

#### 2. Database Configuration for Production

Use a managed PostgreSQL service like Neon, AWS RDS, or Google Cloud SQL:

```sql
-- Production database setup
CREATE DATABASE todo_prod WITH
    OWNER prod_user
    ENCODING 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;
```

#### 3. Production-Ready FastAPI Configuration

```python
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

# Configure structured logging for production
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

app = FastAPI(
    title="Todo API - Production",
    version="1.0.0",
    docs_url=None,  # Disable docs in production
    redoc_url=None,  # Disable redoc in production
)

# Production CORS configuration
allowed_hosts = os.getenv("ALLOWED_HOSTS", "").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_hosts,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    max_age=86400,  # Cache preflight requests for 1 day
)
```

#### 4. Production Next.js Configuration

**`full-stack-todo/next.config.ts`:**
```typescript
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'export', // For static export if deploying to CDN
  trailingSlash: true,
  reactStrictMode: true,
  swcMinify: true,
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: securityHeaders,
      },
    ];
  },
};

const securityHeaders = [
  {
    key: 'X-DNS-Prefetch-Control',
    value: 'on',
  },
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=63072000; includeSubDomains; preload',
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY',
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff',
  },
  {
    key: 'X-XSS-Protection',
    value: '1; mode=block',
  },
  {
    key: 'Referrer-Policy',
    value: 'origin-when-cross-origin',
  },
];

export default nextConfig;
```

## Configuration Management Strategies

### 1. Environment-Based Configuration

Create different configuration files for each environment:

```
config/
├── base.ts          # Base configuration shared across environments
├── development.ts   # Development-specific overrides
├── staging.ts      # Staging-specific overrides
└── production.ts   # Production-specific overrides
```

### 2. Configuration Validation

Implement configuration validation to catch issues early:

**Backend validation (`backend/config.py`):**
```python
from pydantic import BaseSettings, validator
import os

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    environment: str = "development"
    log_level: str = "INFO"

    @validator("secret_key")
    def secret_key_must_be_secure(cls, v, values):
        if values.get("environment") == "production":
            if len(v) < 32:
                raise ValueError("Secret key must be at least 32 characters in production")
        return v

    @validator("database_url")
    def database_url_must_be_set(cls, v):
        if not v:
            raise ValueError("DATABASE_URL environment variable is required")
        return v

settings = Settings()
```

**Frontend validation (`full-stack-todo/lib/config.ts`):**
```typescript
interface AppConfig {
  apiUrl: string;
  authUrl: string;
  environment: 'development' | 'staging' | 'production';
}

const validateConfig = (config: Partial<AppConfig>): AppConfig => {
  const validatedConfig = {
    apiUrl: config.apiUrl || process.env.NEXT_PUBLIC_API_URL,
    authUrl: config.authUrl || process.env.NEXT_PUBLIC_BETTER_AUTH_URL,
    environment: (config.environment || process.env.NODE_ENV || 'development') as any
  };

  if (!validatedConfig.apiUrl) {
    throw new Error('NEXT_PUBLIC_API_URL is required');
  }

  if (!validatedConfig.authUrl) {
    throw new Error('NEXT_PUBLIC_BETTER_AUTH_URL is required');
  }

  return validatedConfig;
};

export const appConfig = validateConfig({});
```

### 3. Secrets Management

For production deployments, use a secrets management system:

**AWS Secrets Manager:**
```python
import boto3
import json

def get_secret(secret_name, region_name="us-east-1"):
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])
```

**Environment Variable Precedence:**
1. Runtime environment variables
2. `.env` files
3. Default values in code

## Performance Configuration

### Database Optimization for Production

**Connection Pooling:**
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

def create_db_engine():
    return create_engine(
        settings.database_url,
        poolclass=QueuePool,
        pool_size=20,  # Adjust based on expected load
        max_overflow=30,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
```

**Database Indexes:**
```sql
-- Essential indexes for production performance
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
CREATE INDEX idx_users_email ON users(email);
```

### Caching Configuration

**Redis for session and cache management:**
```python
import redis
import os

redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=0,
    decode_responses=True
)
```

## Security Configuration

### HTTPS and SSL

Always use HTTPS in production:

**Nginx reverse proxy configuration:**
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Rate Limiting Configuration

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/tasks")
@limiter.limit("100 per hour")
async def get_tasks(request: Request):
    # API endpoint implementation
    pass
```

## Monitoring and Logging Configuration

### Structured Logging

```python
import structlog
from datetime import datetime

logger = structlog.get_logger()

def log_request(user_id: int, endpoint: str, status_code: int):
    logger.info(
        "request_processed",
        user_id=user_id,
        endpoint=endpoint,
        status_code=status_code,
        timestamp=datetime.utcnow().isoformat()
    )
```

### Health Checks

**Backend health check endpoint:**
```python
@app.get("/health")
async def health_check():
    # Check database connectivity
    try:
        db.execute("SELECT 1")
        db_status = "ok"
    except Exception:
        db_status = "error"

    return {
        "status": "healthy" if db_status == "ok" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": db_status,
            "api": "ok"
        }
    }
```

## Deployment Configuration

### CI/CD Pipeline Configuration

**GitHub Actions example (`/.github/workflows/deploy.yml`):**
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'pnpm'

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        cache: 'pip'

    - name: Install dependencies
      run: |
        cd full-stack-todo
        pnpm install

    - name: Build frontend
      run: |
        cd full-stack-todo
        pnpm build
      env:
        NEXT_PUBLIC_API_URL: ${{ secrets.PROD_API_URL }}

    - name: Deploy backend
      run: |
        # Deployment commands
      env:
        DATABASE_URL: ${{ secrets.DATABASE_URL }}
        SECRET_KEY: ${{ secrets.SECRET_KEY }}
```

This configuration guide provides comprehensive instructions for setting up the application in both development and production environments, ensuring security, performance, and maintainability.