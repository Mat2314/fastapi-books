# Build stage
FROM node:18 as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Runtime stage
FROM nginx:alpine
COPY --from=build /app/dist/fabooks/browser/ /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Add script to replace environment variables at runtime
WORKDIR /usr/share/nginx/html
COPY env.sh .
RUN chmod +x env.sh

# Create env.js file that will be populated at runtime
RUN echo "window.env = {};" > env.js

# Create a healthcheck file
RUN echo "OK" > health.txt

# Test nginx configuration during build
RUN nginx -t

# Use shell script as entrypoint with explicit logging and error handling
ENTRYPOINT ["/bin/sh", "-c", "echo 'Starting container on port 8080...' && ./env.sh && echo 'Starting Nginx...' && nginx -t && nginx -g 'daemon off;'"] 