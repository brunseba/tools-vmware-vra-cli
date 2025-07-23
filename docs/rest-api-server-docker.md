# REST API Server Docker Deployment Guide

This guide covers deploying the VMware vRA REST API Server using Docker and Docker Compose, including development, testing, and production scenarios.

## Table of Contents

- [Quick Start with Docker](#quick-start-with-docker)
- [Docker Compose Deployment](#docker-compose-deployment)
- [Available Services](#available-services)
- [Configuration](#configuration)
- [Environment Variables](#environment-variables)
- [Networking](#networking)
- [Monitoring and Logging](#monitoring-and-logging)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)

## Quick Start with Docker

### Building the Image

```bash
# Build the Docker image
docker build -t vmware-vra-cli .

# Or use the provided build script
./scripts/build.sh
```

### Running the Container

```bash
# Basic run
docker run -p 8000:8000 vmware-vra-cli

# Run with environment variables
docker run -p 8000:8000 \
  -e VRA_URL=https://vra.company.com \
  -e VRA_TENANT=company.local \
  vmware-vra-cli

# Run with volume mounts for configuration
docker run -p 8000:8000 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  vmware-vra-cli
```

## Docker Compose Deployment

### Basic Setup

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
# Edit .env with your configuration
```

Start the basic REST API server:

```bash
docker-compose up -d
```

### Development Setup

For development with additional tools and services:

```bash
# Start with development tools
docker-compose --profile tools --profile docs up -d

# This includes:
# - REST API Server
# - OpenAPI generator
# - Swagger UI
# - Log viewer (Dozzle)
```

### Full Setup with Monitoring

For a complete setup with monitoring and cache:

```bash
# Start all services
docker-compose --profile tools --profile docs --profile monitoring up -d

# This includes all development tools plus:
# - Redis cache
# - Enhanced monitoring capabilities
```

## Available Services

### Core Services

#### MCP Server (`vra-server`)
- **Port**: 8000
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs
- **Purpose**: Main API server

```yaml
services:
  vra-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - VRA_URL=${VRA_URL}
      - VRA_TENANT=${VRA_TENANT}
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Development Tools (`tools` profile)

#### OpenAPI Generator (`openapi-generator`)
- **Purpose**: Automatically generates OpenAPI specification
- **Output**: `./openapi.json`
- **Depends on**: vra-server health check

```yaml
openapi-generator:
  image: curlimages/curl:latest
  profiles: ["tools"]
  depends_on:
    vra-server:
      condition: service_healthy
  volumes:
    - ./:/output
  command: >
    sh -c "
      curl -o /output/openapi.json http://vra-server:8000/openapi.json &&
      echo 'OpenAPI spec generated successfully'
    "
```

#### Log Viewer (`log-viewer`)
- **Port**: 8080
- **URL**: http://localhost:8080
- **Purpose**: Web-based log viewing with Dozzle

```yaml
log-viewer:
  image: amir20/dozzle:latest
  profiles: ["tools"]
  ports:
    - "8080:8080"
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock:ro
  environment:
    - DOZZLE_LEVEL=info
    - DOZZLE_TAILSIZE=300
```

### Documentation (`docs` profile)

#### Swagger UI (`swagger-ui`)
- **Port**: 8081
- **URL**: http://localhost:8081
- **Purpose**: Interactive API documentation

```yaml
swagger-ui:
  image: swaggerapi/swagger-ui:latest
  profiles: ["docs"]
  ports:
    - "8081:8080"
  environment:
    - SWAGGER_JSON_URL=http://localhost:8000/openapi.json
  depends_on:
    - vra-server
```

### Monitoring (`monitoring` profile)

#### Redis Cache (`redis`)
- **Port**: 6379
- **Purpose**: Optional caching layer for improved performance

```yaml
redis:
  image: redis:7-alpine
  profiles: ["monitoring"]
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
  command: redis-server --appendonly yes
```

## Configuration

### Environment Variables

Create a `.env` file with your configuration:

```bash
# VMware vRA Configuration
VRA_URL=https://vra.company.com
VRA_TENANT=company.local
VRA_DOMAIN=vsphere.local
VRA_VERIFY_SSL=true
VRA_TIMEOUT=60

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
SERVER_WORKERS=1

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json

# Docker Compose Profiles
COMPOSE_PROFILES=tools,docs

# Optional: Redis Configuration (if using monitoring profile)
REDIS_URL=redis://redis:6379/0
CACHE_TTL=300
```

### Volume Mounts

The Docker setup supports several volume mounts:

```yaml
volumes:
  # Configuration files
  - ./config:/app/config
  
  # Log files
  - ./logs:/app/logs
  
  # Generated OpenAPI spec
  - ./:/output
  
  # Optional: Custom certificates
  - ./certs:/app/certs:ro
```

### Custom Configuration Files

You can provide custom configuration files:

```bash
# Create config directory
mkdir -p config

# Create custom configuration
cat > config/vra-config.json << EOF
{
  "api_url": "https://vra.company.com",
  "tenant": "company.local",
  "verify_ssl": true,
  "timeout": 60
}
EOF

# Mount the config directory
docker run -v $(pwd)/config:/app/config vmware-vra-cli
```

## Networking

### Port Mapping

| Service | Container Port | Host Port | Purpose |
|---------|---------------|-----------|---------|
| vra-server | 8000 | 8000 | Main API server |
| swagger-ui | 8080 | 8081 | API documentation |
| log-viewer | 8080 | 8080 | Log viewer |
| redis | 6379 | 6379 | Cache (optional) |

### Custom Networks

The Docker Compose setup creates a custom network:

```yaml
networks:
  vra-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

Services can communicate using service names:
- `http://vra-server:8000` - Main API server
- `redis://redis:6379` - Redis cache

## Monitoring and Logging

### Log Management

#### Structured Logging
The MCP server supports structured JSON logging:

```bash
# Enable JSON logging
docker run -e LOG_FORMAT=json vmware-vra-cli
```

#### Log Rotation
Docker Compose is configured with log rotation:

```yaml
services:
  vra-server:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

#### Accessing Logs

```bash
# View server logs
docker-compose logs -f vra-server

# View all service logs
docker-compose logs -f

# Use the web-based log viewer
open http://localhost:8080
```

### Health Checks

All services include health checks:

```bash
# Check service health
docker-compose ps

# Manual health check
curl http://localhost:8000/health
```

### Monitoring Endpoints

The MCP server exposes monitoring endpoints:

- `/health` - Health check
- `/metrics` - Application metrics (if enabled)
- `/docs` - API documentation
- `/openapi.json` - OpenAPI specification

## Production Deployment

### Production Docker Compose

Create a `docker-compose.prod.yml` file:

```yaml
version: '3.8'

services:
  vra-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - VRA_URL=${VRA_URL}
      - VRA_TENANT=${VRA_TENANT}
      - VRA_DOMAIN=${VRA_DOMAIN}
      - VRA_VERIFY_SSL=true
      - LOG_LEVEL=WARNING
      - SERVER_WORKERS=4
    volumes:
      - ./logs:/app/logs
      - ./config:/app/config:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "5"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - vra-server
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru

volumes:
  redis_data:

networks:
  default:
    driver: bridge
```

### Nginx Configuration

Create `nginx.conf` for reverse proxy:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream vra_server {
        server vra-server:8000;
    }

    server {
        listen 80;
        server_name vra-api.company.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name vra-api.company.com;

        ssl_certificate /etc/nginx/certs/server.crt;
        ssl_certificate_key /etc/nginx/certs/server.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        client_max_body_size 10M;

        location / {
            proxy_pass http://vra_server;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        location /health {
            proxy_pass http://vra_server/health;
            access_log off;
        }
    }
}
```

### Production Deployment Commands

```bash
# Deploy to production
docker-compose -f docker-compose.prod.yml up -d

# Scale the application
docker-compose -f docker-compose.prod.yml up -d --scale vra-server=3

# Update application
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Backup volumes
docker run --rm -v vra_redis_data:/data -v $(pwd):/backup alpine tar czf /backup/redis-backup.tar.gz -C /data .
```

### Production Security

1. **Use HTTPS**: Always enable SSL/TLS in production
2. **Environment Variables**: Use Docker secrets or external secret management
3. **Network Isolation**: Use custom networks and firewall rules
4. **Regular Updates**: Keep base images and dependencies updated
5. **Monitoring**: Implement comprehensive monitoring and alerting

```yaml
# Using Docker secrets
secrets:
  vra_password:
    external: true

services:
  vra-server:
    secrets:
      - vra_password
    environment:
      - VRA_PASSWORD_FILE=/run/secrets/vra_password
```

## Troubleshooting

### Common Issues

#### Server Won't Start

```bash
# Check logs
docker-compose logs vra-server

# Check container status
docker-compose ps

# Inspect container
docker inspect vra-server
```

#### Authentication Issues

```bash
# Test authentication manually
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test","url":"https://vra.company.com"}'

# Check environment variables
docker-compose exec vra-server env | grep VRA
```

#### Network Connectivity

```bash
# Test internal networking
docker-compose exec vra-server curl -f http://localhost:8000/health

# Test external connectivity
docker-compose exec vra-server curl -f https://vra.company.com
```

#### Performance Issues

```bash
# Check resource usage
docker stats

# Check application metrics
curl http://localhost:8000/metrics

# Scale services
docker-compose up -d --scale vra-server=2
```

### Debugging Commands

```bash
# Enter container shell
docker-compose exec vra-server /bin/bash

# View real-time logs
docker-compose logs -f --tail=100

# Check service dependencies
docker-compose config --services

# Validate compose file
docker-compose config

# Reset everything
docker-compose down -v
docker system prune -f
docker-compose up -d
```

### Log Analysis

```bash
# Search logs for errors
docker-compose logs vra-server 2>&1 | grep -i error

# Monitor authentication attempts
docker-compose logs vra-server 2>&1 | grep -i auth

# Check API requests
docker-compose logs vra-server 2>&1 | grep -E "(POST|GET|PUT|DELETE)"
```

## Best Practices

1. **Use Multi-stage Builds**: Optimize Docker image size
2. **Health Checks**: Always implement proper health checks
3. **Log Rotation**: Configure log rotation to prevent disk space issues
4. **Resource Limits**: Set appropriate CPU and memory limits
5. **Security**: Run containers as non-root users
6. **Backup**: Regularly backup persistent volumes
7. **Monitoring**: Implement comprehensive monitoring
8. **Updates**: Keep images and dependencies updated

This Docker deployment guide provides a complete solution for running the VMware vRA MCP Server in containerized environments, from development to production.
