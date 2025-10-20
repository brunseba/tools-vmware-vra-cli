# VMware vRA REST API Server - Complete Documentation

The VMware vRA REST API Server provides HTTP REST endpoints for all CLI functionality, including advanced reporting and workflow management capabilities.

## Quick Start

### Starting the REST Server

```bash
# Basic server
vra-rest-server

# Server available at: http://localhost:8000
# Interactive docs: http://localhost:8000/docs
# OpenAPI spec: http://localhost:8000/openapi.json
```

### Docker Deployment

```bash
# Complete environment with documentation
docker compose --profile docs --profile monitoring up -d

# Available services:
# - REST API: http://localhost:8000
# - Swagger UI: http://localhost:8090
# - Log Viewer: http://localhost:8080
```

## API Overview

The REST API provides full parity with the CLI tool across five main categories:

| Category | Endpoints | Description |
|----------|-----------|-------------|
| **Authentication** | 4 endpoints | Token management and authentication |
| **Catalog** | 4 endpoints | Service catalog operations |
| **Deployments** | 4 endpoints | Deployment lifecycle management |
| **Reports** | 4 endpoints | **NEW!** Advanced analytics and insights |
| **Workflows** | 5 endpoints | **NEW!** vRO workflow management |

## Authentication Endpoints

All API endpoints require authentication. Start with the login endpoint:

### POST `/auth/login`

Authenticate to vRA and store tokens.

