# VMware vRA REST API Server

The VMware vRA REST API Server provides a HTTP REST API interface for all the functionality available in the CLI tool. This allows you to integrate VMware vRealize Automation operations into web applications, other services, or automation pipelines.

!!! warning "Model Context Protocol Compliance"
    This server implements a traditional HTTP REST API and is **not** compliant with the [Model Context Protocol (MCP) specification](https://modelcontextprotocol.io/specification/2025-06-18). True MCP compliance is planned for a future release.

## Table of Contents

- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Authentication](#authentication)
- [Complete API Reference](#complete-api-reference)
- [Request/Response Schema](#requestresponse-schema)
- [Error Handling](#error-handling)
- [Examples](#examples)
- [Security Considerations](#security-considerations)
- [Production Deployment](#production-deployment)

## Quick Start

### Starting the Server

You can start the server using the CLI command:

```bash
# Start the server on default port 8000
vra-rest-server

# Or run directly with uvicorn for development
uv run uvicorn vmware_vra_cli.app:app --reload --host ******* --port 8000
```

The server will be available at: `http://localhost:8000`

!!! warning "HTTPS Support"
    The MCP server currently serves HTTP only. For production deployments requiring HTTPS, you must use a reverse proxy like Nginx or a load balancer to handle SSL/TLS termination. See the [Production Deployment](#production-deployment) section for details.

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

## Complete API Reference

### Base URL

All API endpoints are relative to the base URL: `http://localhost:8000`

### Authentication Endpoints

#### POST /auth/login

Authenticate to vRA and store tokens.

**Request Body:**
```json
{
  "username": "string",
  "password": "string",
  "url": "string",
  "tenant": "string" | null,
  "domain": "string" | null
}
```

**Response:**
```json
{
  "success": true,
  "message": "Authentication successful",
  "timestamp": "2024-01-01T12:00:00Z",
  "token_stored": true,
  "config_saved": true
}
```

#### POST /auth/logout

Clear stored authentication tokens.

**Response:**
```json
{
  "success": true,
  "message": "Logged out successfully",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### GET /auth/status

Check authentication status.

**Response:**
```json
{
  "success": true,
  "message": "Authenticated (Access token available) with refresh token for automatic renewal",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### POST /auth/refresh

Manually refresh the access token.

**Response:**
```json
{
  "success": true,
  "message": "Access token refreshed successfully",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Catalog Endpoints

#### GET /catalog/items

List available catalog items.

**Query Parameters:**
- `project_id` (optional): Filter by project ID
- `page_size` (default: 100, max: 2000): Number of items per page
- `first_page_only` (default: false): Fetch only the first page
- `verbose` (default: false): Enable verbose HTTP logging

**Response:**
```json
{
  "success": true,
  "message": "Retrieved 156 catalog items",
  "timestamp": "2024-01-01T12:00:00Z",
  "items": [
    {
      "id": "blueprint-ubuntu-server-01",
      "name": "Ubuntu Server Template",
      "type": {
        "name": "blueprint"
      },
      "status": "PUBLISHED",
      "version": "1.2",
      "description": "Standard Ubuntu 20.04 server template"
    }
  ],
  "total_count": 156,
  "page_info": {
    "page_size": 100,
    "first_page_only": false,
    "project_filter": "dev-project-123"
  }
}
```

#### GET /catalog/items/{item_id}

Get details of a specific catalog item.

**Path Parameters:**
- `item_id`: Catalog item identifier

**Query Parameters:**
- `verbose` (default: false): Enable verbose HTTP logging

**Response:**
```json
{
  "success": true,
  "message": "Retrieved catalog item blueprint-ubuntu-server-01",
  "timestamp": "2024-01-01T12:00:00Z",
  "item": {
    "id": "blueprint-ubuntu-server-01",
    "name": "Ubuntu Server Template",
    "type": {
      "name": "blueprint"
    },
    "status": "PUBLISHED",
    "version": "1.2",
    "description": "Standard Ubuntu 20.04 server template with common configurations"
  }
}
```

#### GET /catalog/items/{item_id}/schema

Get the request schema for a catalog item.

**Path Parameters:**
- `item_id`: Catalog item identifier

**Query Parameters:**
- `verbose` (default: false): Enable verbose HTTP logging

**Response:**
```json
{
  "success": true,
  "message": "Retrieved schema for catalog item blueprint-ubuntu-server-01",
  "timestamp": "2024-01-01T12:00:00Z",
  "item_schema": {
    "type": "object",
    "properties": {
      "hostname": {
        "type": "string",
        "title": "Hostname",
        "description": "Server hostname"
      },
      "cpu": {
        "type": "integer",
        "title": "CPU Count",
        "default": 2,
        "minimum": 1,
        "maximum": 8
      },
      "memory": {
        "type": "string",
        "title": "Memory Size",
        "default": "4GB",
        "enum": ["2GB", "4GB", "8GB", "16GB"]
      }
    },
    "required": ["hostname"]
  }
}
```

#### POST /catalog/items/{item_id}/request

Request a catalog item deployment.

**Path Parameters:**
- `item_id`: Catalog item identifier

**Query Parameters:**
- `verbose` (default: false): Enable verbose HTTP logging

**Request Body:**
```json
{
  "item_id": "blueprint-ubuntu-server-01",
  "project_id": "dev-project-123",
  "inputs": {
    "hostname": "web-server-01",
    "cpu": 4,
    "memory": "8GB"
  },
  "reason": "Development web server",
  "name": "web-server-01"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Catalog item request submitted successfully",
  "timestamp": "2024-01-01T12:00:00Z",
  "deployment_id": "deployment-12345-abcdef",
  "request_id": "request-67890-ghijkl"
}
```

### Deployment Endpoints

#### GET /deployments

List deployments.

**Query Parameters:**
- `project_id` (optional): Filter by project ID
- `status` (optional): Filter by status
- `page_size` (default: 100, max: 2000): Number of items per page
- `first_page_only` (default: false): Fetch only the first page
- `verbose` (default: false): Enable verbose HTTP logging

**Response:**
```json
{
  "success": true,
  "message": "Retrieved 89 deployments",
  "timestamp": "2024-01-01T12:00:00Z",
  "deployments": [
    {
      "id": "deployment-12345-abcdef",
      "name": "web-server-01",
      "status": "CREATE_SUCCESSFUL",
      "projectId": "dev-project-123",
      "createdAt": "2024-01-15T09:30:00.000Z",
      "catalogItemId": "blueprint-ubuntu-server-01"
    }
  ],
  "total_count": 89,
  "page_info": {
    "page_size": 100,
    "first_page_only": false,
    "project_filter": "dev-project-123",
    "status_filter": "CREATE_SUCCESSFUL"
  }
}
```

#### GET /deployments/{deployment_id}

Get deployment details.

**Path Parameters:**
- `deployment_id`: Deployment identifier

**Query Parameters:**
- `verbose` (default: false): Enable verbose HTTP logging

**Response:**
```json
{
  "success": true,
  "message": "Retrieved deployment deployment-12345-abcdef",
  "timestamp": "2024-01-01T12:00:00Z",
  "deployment": {
    "id": "deployment-12345-abcdef",
    "name": "web-server-01",
    "status": "CREATE_SUCCESSFUL",
    "projectId": "dev-project-123",
    "catalogItemId": "blueprint-ubuntu-server-01",
    "createdAt": "2024-01-15T09:30:00.000Z",
    "completedAt": "2024-01-15T09:45:00.000Z",
    "inputs": {
      "hostname": "web-server-01",
      "cpu": 4,
      "memory": "8GB"
    }
  }
}
```

#### DELETE /deployments/{deployment_id}

Delete a deployment.

**Path Parameters:**
- `deployment_id`: Deployment identifier

**Query Parameters:**
- `confirm` (required): Must be set to `true` to confirm deletion
- `verbose` (default: false): Enable verbose HTTP logging

**Response:**
```json
{
  "success": true,
  "message": "Deployment deployment-12345-abcdef deletion initiated",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### GET /deployments/{deployment_id}/resources

Get deployment resources.

**Path Parameters:**
- `deployment_id`: Deployment identifier

**Query Parameters:**
- `verbose` (default: false): Enable verbose HTTP logging

**Response:**
```json
{
  "success": true,
  "message": "Retrieved resources for deployment deployment-12345-abcdef",
  "timestamp": "2024-01-01T12:00:00Z",
  "resources": [
    {
      "id": "vm-12345-abcdef",
      "name": "web-server-01",
      "type": "Cloud.vSphere.Machine",
      "status": "SUCCESS",
      "properties": {
        "address": "192.168.1.100",
        "cpu": 4,
        "memory": 8192
      }
    },
    {
      "id": "disk-67890-ghijkl",
      "name": "web-server-01-disk1",
      "type": "Cloud.vSphere.Disk",
      "status": "SUCCESS",
      "properties": {
        "size": "50GB"
      }
    }
  ]
}
```

### Tags Endpoints

*Note: Tag endpoints are defined in the models but not yet implemented in the current router setup. They would include:*

- `GET /tags` - List available tags
- `GET /tags/{tag_id}` - Get tag details
- `POST /tags` - Create a new tag
- `PUT /tags/{tag_id}` - Update a tag
- `DELETE /tags/{tag_id}` - Delete a tag
- `POST /tags/assign` - Assign tag to resource
- `POST /tags/remove` - Remove tag from resource
- `GET /resources/{resource_id}/tags` - Get resource tags

### Workflow Endpoints

*Note: Workflow endpoints are defined in the models but not yet implemented in the current router setup. They would include:*

- `GET /workflows` - List available workflows
- `POST /workflows/{workflow_id}/run` - Execute a workflow

### Report Endpoints

*Note: Report endpoints are defined in the models but not yet implemented in the current router setup. They would include:*

- `GET /reports/activity-timeline` - Generate activity timeline report
- `GET /reports/catalog-usage` - Generate catalog usage report
- `GET /reports/resources-usage` - Generate resources usage report
- `GET /reports/unsync` - Generate unsynced deployments report

### Health and Utility Endpoints

#### GET /

Root endpoint welcome message.

**Response:**
```json
{
  "message": "Welcome to the VMware vRA MCP Server!"
}
```

#### GET /health

Health check endpoint.

**Response:**
```json
{
  "success": true,
  "message": null,
  "timestamp": "2024-01-01T12:00:00Z",
  "status": "healthy",
  "version": "0.1.0",
  "uptime": "3600.25 seconds",
  "vra_connection": null
}
```

## Request/Response Schema

### Common Response Fields

All API responses include these common fields:

- `success` (boolean): Indicates if the operation was successful
- `message` (string|null): Human-readable message about the operation
- `timestamp` (datetime): ISO 8601 timestamp of the response

### Error Response Schema

Error responses include additional fields:

- `error_code` (string|null): Machine-readable error code
- `error_details` (object|null): Additional error information

### Data Validation

All request data is validated using Pydantic models:

- **String fields**: Validated for type and length
- **Integer fields**: Validated for type and range (where applicable)
- **Boolean fields**: Validated for type
- **Optional fields**: Can be null or omitted
- **Enum fields**: Validated against allowed values
- **Pattern fields**: Validated against regular expressions

### Pagination

List endpoints support pagination:

- `page_size`: Number of items per page (1-2000, default: 100)
- `first_page_only`: Boolean to limit to first page only
- Response includes `page_info` object with pagination details

## Error Handling

### HTTP Status Codes

- `200 OK`: Successful operation
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication failed or required
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

### Error Response Examples

#### Validation Error (422)
```json
{
  "success": false,
  "message": [
    {
      "type": "string_too_short",
      "loc": ["body", "username"],
      "msg": "String should have at least 1 character",
      "input": ""
    }
  ],
  "timestamp": 1640995200
}
```

#### Authentication Error (401)
```json
{
  "detail": "Authentication failed: 401 Client Error: Unauthorized for url: https://vra.company.com/csp/gateway/am/api/login"
}
```

#### Not Found Error (404)
```json
{
  "detail": "Catalog item not found: invalid-item-id"
}
```

### Error Handling Best Practices

1. **Always check the `success` field** in responses
2. **Handle HTTP status codes appropriately** in your client
3. **Parse error messages** for user-friendly display
4. **Implement retry logic** for transient errors (5xx)
5. **Log error details** for debugging

## Examples

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

class VRMCPClient {
  constructor(baseURL = 'http://localhost:8000') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }

  async authenticate(credentials) {
    try {
      const response = await this.client.post('/auth/login', credentials);
      return response.data;
    } catch (error) {
      throw new Error(`Authentication failed: ${error.response?.data?.detail || error.message}`);
    }
  }

  async listCatalogItems(options = {}) {
    try {
      const response = await this.client.get('/catalog/items', { params: options });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to list catalog items: ${error.response?.data?.detail || error.message}`);
    }
  }

  async requestCatalogItem(itemId, requestData) {
    try {
      const response = await this.client.post(`/catalog/items/${itemId}/request`, requestData);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to request catalog item: ${error.response?.data?.detail || error.message}`);
    }
  }

  async listDeployments(options = {}) {
    try {
      const response = await this.client.get('/deployments', { params: options });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to list deployments: ${error.response?.data?.detail || error.message}`);
    }
  }
}

// Usage example
async function main() {
  const client = new VRMCPClient();
  
  try {
    // Authenticate
    await client.authenticate({
      username: 'admin',
      password: 'password',
      url: 'https://vra.company.com',
      tenant: 'company.local'
    });
    
    console.log('Authenticated successfully');
    
    // List catalog items
    const catalogItems = await client.listCatalogItems({ page_size: 50 });
    console.log(`Found ${catalogItems.total_count} catalog items`);
    
    // Request a catalog item
    if (catalogItems.items.length > 0) {
      const item = catalogItems.items[0];
      const deployment = await client.requestCatalogItem(item.id, {
        item_id: item.id,
        project_id: 'dev-project-123',
        inputs: {
          hostname: 'test-vm',
          cpu: 2,
          memory: '4GB'
        },
        reason: 'Testing API integration'
      });
      
      console.log(`Deployment created: ${deployment.deployment_id}`);
    }
    
  } catch (error) {
    console.error('Error:', error.message);
  }
}

main();
```

### Python Example

```python
import requests
import json
from typing import Dict, Any, Optional

class VRAMCPClient:
    def __init__(self, base_url: str = 'http://localhost:8000'):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def authenticate(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate to vRA."""
        response = self.session.post(f'{self.base_url}/auth/login', json=credentials)
        response.raise_for_status()
        return response.json()
    
    def list_catalog_items(self, **params) -> Dict[str, Any]:
        """List catalog items."""
        response = self.session.get(f'{self.base_url}/catalog/items', params=params)
        response.raise_for_status()
        return response.json()
    
    def get_catalog_item(self, item_id: str) -> Dict[str, Any]:
        """Get catalog item details."""
        response = self.session.get(f'{self.base_url}/catalog/items/{item_id}')
        response.raise_for_status()
        return response.json()
    
    def request_catalog_item(self, item_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Request a catalog item."""
        response = self.session.post(
            f'{self.base_url}/catalog/items/{item_id}/request', 
            json=request_data
        )
        response.raise_for_status()
        return response.json()
    
    def list_deployments(self, **params) -> Dict[str, Any]:
        """List deployments."""
        response = self.session.get(f'{self.base_url}/deployments', params=params)
        response.raise_for_status()
        return response.json()
    
    def get_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """Get deployment details."""
        response = self.session.get(f'{self.base_url}/deployments/{deployment_id}')
        response.raise_for_status()
        return response.json()
    
    def delete_deployment(self, deployment_id: str, confirm: bool = True) -> Dict[str, Any]:
        """Delete a deployment."""
        response = self.session.delete(
            f'{self.base_url}/deployments/{deployment_id}',
            params={'confirm': confirm}
        )
        response.raise_for_status()
        return response.json()

# Usage example
def main():
    client = VRAMCPClient()
    
    try:
        # Authenticate
        auth_response = client.authenticate({
            'username': 'admin',
            'password': 'password',
            'url': 'https://vra.company.com',
            'tenant': 'company.local'
        })
        print(f"Authentication: {auth_response['message']}")
        
        # List catalog items
        catalog_response = client.list_catalog_items(page_size=50)
        print(f"Found {catalog_response['total_count']} catalog items")
        
        # Get details of first item
        if catalog_response['items']:
            item = catalog_response['items'][0]
            item_details = client.get_catalog_item(item['id'])
            print(f"Item details: {item_details['item']['name']}")
            
            # Request the catalog item
            deployment_response = client.request_catalog_item(item['id'], {
                'item_id': item['id'],
                'project_id': 'dev-project-123',
                'inputs': {
                    'hostname': 'api-test-vm',
                    'cpu': 2,
                    'memory': '4GB'
                },
                'reason': 'API integration test'
            })
            print(f"Deployment created: {deployment_response['deployment_id']}")
        
        # List deployments
        deployments_response = client.list_deployments(project_id='dev-project-123')
        print(f"Found {deployments_response['total_count']} deployments")
        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
```

### cURL Examples

```bash
#!/bin/bash
# Complete workflow example using cURL

BASE_URL="http://localhost:8000"
PROJECT_ID="dev-project-123"

# Function to make authenticated requests
api_call() {
    curl -s -H "Content-Type: application/json" "$@"
}

echo "🔐 Authenticating..."
auth_response=$(api_call -X POST "$BASE_URL/auth/login" -d '{
  "username": "admin",
  "password": "password",
  "url": "https://vra.company.com",
  "tenant": "company.local"
}')

if echo "$auth_response" | jq -r '.success' | grep -q true; then
    echo "✅ Authentication successful"
else
    echo "❌ Authentication failed"
    echo "$auth_response" | jq '.'
    exit 1
fi

echo "📋 Listing catalog items..."
catalog_response=$(api_call "$BASE_URL/catalog/items?page_size=10")
item_count=$(echo "$catalog_response" | jq -r '.total_count')
echo "Found $item_count catalog items"

# Get first catalog item
first_item_id=$(echo "$catalog_response" | jq -r '.items[0].id')
first_item_name=$(echo "$catalog_response" | jq -r '.items[0].name')

if [ "$first_item_id" != "null" ]; then
    echo "🔍 Getting schema for '$first_item_name'..."
    schema_response=$(api_call "$BASE_URL/catalog/items/$first_item_id/schema")
    echo "$schema_response" | jq '.item_schema'
    
    echo "🚀 Requesting catalog item '$first_item_name'..."
    request_response=$(api_call -X POST "$BASE_URL/catalog/items/$first_item_id/request" -d "{
      \"item_id\": \"$first_item_id\",
      \"project_id\": \"$PROJECT_ID\",
      \"inputs\": {
        \"hostname\": \"curl-test-vm\",
        \"cpu\": 2,
        \"memory\": \"4GB\"
      },
      \"reason\": \"cURL API test\"
    }")
    
    deployment_id=$(echo "$request_response" | jq -r '.deployment_id')
    if [ "$deployment_id" != "null" ]; then
        echo "✅ Deployment created: $deployment_id"
        
        echo "📦 Getting deployment details..."
        deployment_response=$(api_call "$BASE_URL/deployments/$deployment_id")
        echo "$deployment_response" | jq '.deployment | {id, name, status, createdAt}'
        
        echo "🔧 Getting deployment resources..."
        resources_response=$(api_call "$BASE_URL/deployments/$deployment_id/resources")
        resource_count=$(echo "$resources_response" | jq '.resources | length')
        echo "Found $resource_count resources"
        echo "$resources_response" | jq '.resources[] | {id, name, type, status}'
    else
        echo "❌ Failed to create deployment"
        echo "$request_response" | jq '.'
    fi
fi

echo "📊 Listing recent deployments..."
deployments_response=$(api_call "$BASE_URL/deployments?project_id=$PROJECT_ID&page_size=5")
deployment_count=$(echo "$deployments_response" | jq -r '.total_count')
echo "Found $deployment_count deployments in project $PROJECT_ID"

echo "✅ API workflow completed successfully"
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

!!! warning "HTTPS Implementation"
    The MCP server currently only supports HTTP. For production deployments, you **must** implement HTTPS using a reverse proxy (e.g., Nginx, Apache) or load balancer. The server does not have built-in SSL/TLS support.

- The server stores authentication tokens securely using the system keyring
- CORS is enabled for all origins in development (configure for production)
- All endpoints except health check and root require authentication
- Sensitive operations require explicit confirmation parameters
- **SSL/TLS termination must be handled by a reverse proxy in production**
- Consider implementing additional authentication layers (API keys, OAuth) for production

## Production Deployment

!!! important "HTTPS Requirements"
    The MCP server **does not support HTTPS directly**. For production deployments, you **must** use a reverse proxy like Nginx, Apache, or a cloud load balancer to handle SSL/TLS termination.

For production deployment, consider:

1. **Reverse Proxy with SSL/TLS**: **Required** - Deploy behind Nginx, Apache, or cloud load balancer for HTTPS
2. **Environment Configuration**: Use environment variables for sensitive configuration
3. **Authentication**: Implement additional authentication layers (API keys, OAuth) if needed
4. **Monitoring**: Add comprehensive logging and monitoring
5. **CORS**: Configure appropriate CORS settings for your domain
6. **Security Headers**: Add security headers via reverse proxy
7. **Rate Limiting**: Implement rate limiting at the reverse proxy level

### Basic Production Setup

**Step 1: Start the MCP server (HTTP only)**
```bash
uvicorn vmware_vra_cli.app:app --host ******* --port 8000 --workers 4
```

**Step 2: Configure reverse proxy for HTTPS**

See the [MCP Server Docker Guide](mcp-server-docker.md) for complete Nginx configuration examples with SSL/TLS setup.

### Recommended Production Architecture

```
Internet → Load Balancer/CDN (HTTPS) → Reverse Proxy (Nginx) → MCP Server (HTTP)
                     ↓
              SSL/TLS Termination
```

The MCP server runs on HTTP internally, while the reverse proxy handles all HTTPS traffic and forwards requests to the server.
