# Environment Variable Configuration Guide

This guide explains all environment variables required for the Full-Stack Todo Application, including their purpose, format, and configuration for different environments.

## Overview

The application uses environment variables to configure different aspects of the system including database connections, authentication, and API endpoints. These variables are loaded differently in the frontend and backend.

## Frontend Environment Variables

Located in `full-stack-todo/.env` (and `.env.local` for local development).

### Required Variables

#### NEXT_PUBLIC_API_URL
- **Description**: The URL of the backend API server
- **Format**: `http://host:port` or `https://domain`
- **Default (Development)**: `http://localhost:8000`
- **Default (Production)**: `https://your-backend-domain.com`
- **Example**:
  ```
  NEXT_PUBLIC_API_URL=http://localhost:8000
  ```

#### NEXT_PUBLIC_BETTER_AUTH_URL
- **Description**: The URL where Better Auth is accessible
- **Format**: `http://host:port` or `https://domain`
- **Default (Development)**: `http://localhost:3000`
- **Default (Production)**: `https://your-frontend-domain.com`
- **Example**:
  ```
  NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
  ```

### Optional Variables

#### NEXT_PUBLIC_APP_NAME
- **Description**: Name of the application displayed in the UI
- **Default**: `Todo App`
- **Example**:
  ```
  NEXT_PUBLIC_APP_NAME=My Todo Manager
  ```

#### NEXT_PUBLIC_DEBUG_MODE
- **Description**: Enable debug logging and additional information
- **Values**: `true` or `false`
- **Default**: `false`
- **Example**:
  ```
  NEXT_PUBLIC_DEBUG_MODE=true
  ```

## Backend Environment Variables

Located in `backend/.env`.

### Required Variables

#### DATABASE_URL
- **Description**: Connection string for the PostgreSQL database
- **Format**: `postgresql://username:password@host:port/database`
- **Example**:
  ```
  DATABASE_URL=postgresql://myuser:mypassword@localhost:5432/todo_app
  ```

#### SECRET_KEY
- **Description**: Secret key used for signing JWT tokens and encrypting data
- **Format**: Random string of at least 32 characters
- **Generation**: Use a cryptographically secure random generator
- **Example**:
  ```
  SECRET_KEY=verylongrandomstringwithatleast32characters
  ```

#### ALGORITHM
- **Description**: Algorithm used for JWT token encoding
- **Default**: `HS256`
- **Example**:
  ```
  ALGORITHM=HS256
  ```

#### ACCESS_TOKEN_EXPIRE_MINUTES
- **Description**: Number of minutes before JWT tokens expire
- **Default**: `1440` (24 hours)
- **Example**:
  ```
  ACCESS_TOKEN_EXPIRE_MINUTES=1440
  ```

### Neon-specific Variables

#### NEON_DATABASE_URL
- **Description**: Connection string for Neon Serverless PostgreSQL database
- **Format**: `postgresql://username:password@endpoint.neon.tech/dbname`
- **Example**:
  ```
  NEON_DATABASE_URL=postgresql://myuser:mypassword@ep-cool-mountain-123456.us-east-1.aws.neon.tech/mydb
  ```

### Optional Variables

#### ENVIRONMENT
- **Description**: Current environment (affects logging and behavior)
- **Values**: `development`, `staging`, `production`
- **Default**: `development`
- **Example**:
  ```
  ENVIRONMENT=production
  ```

#### LOG_LEVEL
- **Description**: Minimum log level to output
- **Values**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Default**: `INFO`
- **Example**:
  ```
  LOG_LEVEL=DEBUG
  ```

#### MAX_TASKS_PER_USER
- **Description**: Maximum number of tasks allowed per user (0 for unlimited)
- **Default**: `0`
- **Example**:
  ```
  MAX_TASKS_PER_USER=100
  ```

#### RATE_LIMIT_REQUESTS
- **Description**: Number of requests allowed per minute per IP
- **Default**: `100`
- **Example**:
  ```
  RATE_LIMIT_REQUESTS=50
  ```

#### RATE_LIMIT_WINDOW
- **Description**: Time window in seconds for rate limiting
- **Default**: `60`
- **Example**:
  ```
  RATE_LIMIT_WINDOW=60
  ```

## Environment-Specific Configuration

### Development Environment

Create `.env` files in both frontend and backend directories:

**Frontend** (`full-stack-todo/.env`):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_DEBUG_MODE=true
```

**Backend** (`backend/.env`):
```
DATABASE_URL=postgresql://localhost:5432/todo_dev
SECRET_KEY=dev_secret_key_that_should_be_long_and_random_for_development
NEON_DATABASE_URL=
ENVIRONMENT=development
LOG_LEVEL=DEBUG
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### Staging Environment

