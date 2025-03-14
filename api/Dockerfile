FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    postgresql-client \
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

# Create a database check script
RUN echo '#!/bin/sh\necho "Checking database permissions..."\nPGPASSWORD=${POSTGRES_PASSWORD} psql -h ${POSTGRES_HOST} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "\\dn" || echo "Could not list schemas - may need to check permissions"\nPGPASSWORD=${POSTGRES_PASSWORD} psql -h ${POSTGRES_HOST} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "SELECT current_user, current_database(), session_user, current_schema" || echo "Could not check current user/schema"' > /app/db_check.sh \
    && chmod +x /app/db_check.sh

# Create a migration script
RUN echo '#!/bin/sh\necho "Running database migrations..."\nalembic upgrade head || echo "Migration failed but continuing"' > /app/run_migrations.sh \
    && chmod +x /app/run_migrations.sh

# Create a startup script
RUN echo '#!/bin/sh\necho "Starting application on port ${PORT}..."\necho "Python version: $(python --version)"\necho "Current directory: $(pwd)"\nls -la\necho "Environment: ${ENVIRONMENT}"\necho "Cloud SQL Connection: ${CLOUD_SQL_CONNECTION_NAME}"\n\n# Check database permissions if host is available\nif [ -n "${POSTGRES_HOST}" ] && [ "${POSTGRES_HOST}" != "localhost" ]; then\n  echo "Checking database permissions..."\n  /app/db_check.sh\n  \n  echo "Running database migrations..."\n  /app/run_migrations.sh\nfi\n\necho "Starting uvicorn..."\nexec uvicorn main:app --host 0.0.0.0 --port ${PORT}' > /app/start.sh \
    && chmod +x /app/start.sh

# Command to run the application
CMD ["/app/start.sh"] 