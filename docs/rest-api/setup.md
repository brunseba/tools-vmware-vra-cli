# REST API Server Setup

This guide walks you through setting up the VMware vRA REST API server for HTTP-based integrations.

## Quick Start

### Basic Server Setup

```bash
# Install the CLI tools (includes REST server)
pipx install vmware-vra-cli

# Start the REST API server
vra-rest-server

# Server will be available at:
# - API: http://localhost:8000
# - Documentation: http://localhost:8000/docs
# - OpenAPI spec: http://localhost:8000/openapi.json
```

### Docker Deployment

```bash
# Pull the Docker image
docker pull vmware-vra-cli:latest

# Run with basic configuration
docker run -d \
  --name vra-rest-server \
  -p 8000:8000 \
  -v ~/.vra-cli:/root/.vra-cli \
  vmware-vra-cli:latest \
  vra-rest-server

# Run with environment variables
docker run -d \
  --name vra-rest-server \
  -p 8000:8000 \
  -e VRA_URL="https://vra.company.com" \
  -e VRA_LOG_LEVEL="INFO" \
  vmware-vra-cli:latest \
  vra-rest-server
```

## Configuration

### Environment Variables

Configure the server using environment variables:

```bash
# vRA Connection
export VRA_URL="https://vra.company.com"
export VRA_TENANT="corp.local" 
export VRA_DOMAIN="vsphere.local"

# Server Configuration
export VRA_REST_HOST="0.0.0.0"
export VRA_REST_PORT="8000"
export VRA_REST_WORKERS="4"

# Security
export VRA_REST_SSL_CERT="/path/to/cert.pem"
export VRA_REST_SSL_KEY="/path/to/key.pem"

# Logging
export VRA_LOG_LEVEL="INFO"
export VRA_LOG_FILE="/var/log/vra-rest-server.log"

# Features
export VRA_REST_ENABLE_CORS="true"
export VRA_REST_ENABLE_METRICS="true"
```

### Configuration File

Create a configuration file at `~/.vra-cli/config.json`:

```json
{
  "vra_url": "https://vra.company.com",
  "tenant": "corp.local",
  "domain": "vsphere.local",
  "rest_server": {
    "host": "0.0.0.0",
    "port": 8000,
    "workers": 4,
    "reload": false,
    "access_log": true,
    "ssl": {
      "enabled": false,
      "cert_file": "/path/to/cert.pem",
      "key_file": "/path/to/key.pem"
    },
    "cors": {
      "enabled": true,
      "allow_origins": ["*"],
      "allow_methods": ["GET", "POST", "PUT", "DELETE"],
      "allow_headers": ["*"]
    },
    "rate_limiting": {
      "enabled": true,
      "requests_per_minute": 100,
      "burst_size": 20
    }
  }
}
```

## Command Line Options

Start the server with custom options:

```bash
# Basic server with custom port
vra-rest-server --port 8080

# Production server with SSL
vra-rest-server \
  --host 0.0.0.0 \
  --port 443 \
  --ssl-cert /etc/ssl/certs/vra-api.pem \
  --ssl-key /etc/ssl/private/vra-api.key \
  --workers 8

# Development server with auto-reload
vra-rest-server --reload --log-level debug

# Server with custom configuration
vra-rest-server --config /etc/vra-cli/config.json
```

### Available Options

```
--host TEXT          Host to bind to [default: 127.0.0.1]
--port INTEGER       Port to bind to [default: 8000]
--workers INTEGER    Number of worker processes [default: 1]
--reload             Enable auto-reload for development
--log-level TEXT     Logging level [default: info]
--config TEXT        Path to configuration file
--ssl-cert TEXT      SSL certificate file
--ssl-key TEXT       SSL private key file
--access-log         Enable access logging
--no-docs           Disable OpenAPI documentation
```

## Authentication Setup

The REST API server requires vRA authentication:

### Method 1: Pre-authenticate

```bash
# Authenticate using the CLI first
vra auth login --username admin --url https://vra.company.com

# Start server (will use stored credentials)
vra-rest-server
```

