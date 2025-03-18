#!/bin/sh
set -e

echo "Starting environment variable injection..."

# Recreate config file
echo "window.env = {" > env.js

# Add environment variables with defaults
echo "  API_URL: \"${API_URL:-http://localhost:8000}\"," >> env.js
echo "  ENVIRONMENT: \"${ENVIRONMENT:-development}\"," >> env.js

# Close the object
echo "};" >> env.js

echo "Environment variables injected into env.js:"
cat env.js
echo ""
echo "Current API_URL value: ${API_URL:-http://localhost:8000}"
echo "Current ENVIRONMENT value: ${ENVIRONMENT:-development}" 