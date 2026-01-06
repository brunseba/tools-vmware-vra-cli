# Multi-stage build for efficient Docker image
FROM node:18-alpine AS build

# Add metadata using OpenContainer labels
LABEL org.opencontainers.image.title="VMware vRA Web UI"
LABEL org.opencontainers.image.description="Frontend web application for VMware vRealize Automation management"
LABEL org.opencontainers.image.vendor="VMware vRA CLI Team"
LABEL org.opencontainers.image.authors="VMware vRA CLI Team"
LABEL org.opencontainers.image.source="https://github.com/your-org/tools-vmware-vra-cli"
LABEL org.opencontainers.image.documentation="https://github.com/your-org/tools-vmware-vra-cli/blob/main/README.md"

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies
RUN npm install --prefer-offline --no-audit --no-fund && npm cache clean --force

# Copy config files
COPY tsconfig.json ./
COPY tsconfig.node.json ./
COPY tsconfig.prod.json ./
COPY vite.config.ts ./

# Copy source code
COPY src/ ./src/
COPY public/ ./public/
COPY index.html ./

# Build the application
RUN npm run build

# Development stage for hot reload (airgap-compatible)
FROM node:18-alpine AS development

# Add OpenContainer labels for development image
LABEL org.opencontainers.image.title="VMware vRA Web UI - Development"
LABEL org.opencontainers.image.description="Development environment for VMware vRealize Automation frontend (airgap-compatible)"
LABEL org.opencontainers.image.vendor="VMware vRA CLI Team"

# Install system dependencies for airgap environment
RUN apk add --no-cache wget

# Set working directory and configure Node.js for Docker
WORKDIR /app

# Configure Node.js environment for Docker containers
ENV NODE_OPTIONS="--max-old-space-size=2048" \
    CHOKIDAR_USEPOLLING=true \
    CHOKIDAR_INTERVAL=1000

# Copy and install dependencies (for airgap compatibility)
COPY package.json ./
RUN npm install --prefer-offline --no-audit --no-fund

# Copy configuration files
COPY tsconfig.json ./
COPY tsconfig.node.json ./
COPY vite.config.ts ./
COPY index.html ./

# Copy source code (will be overridden by volume mounts in development)
COPY src/ ./src/
COPY public/ ./public/

# Expose Vite dev server port
EXPOSE 5173

# Health check for development server
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:5173/ || exit 1

# Start development server (dependencies already installed)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Production stage with nginx
FROM nginx:alpine AS production

# Add OpenContainer labels for production image
LABEL org.opencontainers.image.title="VMware vRA Web UI - Production"
LABEL org.opencontainers.image.description="Production-ready frontend for VMware vRealize Automation management"
LABEL org.opencontainers.image.vendor="VMware vRA CLI Team"

# Install security updates
RUN apk update && apk upgrade && apk add --no-cache dumb-init

# Remove default nginx config
RUN rm -rf /usr/share/nginx/html/*

# Copy built application
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create nginx user for security
RUN adduser -D -s /bin/false nginx-user

# Set proper ownership
RUN chown -R nginx-user:nginx-user /usr/share/nginx/html
RUN chown -R nginx-user:nginx-user /var/cache/nginx
RUN chown -R nginx-user:nginx-user /var/log/nginx

# Create runtime directories
RUN mkdir -p /var/run/nginx && chown nginx-user:nginx-user /var/run/nginx

# Switch to non-root user
USER nginx-user

# Expose port
EXPOSE 8080

# Create a simple health check endpoint
RUN echo '<!DOCTYPE html><html><body>OK</body></html>' > /usr/share/nginx/html/health

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# Use dumb-init as entrypoint for proper signal handling
ENTRYPOINT ["dumb-init", "--"]

# Start nginx
CMD ["nginx", "-g", "daemon off;"]