**Frontend** (`full-stack-todo/.env.staging`):
```
NEXT_PUBLIC_API_URL=https://staging-api.yourapp.com
NEXT_PUBLIC_BETTER_AUTH_URL=https://staging.yourapp.com
NEXT_PUBLIC_DEBUG_MODE=false
```

**Backend** (`backend/.env.staging`):
```
DATABASE_URL=postgresql://staging-db-url
SECRET_KEY=staging_secret_key_here
NEON_DATABASE_URL=your_neon_staging_url
ENVIRONMENT=staging
LOG_LEVEL=INFO
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### Production Environment

**Frontend** (`full-stack-todo/.env.production`):
```
NEXT_PUBLIC_API_URL=https://api.yourapp.com
NEXT_PUBLIC_BETTER_AUTH_URL=https://yourapp.com
NEXT_PUBLIC_DEBUG_MODE=false
```

**Backend** (`backend/.env.production`):
```
DATABASE_URL=postgresql://prod-db-url
SECRET_KEY=production_secret_key_that_should_be_very_secure
NEON_DATABASE_URL=your_neon_production_url
ENVIRONMENT=production
LOG_LEVEL=WARNING
ACCESS_TOKEN_EXPIRE_MINUTES=1440
RATE_LIMIT_REQUESTS=100
MAX_TASKS_PER_USER=0
```

## Generating Secure Values

### Secret Key Generation

Generate a secure secret key using one of these methods:

**Using Python:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Using OpenSSL:**
```bash
openssl rand -base64 32
```

**Using Node.js:**
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

### Neon Database URL

1. Log in to your Neon console
2. Select your project
3. Go to the "Connection Details" section
4. Copy the connection string for your region
5. Replace `<password>` with your actual database password

## Docker Environment Configuration

When using Docker, environment variables can be configured in `docker-compose.yml`:

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=${ENVIRONMENT:-development}
    env_file:
      - ./backend/.env
    ports:
      - "8000:8000"
    depends_on:
      - db

  frontend:
    build: ./full-stack-todo
    environment:
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
      - NEXT_PUBLIC_BETTER_AUTH_URL=${NEXT_PUBLIC_BETTER_AUTH_URL}
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

## Best Practices

### Security

1. **Never commit** `.env` files to version control
2. Use `.gitignore` to exclude environment files
3. Generate strong, random values for secret keys
4. Rotate secrets regularly in production
5. Use different secrets for different environments
6. Restrict access to production environment files

### Management

1. Use a secrets management system in production (AWS Secrets Manager, Azure Key Vault, etc.)
2. Implement environment-specific configurations
3. Document all environment variables and their purposes
4. Use validation to ensure required variables are set
5. Set reasonable defaults for optional variables

### Validation

The application validates required environment variables at startup:

```python
# backend/main.py
def validate_env_vars():
    required_vars = ['DATABASE_URL', 'SECRET_KEY']
    for var in required_vars:
        if not os.getenv(var):
            raise ValueError(f"Required environment variable {var} is not set")
```

## Troubleshooting

### Common Issues

#### "Database connection failed"
- Check that `DATABASE_URL` is correctly formatted
- Verify database server is running and accessible
- Ensure credentials in the connection string are correct

#### "Invalid token" errors
- Verify `SECRET_KEY` matches between frontend and backend
- Check that tokens haven't expired
- Ensure the same algorithm is used for token generation and verification

#### "Environment variable not found"
- Confirm the variable is set in the correct `.env` file
- Check that environment files are loaded properly
- Verify variable names match exactly (case-sensitive)

#### "Permission denied" to database
- Verify database user has appropriate permissions
- Check that the database exists
- Ensure the connection string includes the correct database name

## Loading Environment Variables

### Frontend (Next.js)

Environment variables are loaded automatically by Next.js. Only variables prefixed with `NEXT_PUBLIC_` are available in the browser.

### Backend (FastAPI)

Environment variables are loaded using the `python-dotenv` package:

```python
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file
```

## Setting Up Environment Files

### Quick Setup Script

Create a script to initialize environment files:

**setup-env.sh:**
```bash
#!/bin/bash

# Create frontend .env if it doesn't exist
if [ ! -f "full-stack-todo/.env" ]; then
    echo "Creating frontend .env file..."
    cat > full-stack-todo/.env << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
EOF
fi

# Create backend .env if it doesn't exist
if [ ! -f "backend/.env" ]; then
    echo "Creating backend .env file..."
    SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
    cat > backend/.env << EOF
DATABASE_URL=postgresql://localhost:5432/todo_dev
SECRET_KEY=$SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ENVIRONMENT=development
LOG_LEVEL=DEBUG
NEON_DATABASE_URL=
EOF
fi

echo "Environment files created successfully!"
echo "Please update the values according to your setup."
```

This script creates initial environment files with secure random values for secrets.