**Request Body:**
```json
{
  "username": "admin@corp.local",
  "password": "your-password",
  "url": "https://vra.company.com",
  "tenant": "corp.local",
  "domain": "vsphere.local"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Authentication successful",
  "token_stored": true,
  "config_saved": true,
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Other Authentication Endpoints

- `POST /auth/logout` - Clear stored tokens
- `GET /auth/status` - Check authentication status  
- `POST /auth/refresh` - Refresh access token

## Catalog Endpoints

### GET `/catalog/items`

List available catalog items with optional filtering.

**Query Parameters:**
- `project_id` (optional): Filter by project ID
- `page_size` (optional): Items per page (1-2000, default: 100)
- `first_page_only` (optional): Fetch only first page (default: false)
- `verbose` (optional): Enable verbose logging (default: false)

**Example Request:**
```bash
curl -X GET "http://localhost:8000/catalog/items?page_size=50&project_id=dev-project-123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "message": "Retrieved 25 catalog items",
  "items": [
    {
      "id": "blueprint-ubuntu-server",
      "name": "Ubuntu Server 20.04",
      "type": "com.vmw.blueprint",
      "status": "PUBLISHED",
      "version": "2.1"
    }
  ],
  "total_count": 25,
  "page_info": {
    "page_size": 50,
    "first_page_only": false,
    "project_filter": "dev-project-123"
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Other Catalog Endpoints

- `GET /catalog/items/{item_id}` - Get catalog item details
- `GET /catalog/items/{item_id}/schema` - Get catalog item schema
- `POST /catalog/items/{item_id}/request` - Request catalog item deployment

## Deployment Endpoints

### GET `/deployments`

List deployments with filtering options.

**Query Parameters:**
- `project_id` (optional): Filter by project ID
- `status` (optional): Filter by deployment status
- `page_size` (optional): Items per page (default: 100)
- `first_page_only` (optional): Fetch only first page
- `verbose` (optional): Enable verbose logging

**Example:**
```bash
curl -X GET "http://localhost:8000/deployments?status=CREATE_SUCCESSFUL&page_size=20"
```

### Other Deployment Endpoints

- `GET /deployments/{deployment_id}` - Get deployment details
- `DELETE /deployments/{deployment_id}` - Delete deployment (requires confirmation)
- `GET /deployments/{deployment_id}/resources` - Get deployment resources

## Reporting Endpoints (NEW!)

Advanced analytics and reporting capabilities for infrastructure insights.

### GET `/reports/activity-timeline`

Generate deployment activity timeline with trends and peak analysis.

**Query Parameters:**
- `project_id` (optional): Filter by project ID
- `days_back` (optional): Days back for timeline (1-365, default: 30)
- `group_by` (optional): Time grouping - `day`, `week`, `month`, `year` (default: `day`)
- `statuses` (optional): Comma-separated status list

**Example:**
```bash
curl -X GET "http://localhost:8000/reports/activity-timeline?days_back=90&group_by=week"
```

**Response:**
```json
{
  "success": true,
  "message": "Activity timeline generated for 90 days",
  "timeline_data": {
    "summary": {
      "total_deployments": 145,
      "successful_deployments": 132,
      "failed_deployments": 8,
      "in_progress_deployments": 5,
      "success_rate": 91.0,
      "trend": "increasing",
      "trend_percentage": 15.3,
      "peak_activity_period": "2024-W03",
      "peak_activity_count": 23,
      "peak_hour": "10:00",
      "peak_hour_count": 12,
      "unique_catalog_items": 8,
      "unique_projects": 3
    },
    "period_activity": {
      "2024-W01": {
        "total_deployments": 18,
        "successful_deployments": 16,
        "failed_deployments": 2,
        "in_progress_deployments": 0,
        "unique_catalog_items": 4,
        "unique_projects": 2
      }
    }
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### GET `/reports/catalog-usage`

Generate catalog usage statistics with deployment counts and success rates.

**Query Parameters:**
- `project_id` (optional): Filter by project ID
- `include_zero` (optional): Include items with zero deployments (default: false)
- `sort_by` (optional): Sort by - `deployments`, `resources`, `name` (default: `deployments`)
- `detailed_resources` (optional): Fetch exact resource counts (default: false)

**Response Example:**
```json
{
  "success": true,
  "message": "Catalog usage report generated for 12 items",
  "usage_stats": [
    {
      "id": "blueprint-ubuntu-server",
      "name": "Ubuntu Server 20.04",
      "type": "com.vmw.blueprint",
      "deployment_count": 45,
      "resource_count": 135,
      "success_count": 42,
      "failed_count": 2,
      "in_progress_count": 1,
      "success_rate": 93.3,
      "status_breakdown": {
        "CREATE_SUCCESSFUL": 42,
        "CREATE_FAILED": 2,
        "CREATE_INPROGRESS": 1
      }
    }
  ],
  "summary": {
    "total_catalog_items": 12,
    "active_items": 8,
    "total_deployments_system_wide": 156,
    "catalog_linked_deployments": 145,
    "unlinked_deployments": 11,
    "total_resources": 487,
    "average_deployments_per_active_item": 18.1
  }
}
```

### GET `/reports/resources-usage`

Generate comprehensive resources usage report across all deployments.

**Query Parameters:**
- `project_id` (optional): Filter by project ID
- `detailed_resources` (optional): Fetch detailed resource info (default: true)
- `sort_by` (optional): Sort by - `deployment-name`, `catalog-item`, `resource-count`, `status`
- `group_by` (optional): Group by - `catalog-item`, `resource-type`, `deployment-status`

**Response includes:**
- Total resource counts by type and status
- Resource breakdown per deployment
- Catalog item resource utilization
- Unlinked deployments and their resources

### GET `/reports/unsync`

Generate report of deployments not linked to catalog items with root cause analysis.

**Query Parameters:**
- `project_id` (optional): Filter by project ID
- `detailed_resources` (optional): Fetch exact resource counts (default: false)
- `reason_filter` (optional): Filter by specific reason

**Response includes:**
- Unsynced deployment statistics
- Root cause analysis and remediation suggestions
- Status and age breakdowns
- Detailed analysis for each unsynced deployment

## Workflow Endpoints (NEW!)

vRealize Orchestrator workflow management and execution.

### GET `/workflows`

List available vRealize Orchestrator workflows.

**Query Parameters:**
- `page_size` (optional): Items per page (1-2000, default: 100)
- `first_page_only` (optional): Fetch only first page (default: false)
- `verbose` (optional): Enable verbose logging

**Example:**
```bash
curl -X GET "http://localhost:8000/workflows?page_size=50"
```

**Response:**
```json
{
  "success": true,
  "message": "Retrieved 23 workflows",
  "workflows": [
    {
      "id": "create-user-workflow",
      "name": "Create User Account",
      "description": "Automated user account creation workflow",
      "version": "1.2.0"
    }
  ],
  "total_count": 23,
  "page_info": {
    "page_size": 50,
    "first_page_only": false
  }
}
```

### GET `/workflows/{workflow_id}`

Get workflow input/output schema and parameter definitions.

**Response:**
```json
{
  "success": true,
  "message": "Workflow schema retrieved for create-user-workflow",
  "workflow_schema": {
    "id": "create-user-workflow",
    "name": "Create User Account",
    "description": "Automated user account creation",
    "input-parameters": [
      {
        "name": "username",
        "type": "string",
        "description": "Username for the new account"
      },
      {
        "name": "department",
        "type": "string", 
        "description": "User's department"
      }
    ],
    "output-parameters": [
      {
        "name": "userId",
        "type": "string",
        "description": "Generated user ID"
      }
    ]
  }
}
```

### POST `/workflows/{workflow_id}/run`

Execute a workflow with specified inputs.

**Request Body:**
```json
{
  "inputs": {
    "username": "john.doe",
    "department": "IT",
    "email": "john.doe@company.com"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Workflow create-user-workflow execution started",
  "execution_id": "exec-12345-abcdef",
  "state": "running"
}
```

### GET `/workflows/{workflow_id}/executions/{execution_id}`

Get workflow execution details and current status.

### PUT `/workflows/{workflow_id}/executions/{execution_id}/cancel`

Cancel a running workflow execution.

## Error Handling

All endpoints follow consistent error response format:

```json
{
  "success": false,
  "message": "Authentication failed: Invalid credentials",
  "error_code": "AUTH_FAILED",
  "error_details": {
    "reason": "Invalid username or password",
    "retry_after": 60
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Common HTTP Status Codes

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Default**: 100 requests per minute per IP
- **Authenticated**: 500 requests per minute per user
- **Reports**: 10 requests per minute (resource-intensive)

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248600
```

## OpenAPI Specification

### Interactive Documentation

Visit `http://localhost:8000/docs` for:
- Interactive API explorer
- Request/response examples
- Parameter documentation
- Authentication testing

### OpenAPI JSON

Download the complete OpenAPI 3.0 specification:
```bash
curl http://localhost:8000/openapi.json > vra-api-spec.json
```

## SDK Generation

Generate client SDKs using the OpenAPI specification:

```bash
# Python SDK
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g python \
  -o ./python-sdk

# JavaScript SDK  
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g javascript \
  -o ./js-sdk

# Go SDK
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g go \
  -o ./go-sdk
```

## Integration Examples

### Python Integration

```python
import requests
import json

class VRAClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def authenticate(self, username, password, url, tenant=None):
        response = self.session.post(f"{self.base_url}/auth/login", json={
            "username": username,
            "password": password,
            "url": url,
            "tenant": tenant
        })
        return response.json()
    
    def list_catalog_items(self, project_id=None, page_size=100):
        params = {"page_size": page_size}
        if project_id:
            params["project_id"] = project_id
            
        response = self.session.get(f"{self.base_url}/catalog/items", params=params)
        return response.json()
    
    def get_activity_timeline(self, days_back=30, group_by="day"):
        params = {"days_back": days_back, "group_by": group_by}
        response = self.session.get(f"{self.base_url}/reports/activity-timeline", params=params)
        return response.json()
    
    def run_workflow(self, workflow_id, inputs=None):
        data = {"inputs": inputs or {}}
        response = self.session.post(f"{self.base_url}/workflows/{workflow_id}/run", json=data)
        return response.json()

# Usage
client = VRAClient()

# Authenticate
auth_result = client.authenticate(
    username="admin",
    password="password", 
    url="https://vra.company.com"
)

if auth_result["success"]:
    # Get catalog items
    items = client.list_catalog_items(page_size=50)
    
    # Generate activity report
    timeline = client.get_activity_timeline(days_back=90, group_by="week")
    
    # Run workflow
    workflow_result = client.run_workflow("create-user-workflow", {
        "username": "john.doe",
        "department": "IT"
    })
```

### JavaScript Integration

```javascript
class VRAClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    async authenticate(username, password, url, tenant = null) {
        const response = await fetch(`${this.baseUrl}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username,
                password,
                url,
                tenant
            })
        });
        return await response.json();
    }
    
    async listCatalogItems(projectId = null, pageSize = 100) {
        const params = new URLSearchParams({
            page_size: pageSize.toString()
        });
        if (projectId) {
            params.append('project_id', projectId);
        }
        
        const response = await fetch(`${this.baseUrl}/catalog/items?${params}`);
        return await response.json();
    }
    
    async getCatalogUsageReport(includeZero = false, sortBy = 'deployments') {
        const params = new URLSearchParams({
            include_zero: includeZero.toString(),
            sort_by: sortBy
        });
        
        const response = await fetch(`${this.baseUrl}/reports/catalog-usage?${params}`);
        return await response.json();
    }
    
    async runWorkflow(workflowId, inputs = {}) {
        const response = await fetch(`${this.baseUrl}/workflows/${workflowId}/run`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ inputs })
        });
        return await response.json();
    }
}

