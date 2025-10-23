# VMware vRA Web UI - Deployment Guide

This document provides comprehensive instructions for deploying the VMware vRA Web UI application in different environments.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   Frontend      │────│   Backend       │────│   VMware vRA    │
│   (React/Vite)  │    │   (Node.js)     │    │   API           │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       
         │                       │                       
    ┌─────────┐            ┌─────────┐                  
    │         │            │         │                  
    │  Nginx  │            │  Redis  │                  
    │         │            │         │                  
    └─────────┘            └─────────┘                  
```

## Prerequisites

- Docker Engine 20.10+ and Docker Compose 2.0+
- Node.js 18+ (for local development)
- VMware vRA instance with API access
- OIDC provider (optional, for SSO)

## Quick Start

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd tools-vmware-vra-cli
   cp .env.example .env
   ```

2. **Configure Environment**
   Edit `.env` file with your VMware vRA configuration:
   ```bash
   VRA_API_URL=https://your-vra-instance.com
   VRA_API_TOKEN=your_api_token
   VRA_TENANT=your_tenant
   ```

3. **Start Development Environment**
   ```bash
   docker-compose up -d backend frontend redis
   ```

4. **Access the Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:3000
   - Redis: localhost:6379

## Deployment Environments

### Development

For local development with hot reloading:

```bash
# Start all development services
docker-compose up -d

# View logs
docker-compose logs -f frontend backend

# Stop services
docker-compose down
```

**Development URLs:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:3000
- Log Viewer: http://localhost:8081 (with `--profile monitoring`)

### Production

For production deployment with Nginx reverse proxy:

```bash
# Build production images
docker-compose -f docker-compose.yml --profile production build

# Start production services
docker-compose --profile production up -d

# Monitor services
docker-compose --profile production ps
```

**Production URLs:**
- Application: http://localhost:8080
- Health Check: http://localhost:8080/health

## Configuration

### Environment Variables

#### VMware vRA Configuration
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `VRA_API_URL` | VMware vRA API endpoint | Yes | - |
| `VRA_API_TOKEN` | API authentication token | Yes | - |
| `VRA_TENANT` | vRA tenant name | Yes | - |
| `VRA_DOMAIN` | vRA domain (if applicable) | No | - |
| `VRA_VERIFY_SSL` | Verify SSL certificates | No | `true` |

#### Security Configuration
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `JWT_SECRET` | JWT signing secret (32+ chars) | Yes | - |
| `SESSION_SECRET` | Session encryption secret | Yes | - |

#### OIDC Configuration (Optional)
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OIDC_ISSUER_URL` | OIDC provider URL | No | - |
| `OIDC_CLIENT_ID` | OIDC client ID | No | - |
| `OIDC_CLIENT_SECRET` | OIDC client secret | No | - |

### Docker Compose Profiles

Use profiles to control which services are started:

```bash
# Development (default)
docker-compose up -d

# Production with reverse proxy
docker-compose --profile production up -d

# With monitoring and logs
docker-compose --profile monitoring up -d

# Tools for debugging
docker-compose --profile tools run tools sh
```

## Security

### Network Security
- All services communicate over a private Docker network
- Nginx acts as a reverse proxy with security headers
- Rate limiting configured for API endpoints

### Authentication
- JWT-based authentication with configurable secrets
- Optional OIDC integration for SSO
- Session management with Redis

### Container Security
- Non-root user execution in containers
- Multi-stage builds for minimal attack surface
- Security updates applied in base images
- OpenContainer labels for metadata

## Monitoring and Logging

### Health Checks
- Backend: `GET /health`
- Frontend: `GET /health` (via Nginx)
- Redis: Built-in health check

### Log Aggregation
Optional Dozzle log viewer for centralized logging:

```bash
docker-compose --profile monitoring up -d log-viewer
```

Access at: http://localhost:8081

### Metrics
The application supports metrics collection:

```bash
# Enable metrics in environment
ENABLE_METRICS=true
METRICS_PORT=9090
```

## Backup and Recovery

### Data Backup
```bash
# Backup Redis data
docker-compose exec redis redis-cli BGSAVE

# Export volume data
docker run --rm -v vra-redis-data:/data -v $(pwd):/backup alpine tar czf /backup/redis-backup.tar.gz -C /data .
```

### Configuration Backup
```bash
# Backup configuration
tar czf config-backup.tar.gz .env docker-compose.yml frontend/nginx.conf
```

## Troubleshooting

### Common Issues

**Frontend not loading:**
```bash
# Check if services are running
docker-compose ps

# Check frontend logs
docker-compose logs frontend

# Verify environment variables
docker-compose exec frontend printenv | grep VITE_
```

**Backend API errors:**
```bash
# Check backend logs
docker-compose logs backend

# Verify vRA connectivity
docker-compose exec backend curl -k $VRA_API_URL/health

# Check Redis connection
docker-compose exec backend node -e "console.log(require('redis').createClient(process.env.REDIS_URL))"
```

**Permission denied errors:**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Rebuild with --no-cache
docker-compose build --no-cache
```

### Debug Mode

Enable debug logging:

```bash
# Set debug environment
LOG_LEVEL=debug

# View detailed logs
docker-compose logs -f --tail=100 backend
```

## Performance Optimization

### Production Optimizations
- Enable gzip compression in Nginx
- Configure appropriate cache headers
- Use Redis for session storage and caching
- Optimize bundle size with tree shaking

### Resource Limits
Configure resource limits in docker-compose.override.yml:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
  
  frontend:
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.25'
```

## Security Hardening

### Production Security Checklist
- [ ] Change all default passwords and secrets
- [ ] Enable SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Enable audit logging
- [ ] Regular security updates
- [ ] Implement backup strategy
- [ ] Monitor for security alerts

### SSL/TLS Configuration
For production with SSL:

1. Obtain SSL certificates
2. Update nginx.conf with SSL configuration
3. Set environment variables:
   ```bash
   SSL_CERT_PATH=/etc/ssl/certs/app.crt
   SSL_KEY_PATH=/etc/ssl/private/app.key
   ```

## Scaling

### Horizontal Scaling
Scale backend instances:

```bash
docker-compose up -d --scale backend=3
```

### Load Balancing
Configure Nginx upstream for load balancing:

```nginx
upstream backend {
    server backend_1:3000;
    server backend_2:3000;
    server backend_3:3000;
}
```

## Support

For deployment issues:
1. Check this deployment guide
2. Review application logs
3. Verify environment configuration
4. Check Docker and container status
5. Consult the main README.md for development setup

## Updates

### Application Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose build --no-cache
docker-compose up -d
```

### Security Updates
```bash
# Update base images
docker-compose pull
docker-compose build --pull --no-cache
docker-compose up -d
```