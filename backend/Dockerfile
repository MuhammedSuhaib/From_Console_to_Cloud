FROM python:3.10-slim

# 1. Install uv efficiently from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 2. Set working directory
WORKDIR /app

# 3. Copy requirements first for better caching
COPY requirements.txt .

# 4. Install dependencies into the system environment
# This is where the fix is: added --system
RUN uv pip install --system -r requirements.txt

# 5. Copy the rest of the backend code
COPY . .

# 6. Set environment variables
ENV PORT=7860
ENV PYTHONUNBUFFERED=1

# 7. Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]