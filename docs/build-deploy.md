# Building and Deploying vra-server

This guide covers all methods to build and deploy the VMware vRA MCP server.

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager (>= 0.8.0)
- Docker (for containerized deployment)
- Docker Compose (for orchestrated deployment)

### Basic Build

```bash
# Install dependencies
uv sync --extra dev

# Run the server directly
vra-server

# Or with uvicorn
uv run uvicorn vmware_vra_cli.app:app --reload
```

## 🏗️ Build Methods

> **Note**: This project uses the `uv_build` backend (uv >= 0.8.0), which provides native uv integration and improved build performance.

### 1. Python Package Build

Build a distributable Python package:

```bash
# Build wheel and source distribution
uv build

# Install the built package
pip install dist/vmware_vra_cli-*.whl

# Run server
vra-server
```

### 2. Docker Build

Build a containerized version:

```bash
# Build Docker image
docker build -t vmware-vra-cli:latest .

# Run container
docker run -p 8000:8000 vmware-vra-cli:latest

# With environment variables
docker run -p 8000:8000 \
  -e VRA_URL=https://vra.company.com \
  -e VRA_TENANT=vsphere.local \
  vmware-vra-cli:latest
```

### 3. Docker Compose Build

For development and production deployments:

```bash
# Copy environment template
cp .env.example .env

# Edit your configuration
vim .env

# Build and start
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### 4. Automated Build Script

Use the provided build script for all options:

```bash
# Build everything (wheel + docker)
./scripts/build.sh

# Build only Python wheel
./scripts/build.sh -t wheel

# Build only Docker image
./scripts/build.sh -t docker

# Build and start with docker-compose
./scripts/build.sh -t compose

# Build with custom version
./scripts/build.sh -t docker -v 1.0.0

# Show help
./scripts/build.sh -h
```

## 🎯 Deployment Options

### Development Deployment

```bash
# Direct Python execution
uv run uvicorn vmware_vra_cli.app:app --reload --host 0.0.0.0 --port 8000

# Or use the CLI command
uv run vra-server
```

### Production Deployment

#### Option 1: Direct Python Deployment

```bash
# Install production dependencies
pip install vmware-vra-cli

# Run with production settings
uvicorn vmware_vra_cli.app:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --access-log
```

#### Option 2: Docker Deployment

```bash
# Single container
docker run -d \
  --name vra-server \
  -p 8000:8000 \
  -e VRA_URL=https://vra.company.com \
  -e VRA_TENANT=vsphere.local \
  -v vra-config:/home/appuser/.config/vmware-vra-cli \
  --restart unless-stopped \
  vmware-vra-cli:latest
```

#### Option 3: Docker Compose Deployment

```yaml
# Production docker-compose.yml
version: '3.8'

services:
  vra-server:
    image: vmware-vra-cli:latest
    ports:
      - "8000:8000"
    environment:
      - VRA_URL=${VRA_URL}
      - VRA_TENANT=${VRA_TENANT}
      - UVICORN_WORKERS=4
    volumes:
      - vra-config:/home/appuser/.config/vmware-vra-cli
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  vra-config:
```

### Kubernetes Deployment

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vra-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: vra-server
  template:
    metadata:
      labels:
        app: vra-server
    spec:
      containers:
      - name: vra-server
        image: vmware-vra-cli:latest
        ports:
        - containerPort: 8000
        env:
        - name: VRA_URL
          value: "https://vra.company.com"
        - name: VRA_TENANT
          value: "vsphere.local"
        - name: UVICORN_WORKERS
          value: "1"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: vra-server-service
spec:
  selector:
    app: vra-server
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VRA_URL` | - | VMware vRA server URL |
| `VRA_TENANT` | - | VMware vRA tenant |
| `VRA_DOMAIN` | - | VMware vRA domain (optional) |
| `VRA_VERIFY_SSL` | `true` | Enable SSL verification |
| `UVICORN_HOST` | `0.0.0.0` | Server bind address |
| `UVICORN_PORT` | `8000` | Server port |
| `UVICORN_WORKERS` | `1` | Number of worker processes |
| `UVICORN_LOG_LEVEL` | `info` | Log level |
| `LOG_LEVEL` | `INFO` | Application log level |

### Configuration Files

Create `~/.config/vmware-vra-cli/config.yaml`:

```yaml
server:
  url: "https://vra.company.com"
  tenant: "vsphere.local"
  verify_ssl: true

defaults:
  project: "Development"
  output_format: "json"

logging:
  level: "INFO"
```

## 🧪 Testing Builds

### Test Python Package

```bash
# Install in editable mode
pip install -e .

# Run tests
pytest tests/test_server.py -v

# Test CLI
vra-server &
curl http://localhost:8000/health
```

### Test Docker Image

```bash
# Build and test
docker build -t test-vra-server .
docker run -d -p 8000:8000 --name test-server test-vra-server

# Health check
sleep 10
curl http://localhost:8000/health

# Cleanup
docker stop test-server
docker rm test-server
```

### Test Docker Compose

```bash
# Start services
docker-compose up -d

# Wait for health check
docker-compose ps

# Test endpoints
curl http://localhost:8000/
curl http://localhost:8000/health

# Cleanup
docker-compose down
```

## 📊 Performance Tuning

### Production Settings

```bash
# Recommended production command
uvicorn vmware_vra_cli.app:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --access-log \
  --log-level info
```

### Docker Resource Limits

```yaml
# docker-compose.yml with resource limits
services:
  vra-server:
    # ... other config ...
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

## 🔒 Security Considerations

### SSL/TLS

```bash
# Run behind reverse proxy (nginx, traefik, etc.)
# Or with SSL termination at load balancer level

# For development with self-signed certs
uvicorn vmware_vra_cli.app:app \
  --host 0.0.0.0 \
  --port 8000 \
  --ssl-keyfile private.key \
  --ssl-certfile certificate.crt
```

### CORS Configuration

Update `src/vmware_vra_cli/app.py` for production CORS settings:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],  # Specify allowed origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## 🚀 CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/build-and-deploy.yml
name: Build and Deploy

on:
  push:
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.10'
    
    - name: Install uv
      run: pip install uv
    
    - name: Build package
      run: |
        uv sync --extra dev
        uv run pytest
        uv build
    
    - name: Build Docker image
      run: |
        docker build -t vmware-vra-cli:${{ github.ref_name }} .
        docker tag vmware-vra-cli:${{ github.ref_name }} vmware-vra-cli:latest
    
    - name: Push to registry
      # Add your registry push commands here
      run: echo "Push to your container registry"
```

## 📈 Monitoring and Logging

### Health Checks

The server includes built-in health checks at `/health`:

```bash
curl http://localhost:8000/health
```

### Logging

Configure structured logging in production:

```python
import logging
import structlog

# Add to app startup
logging.basicConfig(level=logging.INFO)
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**: Change port with `--port 8001`
2. **Permission denied**: Run as non-root user in containers
3. **SSL verification errors**: Set `VRA_VERIFY_SSL=false` for development
4. **Memory issues**: Increase container memory limits
5. **Slow startup**: Check health endpoint after 30-60 seconds

### Debug Mode

```bash
# Enable debug mode
export UVICORN_LOG_LEVEL=debug
export LOG_LEVEL=DEBUG
vra-server
```

### Container Debugging

```bash
# Enter running container
docker exec -it container_name bash

# Check logs
docker logs container_name -f

# Check health
docker inspect container_name | grep Health
```
