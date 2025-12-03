# Multi-stage Dockerfile for the application
FROM python:3.11-slim as base

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY tests/ ./tests/

# Create logs directory
RUN mkdir -p logs

# Run tests by default
CMD ["python", "-m", "pytest", "tests/", "-v", "--tb=short"]
