FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Install pg8000 for Cloud SQL connectivity
RUN pip install --no-cache-dir pg8000

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
# Default port to 8080 for Cloud Run
ENV PORT=8080
# Set environment to production
ENV ENVIRONMENT=production
# Set Cloud SQL connection name - replace with your actual connection name
# Format: PROJECT_ID:REGION:INSTANCE_NAME
ENV CLOUD_SQL_CONNECTION_NAME="experiments-444412:us-central1:fabooks-db"

# Create a healthcheck script
RUN echo '#!/bin/sh\necho "Health check running..."\ncurl -f http://localhost:${PORT} || exit 1' > /app/healthcheck.sh \
    && chmod +x /app/healthcheck.sh

# Create a startup script
RUN echo '#!/bin/sh\necho "Starting application on port ${PORT}..."\necho "Python version: $(python --version)"\necho "Current directory: $(pwd)"\nls -la\necho "Environment: ${ENVIRONMENT}"\necho "Cloud SQL Connection: ${CLOUD_SQL_CONNECTION_NAME}"\necho "Starting uvicorn..."\nexec uvicorn main:app --host 0.0.0.0 --port ${PORT}' > /app/start.sh \
    && chmod +x /app/start.sh

# Command to run the application
CMD ["/app/start.sh"] 