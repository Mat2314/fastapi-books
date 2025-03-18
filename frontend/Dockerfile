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

# Add entrypoint script to handle runtime configuration
WORKDIR /usr/share/nginx/html
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create a healthcheck file
RUN echo "OK" > health.txt

# Test nginx configuration during build
RUN nginx -t

# Use entrypoint script
ENTRYPOINT ["/entrypoint.sh"] 