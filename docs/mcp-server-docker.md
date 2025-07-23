# MCP Server Docker Deployment Guide

The VMware vRA MCP Server can be deployed using Docker containers for development, testing, and production environments. This guide covers containerization approaches for the Model Context Protocol compliant server.

!!! info "MCP Server vs REST API Server"
    This guide covers Docker deployment for the **MCP Server** (`vra-mcp-server`), which uses STDIO transport for JSON-RPC 2.0 communication. For the REST API server (`vra-rest-server`), see the [REST API Server Docker Guide](rest-api-server-docker.md).

## Container Architecture Considerations

### MCP Protocol Requirements

The MCP server has unique requirements compared to traditional web services:

- **STDIO Transport**: Uses standard input/output for JSON-RPC communication
- **No HTTP Endpoints**: Does not bind to network ports by default
- **Process-based Communication**: Designed to be spawned by MCP clients
- **Session Management**: Maintains stateful connections with clients

### Container Communication Patterns

#### 1. Client-Server Pattern (Recommended)
The MCP client runs outside the container and spawns the containerized MCP server:

```bash
# Client connects to containerized MCP server
docker run -i vmware-vra-mcp-server vra-mcp-server
```

#### 2. Sidecar Pattern
Both client and server run in the same container environment:

```yaml
services:
  mcp-client:
    image: my-mcp-client
    depends_on:
      - vra-mcp-server
  
  vra-mcp-server:
    image: vmware-vra-mcp-server
    command: ["vra-mcp-server"]
```

#### 3. Embedded Pattern
The MCP server is embedded within a larger application container.

## Building the MCP Server Image

### Basic Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY setup.py .

# Install the application
RUN pip install -e .

# Create non-root user
RUN useradd -m mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

# Set environment variables
ENV PYTHONPATH=/app/src
ENV VRA_CONFIG_DIR=/app/config

# Default command
CMD ["vra-mcp-server"]
```

### Multi-stage Build

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY setup.py .
RUN pip install --user -e .

# Runtime stage
FROM python:3.11-slim

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Add local packages to path
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app/src

# Copy application
COPY src/ /app/src/

# Create config directory
RUN mkdir -p /app/config && chmod 755 /app/config

# Set working directory
WORKDIR /app

# Default command
CMD ["vra-mcp-server"]
```

## Running the MCP Server Container

### Interactive Mode

```bash
# Run MCP server interactively
docker run -i --rm vmware-vra-mcp-server

# With environment variables
docker run -i --rm \
  -e VRA_URL=https://vra.company.com \
  -e VRA_TENANT=corp.local \
  vmware-vra-mcp-server

# With volume mounts
docker run -i --rm \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  vmware-vra-mcp-server
```

### Named Container

```bash
# Run as named container
docker run -d --name vra-mcp-server \
  -e VRA_URL=https://vra.company.com \
  vmware-vra-mcp-server

# Connect to running container
docker exec -i vra-mcp-server vra-mcp-server
```

## Docker Compose Configuration

### Basic Setup

```yaml
version: '3.8'

services:
  vra-mcp-server:
    build: .
    image: vmware-vra-mcp-server:latest
    container_name: vra-mcp-server
    environment:
      - VRA_URL=${VRA_URL}
      - VRA_TENANT=${VRA_TENANT}
      - VRA_VERIFY_SSL=${VRA_VERIFY_SSL:-true}
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
    stdin_open: true
    tty: true
    restart: unless-stopped
```

### Development Setup

```yaml
version: '3.8'

services:
  vra-mcp-server:
    build:
      context: .
      target: builder
    image: vmware-vra-mcp-server:dev
    container_name: vra-mcp-server-dev
    environment:
      - VRA_URL=${VRA_URL}
      - VRA_TENANT=${VRA_TENANT}
      - VRA_DEBUG=true
      - VRA_VERBOSE=true
    volumes:
      - ./src:/app/src
      - ./config:/app/config
      - ./logs:/app/logs
      - ./tests:/app/tests
    stdin_open: true
    tty: true
    command: ["bash"]
```

## Integration Examples

### Claude Desktop with Docker

Configure Claude Desktop to use the containerized MCP server:

```json
{
  "mcpServers": {
    "vmware-vra": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "VRA_URL=https://vra.company.com",
        "-e", "VRA_TENANT=corp.local",
        "vmware-vra-mcp-server"
      ]
    }
  }
}
```

### VS Code Continue with Docker

```json
{
  "experimental": {
    "mcp": {
      "servers": [
        {
          "name": "vmware-vra",
          "command": ["docker", "run", "-i", "--rm", "vmware-vra-mcp-server"],
          "env": {
            "VRA_URL": "https://vra.company.com",
            "VRA_TENANT": "corp.local"
          }
        }
      ]
    }
  }
}
```

### Python Client with Docker

