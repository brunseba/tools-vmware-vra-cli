# VMware vRA MCP Server

The VMware vRA MCP (Model Context Protocol) Server provides a REST API interface for all the functionality available in the CLI tool. This allows you to integrate VMware vRealize Automation operations into web applications, other services, or automation pipelines.

## Quick Start

### Starting the Server

You can start the server using the CLI command:

```bash
# Start the server on default port 8000
vra-server

# Or run directly with uvicorn for development
uv run uvicorn vmware_vra_cli.app:app --reload --host 0.0.0.0 --port 8000
```

The server will be available at: `http://localhost:8000`

### API Documentation

Once the server is running, you can access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Authentication

Before using most endpoints, you need to authenticate with your VMware vRA instance.

### Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your-username",
    "password": "your-password", 
    "url": "https://your-vra-server.com",
    "tenant": "your-tenant",
    "domain": "your-domain"
  }'
```

### Check Authentication Status

```bash
curl "http://localhost:8000/auth/status"
```

### Logout

```bash
curl -X POST "http://localhost:8000/auth/logout"
```

## Available Endpoints

### Health Check

```bash
curl "http://localhost:8000/health"
```

### Catalog Operations

#### List Catalog Items

```bash
curl "http://localhost:8000/catalog/items?project_id=your-project-id&page_size=50"
```

#### Get Catalog Item Details

```bash
curl "http://localhost:8000/catalog/items/{item_id}"
```

#### Get Catalog Item Schema

```bash
curl "http://localhost:8000/catalog/items/{item_id}/schema"
```

#### Request Catalog Item

```bash
curl -X POST "http://localhost:8000/catalog/items/{item_id}/request" \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": "catalog-item-id",
    "project_id": "project-id", 
    "inputs": {
      "input1": "value1",
      "input2": "value2"
    },
    "name": "deployment-name",
    "reason": "Business justification"
  }'
```

### Deployment Operations

#### List Deployments

```bash
curl "http://localhost:8000/deployments?project_id=your-project-id&status=CREATE_SUCCESSFUL"
```

#### Get Deployment Details

```bash
curl "http://localhost:8000/deployments/{deployment_id}"
```

#### Get Deployment Resources

```bash
curl "http://localhost:8000/deployments/{deployment_id}/resources"
```

#### Delete Deployment

```bash
curl -X DELETE "http://localhost:8000/deployments/{deployment_id}?confirm=true"
```

## Response Format

All API responses follow a consistent format:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    // Response-specific data
  }
}
```

Error responses:

```json
{
  "success": false,
  "message": "Error description",
  "timestamp": "2024-01-01T12:00:00Z",
  "error_code": "ERROR_CODE",
  "error_details": {
    // Additional error information
  }
}
```

## Configuration

The server uses the same configuration system as the CLI tool. You can configure:

- VMware vRA server URL
- SSL verification settings
- Default project IDs
- Timeout settings

Configuration can be set via:
- Environment variables (prefixed with `VRA_`)
- Configuration files
- API endpoints

## Development

### Running Tests

```bash
uv run pytest tests/test_server.py -v
```

### Development Mode

For development with auto-reload:

```bash
uv run uvicorn vmware_vra_cli.app:app --reload --host 0.0.0.0 --port 8000
```

### Code Coverage

```bash
uv run pytest --cov=src --cov-report=html
```

## Architecture

The server is built using:

- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: Lightning-fast ASGI server
- **Same core libraries**: Reuses the CLI's API client and authentication logic

### Project Structure

```
src/vmware_vra_cli/
├── app.py                    # FastAPI application
├── server/
│   ├── models.py            # Pydantic request/response models
│   ├── utils.py             # Utility functions
│   └── routers/
│       ├── auth.py          # Authentication endpoints
│       ├── catalog.py       # Catalog endpoints
│       └── deployments.py   # Deployment endpoints
├── api/                     # Shared API clients
├── auth.py                  # Authentication logic
└── config.py               # Configuration management
```

## Security Considerations

- The server stores authentication tokens securely using the system keyring
- CORS is enabled for all origins in development (configure for production)
- All endpoints except health check and root require authentication
- Sensitive operations require explicit confirmation parameters

## Production Deployment

For production deployment, consider:

1. **Environment Configuration**: Use environment variables for configuration
2. **Reverse Proxy**: Deploy behind nginx or similar
3. **SSL/TLS**: Enable HTTPS
4. **Authentication**: Implement additional authentication layers if needed
5. **Monitoring**: Add logging and monitoring
6. **CORS**: Configure appropriate CORS settings

Example production start:

```bash
uvicorn vmware_vra_cli.app:app --host 0.0.0.0 --port 8000 --workers 4
```