### Method 2: Environment Variables

```bash
# Set authentication via environment
export VRA_USERNAME="admin@corp.local"
export VRA_PASSWORD="your-password"
export VRA_URL="https://vra.company.com"

# Server will authenticate on startup
vra-rest-server
```

### Method 3: API Authentication

Use the `/auth/login` endpoint after starting the server:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin@corp.local",
    "password": "your-password", 
    "url": "https://vra.company.com"
  }'
```

## Production Deployment

### Systemd Service

Create `/etc/systemd/system/vra-rest-server.service`:

```ini
[Unit]
Description=VMware vRA REST API Server
After=network.target

[Service]
Type=exec
User=vra-api
Group=vra-api
WorkingDirectory=/opt/vra-cli
ExecStart=/usr/local/bin/vra-rest-server \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --config /etc/vra-cli/config.json
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable vra-rest-server
sudo systemctl start vra-rest-server
sudo systemctl status vra-rest-server
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  vra-rest-server:
    image: vmware-vra-cli:latest
    container_name: vra-rest-server
    command: vra-rest-server --host 0.0.0.0 --workers 4
    ports:
      - "8000:8000"
    environment:
      - VRA_URL=https://vra.company.com
      - VRA_TENANT=corp.local
      - VRA_LOG_LEVEL=INFO
    volumes:
      - ./config:/root/.vra-cli
      - ./logs:/var/log
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Optional: Reverse proxy with SSL
  nginx:
    image: nginx:alpine
    container_name: vra-nginx
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - vra-rest-server
    restart: unless-stopped

  # Optional: Monitoring
  prometheus:
    image: prom/prometheus
    container_name: vra-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    restart: unless-stopped
```

### Kubernetes Deployment

Create `k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vra-rest-server
  labels:
    app: vra-rest-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: vra-rest-server
  template:
    metadata:
      labels:
        app: vra-rest-server
    spec:
      containers:
      - name: vra-rest-server
        image: vmware-vra-cli:latest
        command: ["vra-rest-server"]
        args: ["--host", "0.0.0.0", "--workers", "2"]
        ports:
        - containerPort: 8000
        env:
        - name: VRA_URL
          value: "https://vra.company.com"
        - name: VRA_TENANT
          value: "corp.local"
        - name: VRA_LOG_LEVEL
          value: "INFO"
        - name: VRA_USERNAME
          valueFrom:
            secretKeyRef:
              name: vra-credentials
              key: username
        - name: VRA_PASSWORD
          valueFrom:
            secretKeyRef:
              name: vra-credentials
              key: password
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
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"

---
apiVersion: v1
kind: Service
metadata:
  name: vra-rest-server-service
spec:
  selector:
    app: vra-rest-server
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: ClusterIP

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: vra-rest-server-ingress
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - vra-api.company.com
    secretName: vra-api-tls
  rules:
  - host: vra-api.company.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: vra-rest-server-service
            port:
              number: 80
```

## Security Configuration

### HTTPS/TLS Setup

#### Self-signed Certificate (Development)

```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Start server with SSL
vra-rest-server --ssl-cert cert.pem --ssl-key key.pem --port 443
```

#### Production Certificate

```bash
# Using Let's Encrypt with certbot
certbot certonly --standalone -d vra-api.company.com

# Start server with Let's Encrypt certificate
vra-rest-server \
  --ssl-cert /etc/letsencrypt/live/vra-api.company.com/fullchain.pem \
  --ssl-key /etc/letsencrypt/live/vra-api.company.com/privkey.pem \
  --port 443
```

### API Key Authentication

Configure API keys for additional security:

```bash
# Set API keys via environment
export VRA_REST_API_KEYS="prod-key:read-write,readonly-key:read"

