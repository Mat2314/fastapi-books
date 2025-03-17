# Build stage
FROM node:18 as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build --prod

# Runtime stage
FROM nginx:alpine
COPY --from=build /app/dist/* /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Add script to replace environment variables at runtime
WORKDIR /usr/share/nginx/html
COPY env.sh .
RUN chmod +x env.sh

# Create env.js file that will be populated at runtime
RUN echo "window.env = {};" > env.js

# Use shell script as entrypoint
ENTRYPOINT ["/bin/sh", "-c", "./env.sh && nginx -g 'daemon off;'"] 