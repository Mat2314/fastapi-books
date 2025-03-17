#!/bin/sh

# Recreate config file
echo "window.env = {" > env.js

# Add environment variables
echo "  API_URL: \"$API_URL\"," >> env.js
echo "  ENVIRONMENT: \"$ENVIRONMENT\"," >> env.js

# Close the object
echo "};" >> env.js

echo "Environment variables injected into env.js" 