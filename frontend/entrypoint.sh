#!/bin/sh
set -e

echo "Starting runtime configuration..."

# Create or replace config.json with runtime API URL
echo "{
  \"apiUrl\": \"${API_URL:-http://localhost:8000}\"
}" > /usr/share/nginx/html/assets/config.json

echo "Runtime configuration created:"
cat /usr/share/nginx/html/assets/config.json
echo ""
echo "Current API_URL value: ${API_URL:-http://localhost:8000}"
echo "Current ENVIRONMENT value: ${ENVIRONMENT:-development}"

# Start Nginx as the main process
echo "Starting Nginx..."
nginx -t
exec nginx -g 'daemon off;' 