// Usage
const client = new VRAClient();

// Authenticate and generate comprehensive report
async function generateDashboard() {
    // Authenticate
    const authResult = await client.authenticate(
        'admin', 
        'password', 
        'https://vra.company.com'
    );
    
    if (authResult.success) {
        // Get data for dashboard
        const [catalog, timeline, usage, deployments] = await Promise.all([
            client.listCatalogItems(),
            client.getActivityTimeline(30, 'day'),
            client.getCatalogUsageReport(false, 'deployments'),
            client.listDeployments()
        ]);
        
        console.log('Dashboard Data:', {
            catalog: catalog.items.length,
            timeline: timeline.timeline_data.summary,
            usage: usage.summary,
            deployments: deployments.deployments.length
        });
    }
}
```

### cURL Examples

```bash
#!/bin/bash
# Complete API workflow example

BASE_URL="http://localhost:8000"

# 1. Authenticate
AUTH_RESPONSE=$(curl -s -X POST "${BASE_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password",
    "url": "https://vra.company.com"
  }')

echo "Authentication: $(echo $AUTH_RESPONSE | jq -r '.message')"

# 2. List catalog items
echo "Fetching catalog items..."
curl -s "${BASE_URL}/catalog/items?page_size=10" | jq '.items[] | {id, name, type}'