# Or in configuration file
```

```json
{
  "rest_server": {
    "api_keys": {
      "enabled": true,
      "keys": {
        "prod-key": ["read", "write", "admin"],
        "readonly-key": ["read"],
        "monitoring-key": ["read", "metrics"]
      }
    }
  }
}
```

Use API keys in requests:

```bash
curl -H "X-API-Key: prod-key" http://localhost:8000/catalog/items
```

## Health Checks and Monitoring

### Health Check Endpoint

```bash
# Basic health check
curl http://localhost:8000/health

# Response
{
  "status": "healthy",
  "version": "0.11.0",
  "uptime": "1 hour 23 minutes",
  "vra_connection": "connected"
}
```

### Metrics Endpoint

```bash
# Prometheus metrics
curl http://localhost:8000/metrics

# Returns Prometheus-format metrics:
# vra_api_requests_total{method="GET",endpoint="/catalog/items"} 127
# vra_api_request_duration_seconds{method="GET",endpoint="/catalog/items"} 0.045
```

### Custom Health Checks

Configure custom health checks:

```json
{
  "rest_server": {
    "health_checks": {
      "vra_api": {
        "enabled": true,
        "timeout": 5,
        "retry_count": 3
      },
      "database": {
        "enabled": false
      }
    }
  }
}
```

## Performance Tuning

### Worker Configuration

```bash
# Optimal workers = CPU cores * 2
vra-rest-server --workers 8  # For 4-core system

# For high-traffic scenarios
vra-rest-server --workers 16 --worker-class uvicorn.workers.UvicornWorker
```

### Connection Pooling

Configure HTTP connection pooling:

```json
{
  "vra_client": {
    "connection_pool": {
      "max_connections": 100,
      "max_connections_per_host": 20,
      "timeout": 30,
      "retry_attempts": 3
    }
  }
}
```

### Caching

Enable response caching:

```json
{
  "rest_server": {
    "cache": {
      "enabled": true,
      "ttl_seconds": 300,
      "max_size": 1000,
      "cache_headers": true
    }
  }
}
```

## Logging Configuration

### Log Levels

Available log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

```bash
# Debug mode for development
vra-rest-server --log-level debug

# Production logging
vra-rest-server --log-level info
```

### Log Format

Configure structured logging:

```json
{
  "logging": {
    "level": "INFO",
    "format": "json",
    "file": "/var/log/vra-rest-server.log",
    "rotation": {
      "max_size": "100MB",
      "backup_count": 7
    },
    "fields": {
      "timestamp": true,
      "request_id": true,
      "user_id": true,
      "endpoint": true,
      "response_time": true
    }
  }
}
```

### Log Analysis

Use structured logs with log aggregation tools:

```bash
# View logs with jq
tail -f /var/log/vra-rest-server.log | jq '.'

# Filter by endpoint
tail -f /var/log/vra-rest-server.log | jq 'select(.endpoint == "/catalog/items")'

# Monitor error rates
tail -f /var/log/vra-rest-server.log | jq 'select(.level == "ERROR")'
```

## Troubleshooting

### Common Issues

**Server won't start**
```bash
# Check port availability
netstat -tlnp | grep 8000

# Check authentication
vra auth status

# Check configuration
vra-rest-server --validate-config
```

**High memory usage**
```bash
# Monitor memory usage
top -p $(pidof vra-rest-server)

# Reduce workers or enable response streaming
vra-rest-server --workers 2 --enable-streaming
```

**SSL certificate errors**
```bash
# Verify certificate
openssl x509 -in cert.pem -text -noout

# Check certificate chain
openssl verify -CAfile ca-bundle.crt cert.pem
```

### Debug Mode

Enable debug mode for troubleshooting:

```bash
vra-rest-server \
  --log-level debug \
  --reload \
  --enable-debug-routes
```

Debug routes available at:
- `/debug/info` - Server information
- `/debug/config` - Current configuration
- `/debug/metrics` - Detailed metrics
- `/debug/auth` - Authentication status

## Next Steps

- [Authentication Configuration](authentication.md)
- [OpenAPI Documentation](openapi.md)
- [Integration Examples](examples.md)
- [Complete API Reference](../rest-api-comprehensive.md)