```python
import asyncio
import subprocess
from typing import Dict, Any

class DockerMcpClient:
    def __init__(self, image: str = "vmware-vra-mcp-server"):
        self.image = image
        self.process = None
    
    async def start(self, env_vars: Dict[str, str] = None):
        """Start the containerized MCP server."""
        cmd = ["docker", "run", "-i", "--rm"]
        
        # Add environment variables
        if env_vars:
            for key, value in env_vars.items():
                cmd.extend(["-e", f"{key}={value}"])
        
        cmd.append(self.image)
        
        self.process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
    
    async def send_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send a JSON-RPC message to the MCP server."""
        import json
        
        message_json = json.dumps(message) + '\n'
        self.process.stdin.write(message_json.encode())
        await self.process.stdin.drain()
        
        response_line = await self.process.stdout.readline()
        return json.loads(response_line.decode())
    
    async def stop(self):
        """Stop the MCP server."""
        if self.process:
            self.process.stdin.close()
            await self.process.wait()

# Usage example
async def main():
    client = DockerMcpClient()
    
    await client.start({
        "VRA_URL": "https://vra.company.com",
        "VRA_TENANT": "corp.local"
    })
    
    # Initialize
    response = await client.send_message({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {"tools": {}},
            "clientInfo": {"name": "docker-client", "version": "1.0"}
        }
    })
    
    print("Server initialized:", response["result"]["serverInfo"]["name"])
    
    await client.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration Management

### Environment Variables

```bash
# Create environment file
cat > .env << EOF
VRA_URL=https://vra.company.com
VRA_TENANT=corp.local
VRA_VERIFY_SSL=true
VRA_TIMEOUT=60
VRA_DEBUG=false
VRA_VERBOSE=false
VRA_CONFIG_DIR=/app/config
VRA_LOG_LEVEL=INFO
EOF

# Use with Docker
docker run -i --rm --env-file .env vmware-vra-mcp-server
```

### Configuration Files

```bash
# Create config directory
mkdir -p config

# Create configuration file
cat > config/vra-mcp.yaml << EOF
server:
  protocol_version: "2025-06-18"
  capabilities:
    tools: {}
    resources: 
      subscribe: true
    logging: {}

vra:
  url: "https://vra.company.com"
  tenant: "corp.local"
  verify_ssl: true
  timeout: 60
  
logging:
  level: INFO
  format: json
EOF

# Mount config directory
docker run -i --rm -v $(pwd)/config:/app/config vmware-vra-mcp-server
```

### Secrets Management

```yaml
# Using Docker secrets
version: '3.8'

services:
  vra-mcp-server:
    image: vmware-vra-mcp-server
    secrets:
      - vra_username
      - vra_password
    environment:
      - VRA_URL=https://vra.company.com
      - VRA_USERNAME_FILE=/run/secrets/vra_username
      - VRA_PASSWORD_FILE=/run/secrets/vra_password
    stdin_open: true
    tty: true

secrets:
  vra_username:
    file: ./secrets/username.txt
  vra_password:
    file: ./secrets/password.txt
```

## Monitoring and Debugging

### Health Checks

Since MCP servers don't expose HTTP endpoints, health checks are different:

```yaml
services:
  vra-mcp-server:
    image: vmware-vra-mcp-server
    healthcheck:
      test: ["CMD", "pgrep", "-f", "vra-mcp-server"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Logging

```bash
# View container logs
docker logs vra-mcp-server

# Follow logs in real-time
docker logs -f vra-mcp-server

# View logs with timestamps
docker logs -t vra-mcp-server

# View last 100 lines
docker logs --tail 100 vra-mcp-server
```

### Debugging

```bash
# Enter container for debugging
docker exec -it vra-mcp-server /bin/bash

# Run with debug output
docker run -i --rm \
  -e VRA_DEBUG=true \
  -e VRA_VERBOSE=true \
  vmware-vra-mcp-server

# Check environment variables
docker exec vra-mcp-server env | grep VRA
```

## Production Considerations

### Resource Limits

```yaml
services:
  vra-mcp-server:
    image: vmware-vra-mcp-server
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    restart: unless-stopped
```

### Security

```yaml
services:
  vra-mcp-server:
    image: vmware-vra-mcp-server
    user: "1000:1000"  # Run as non-root
    read_only: true    # Read-only filesystem
    tmpfs:
      - /tmp
      - /var/tmp
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
```

### Networking

Since MCP servers use STDIO, traditional Docker networking isn't typically required:

```yaml
services:
  vra-mcp-server:
    image: vmware-vra-mcp-server
    network_mode: "none"  # No network access needed for STDIO
    # Or for vRA API access:
    # networks:
    #   - vra-network
```

## Troubleshooting

### Common Issues

1. **Container Exits Immediately**
   ```bash
   # Check if STDIN is properly connected
   docker run -i vmware-vra-mcp-server
   
   # Verify the command
   docker run --rm vmware-vra-mcp-server vra-mcp-server --help
   ```

2. **Communication Issues**
   ```bash
   # Test JSON-RPC communication
   echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | docker run -i --rm vmware-vra-mcp-server
   ```

3. **Authentication Problems**
   ```bash
   # Check environment variables
   docker run --rm -e VRA_URL=https://vra.company.com vmware-vra-mcp-server env | grep VRA
   ```

### Debugging Commands

```bash
# Interactive debugging session
docker run -it --rm vmware-vra-mcp-server /bin/bash

# Run tests inside container
docker run --rm -v $(pwd)/tests:/app/tests vmware-vra-mcp-server pytest /app/tests

# Check file permissions
docker run --rm vmware-vra-mcp-server ls -la /app/
```

## Best Practices

1. **Use Multi-stage Builds**: Minimize image size
2. **Non-root User**: Run containers as non-root
3. **Resource Limits**: Set appropriate CPU/memory limits
4. **Read-only Filesystem**: Use read-only containers when possible
5. **Secrets Management**: Use proper secret management
6. **Health Checks**: Implement appropriate health checks
7. **Logging**: Configure structured logging
8. **Monitoring**: Monitor container performance

This guide provides a comprehensive approach to containerizing and deploying the VMware vRA MCP Server using Docker, enabling flexible deployment patterns while maintaining MCP protocol compliance.