# 3. Generate activity timeline
echo "Generating 30-day activity timeline..."
curl -s "${BASE_URL}/reports/activity-timeline?days_back=30&group_by=week" | \
  jq '.timeline_data.summary | {total_deployments, success_rate, trend}'

# 4. Get catalog usage report
echo "Generating catalog usage report..."
curl -s "${BASE_URL}/reports/catalog-usage?sort_by=deployments" | \
  jq '.summary | {total_catalog_items, active_items, total_resources}'

# 5. List workflows
echo "Available workflows:"
curl -s "${BASE_URL}/workflows?page_size=5" | jq '.workflows[] | {id, name}'

# 6. Get deployment resources report
echo "Resources usage analysis..."
curl -s "${BASE_URL}/reports/resources-usage" | \
  jq '.report_data.summary | {total_deployments, total_resources, unique_resource_types}'
```

## Monitoring and Observability

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "success": true,
  "status": "healthy",
  "version": "0.11.0", 
  "uptime": "3600.45 seconds",
  "vra_connection": "connected"
}
```

### Metrics Endpoint

```bash
curl http://localhost:8000/metrics
```

### Docker Compose Monitoring Stack

```yaml
version: '3.8'
services:
  vra-api:
    image: vmware-vra-cli:latest
    ports:
      - "8000:8000"
    
  swagger-ui:
    image: swaggerapi/swagger-ui
    environment:
      - SWAGGER_JSON=/app/openapi.json
    ports:
      - "8090:8080"
      
  dozzle:
    image: amir20/dozzle:latest
    ports:
      - "8080:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
```

## Security Best Practices

### Authentication
- Always authenticate before making requests
- Store tokens securely (avoid localStorage in browsers)
- Implement token refresh logic

### HTTPS in Production
```bash
# Use HTTPS in production environments
export VRA_API_SSL_CERT=/path/to/cert.pem
export VRA_API_SSL_KEY=/path/to/key.pem
vra-rest-server --ssl
```

### API Keys (Optional)
```bash
# Enable API key authentication
export VRA_API_REQUIRE_KEY=true
export VRA_API_KEYS="key1:read,key2:read-write"
```

Request with API key:
```bash
curl -H "X-API-Key: key1" http://localhost:8000/catalog/items
```

---

**Built with ❤️ for programmatic VMware infrastructure automation**