# OpenAPI Documentation

The VMware vRA REST API server provides comprehensive OpenAPI 3.0 documentation with interactive exploration capabilities.

## Interactive Documentation

### Swagger UI

Access the interactive API documentation at:

```
http://localhost:8000/docs
```

Features:
- **Interactive API Explorer**: Test endpoints directly from the browser
- **Schema Validation**: Real-time request/response validation
- **Authentication Testing**: Test different authentication methods
- **Example Requests**: Pre-filled examples for all endpoints
- **Response Inspection**: View detailed response schemas and examples

### ReDoc Documentation

Alternative documentation interface:

```
http://localhost:8000/redoc
```

Features:
- **Clean Layout**: Organized, easy-to-read documentation
- **Code Samples**: Multiple programming language examples
- **Schema Explorer**: Interactive schema navigation
- **Search Functionality**: Quick endpoint and schema search

## OpenAPI Specification

### Download Specification

Get the complete OpenAPI 3.0 specification:

```bash
# JSON format
curl http://localhost:8000/openapi.json > vra-api-spec.json

# YAML format  
curl -H "Accept: application/yaml" http://localhost:8000/openapi.yaml > vra-api-spec.yaml
```

### Specification Overview

```json
{
  "openapi": "3.0.2",
  "info": {
    "title": "VMware vRA REST API",
    "description": "Comprehensive REST API for VMware vRealize Automation management",
    "version": "0.11.0",
    "contact": {
      "name": "VMware vRA CLI",
      "url": "https://github.com/brunseba/tools-vmware-vra-cli"
    },
    "license": {
      "name": "MIT",
      "url": "https://opensource.org/licenses/MIT"
    }
  },
  "servers": [
    {
      "url": "http://localhost:8000",
      "description": "Local development server"
    },
    {
      "url": "https://api.company.com",
      "description": "Production server"
    }
  ]
}
```

## Authentication in OpenAPI

### Security Schemes

The API supports multiple authentication methods:

```yaml
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: vRA bearer token authentication
      
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
      description: API key for programmatic access
      
    ApiKeyHeader:
      type: apiKey
      in: header
      name: Authorization
      description: API key in Authorization header (Api-Key <key>)
```

### Testing Authentication

1. **Via Swagger UI**:
   - Click "Authorize" button
   - Enter credentials or API key
   - Test endpoints with authentication

2. **Via cURL**:
   ```bash
   # Bearer token
   curl -H "Authorization: Bearer <token>" http://localhost:8000/catalog/items
   
   # API key
   curl -H "X-API-Key: <key>" http://localhost:8000/catalog/items
   ```

## API Endpoints Documentation

### Authentication Endpoints

```yaml
paths:
  /auth/login:
    post:
      summary: Authenticate with vRA
      description: Login to vRA and store authentication token
      operationId: login
      tags: [Authentication]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/LoginRequest'
            examples:
              basic_login:
                summary: Basic login
                value:
                  username: "admin@corp.local"
                  password: "password"
                  url: "https://vra.company.com"
                  tenant: "corp.local"
      responses:
        '200':
          description: Authentication successful
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AuthResponse'
```

### Catalog Endpoints

```yaml
  /catalog/items:
    get:
      summary: List catalog items
      description: Retrieve available catalog items with optional filtering
      operationId: listCatalogItems
      tags: [Catalog]
      security:
        - BearerAuth: []
        - ApiKeyAuth: []
      parameters:
        - name: project_id
          in: query
          description: Filter by project ID
          schema:
            type: string
            example: "dev-project-123"
        - name: page_size
          in: query
          description: Number of items per page
          schema:
            type: integer
            minimum: 1
            maximum: 2000
            default: 100
      responses:
        '200':
          description: List of catalog items
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CatalogItemsResponse'
```

### Reporting Endpoints

```yaml
  /reports/activity-timeline:
    get:
      summary: Generate activity timeline report
      description: Generate deployment activity timeline with trends and analytics
      operationId: getActivityTimeline
      tags: [Reports]
      security:
        - BearerAuth: []
        - ApiKeyAuth: []
      parameters:
        - name: days_back
          in: query
          description: Number of days back to analyze
          schema:
            type: integer
            minimum: 1
            maximum: 365
            default: 30
        - name: group_by
          in: query
          description: Time grouping for analysis
          schema:
            type: string
            enum: [day, week, month, year]
            default: day
      responses:
        '200':
          description: Activity timeline data
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ActivityTimelineResponse'
```

## Data Schemas

### Request Schemas

```yaml
components:
  schemas:
    LoginRequest:
      type: object
      required: [username, password, url]
      properties:
        username:
          type: string
          description: vRA username
          example: "admin@corp.local"
        password:
          type: string
          format: password
          description: User password
        url:
          type: string
          format: uri
          description: vRA server URL
          example: "https://vra.company.com"
        tenant:
          type: string
          description: vRA tenant
          example: "corp.local"
        domain:
          type: string
          description: Authentication domain
          default: "vsphere.local"
    
    CatalogItemRequest:
      type: object
      required: [catalog_item_id, project_id, name]
      properties:
        catalog_item_id:
          type: string
          description: Catalog item identifier
        project_id:
          type: string
          description: Target project ID
        name:
          type: string
          description: Deployment name
        description:
          type: string
          description: Deployment description
        inputs:
          type: object
          description: Deployment input parameters
          additionalProperties: true
```

### Response Schemas

```yaml
    AuthResponse:
      type: object
      properties:
        success:
          type: boolean
          description: Operation success status
        message:
          type: string
          description: Response message
        token_stored:
          type: boolean
          description: Whether token was stored successfully
        expires_at:
          type: string
          format: date-time
          description: Token expiration time
          
    CatalogItemsResponse:
      type: object
      properties:
        success:
          type: boolean
        items:
          type: array
          items:
            $ref: '#/components/schemas/CatalogItem'
        total_count:
          type: integer
          description: Total number of items
        page_info:
          $ref: '#/components/schemas/PageInfo'
          
    CatalogItem:
      type: object
      properties:
        id:
          type: string
          description: Catalog item ID
        name:
          type: string
          description: Catalog item name
        type:
          type: string
          description: Item type
        status:
          type: string
          description: Item status
        version:
          type: string
          description: Item version
        description:
          type: string
          description: Item description
```

## Error Schemas

```yaml
    ErrorResponse:
      type: object
      properties:
        success:
          type: boolean
          example: false
        error:
          type: string
          description: Error code
          example: "AUTH_FAILED"
        message:
          type: string
          description: Human-readable error message
          example: "Authentication failed: Invalid credentials"
        details:
          type: object
          description: Additional error details
          properties:
            error_type:
              type: string
            suggestion:
              type: string
        timestamp:
          type: string
          format: date-time
          description: Error timestamp
```

## Code Generation

### Generate Client SDKs

Use the OpenAPI specification to generate client libraries:

#### Python Client

```bash
# Install OpenAPI Generator
npm install -g @openapitools/openapi-generator-cli

# Generate Python client
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g python \
  -o ./python-client \
  --additional-properties=projectName=vra-api-client,packageName=vra_api_client

# Install and use
cd python-client
pip install -e .
```

Python usage:
```python
from vra_api_client import ApiClient, Configuration
from vra_api_client.api.catalog_api import CatalogApi

# Configure client
config = Configuration(host="http://localhost:8000")
client = ApiClient(config)

# Use API
catalog_api = CatalogApi(client)
items = catalog_api.list_catalog_items()
```

#### JavaScript/TypeScript Client

```bash
# Generate JavaScript client
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g typescript-axios \
  -o ./typescript-client \
  --additional-properties=npmName=vra-api-client

# Install dependencies
cd typescript-client
npm install
npm run build
```

TypeScript usage:
```typescript
import { Configuration, CatalogApi } from 'vra-api-client';

// Configure client
const config = new Configuration({
  basePath: 'http://localhost:8000'
});

// Use API
const catalogApi = new CatalogApi(config);
const items = await catalogApi.listCatalogItems();
```

#### Go Client

```bash
# Generate Go client
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g go \
  -o ./go-client \
  --additional-properties=packageName=vraclient,moduleName=github.com/company/vra-client

cd go-client
go mod tidy
```

Go usage:
```go
package main

import (
    "context"
    "fmt"
    vraclient "github.com/company/vra-client"
)

func main() {
    config := vraclient.NewConfiguration()
    config.Host = "localhost:8000"
    config.Scheme = "http"
    
    client := vraclient.NewAPIClient(config)
    
    items, _, err := client.CatalogApi.ListCatalogItems(context.Background()).Execute()
    if err != nil {
        fmt.Printf("Error: %v\n", err)
        return
    }
    
    fmt.Printf("Found %d catalog items\n", len(items.Items))
}
```

### Custom Templates

Create custom code generation templates:

```bash
# Get default templates
openapi-generator-cli author template -g python -o ./custom-templates

# Modify templates as needed
# Then use custom templates
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g python \
  -t ./custom-templates \
  -o ./custom-client
```

## API Testing

### Postman Collection

Generate Postman collection from OpenAPI spec:

```bash
# Using openapi-to-postman
npm install -g openapi-to-postman

# Convert OpenAPI to Postman
openapi2postmanv2 \
  -s http://localhost:8000/openapi.json \
  -o vra-api-collection.json \
  -p

# Import the collection file into Postman
```

### Insomnia Workspace

Import OpenAPI spec directly into Insomnia:

1. Open Insomnia
2. Create new workspace
3. Import from URL: `http://localhost:8000/openapi.json`
4. All endpoints will be automatically configured

### Newman Testing

Automate API testing with Newman:

```bash
# Install Newman
npm install -g newman

# Run collection
newman run vra-api-collection.json \
  --environment vra-api-environment.json \
  --reporters cli,htmlextra \
  --reporter-htmlextra-export ./test-results.html
```

## Documentation Customization

### Custom OpenAPI Metadata

Customize the OpenAPI specification:

```python
from fastapi import FastAPI

app = FastAPI(
    title="Custom VMware vRA API",
    description="Enhanced API with custom features",
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "api-support@company.com",
        "url": "https://support.company.com"
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html"
    },
    servers=[
        {"url": "https://api.company.com", "description": "Production"},
        {"url": "https://staging-api.company.com", "description": "Staging"}
    ]
)
```

### Custom Swagger UI

Customize the Swagger UI appearance:

```python
from fastapi.openapi.docs import get_swagger_ui_html

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Custom vRA API Documentation",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4.15.5/swagger-ui.css",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4.15.5/swagger-ui-bundle.js",
        swagger_favicon_url="/static/favicon.ico"
    )
```

### Documentation Themes

Apply custom themes to documentation:

```html
<!-- Custom CSS for Swagger UI -->
<style>
.swagger-ui .topbar {
    background-color: #1e3a8a;
}

.swagger-ui .topbar .download-url-wrapper .select-label {
    color: white;
}

.swagger-ui .info .title {
    color: #1e3a8a;
}
</style>
```

## Validation and Testing

### Schema Validation

Validate requests and responses against OpenAPI schema:

```python
import jsonschema
import yaml

# Load OpenAPI spec
with open('openapi.yaml') as f:
    openapi_spec = yaml.safe_load(f)

# Extract schema
catalog_item_schema = openapi_spec['components']['schemas']['CatalogItem']

# Validate data
def validate_catalog_item(data):
    try:
        jsonschema.validate(data, catalog_item_schema)
        return True
    except jsonschema.ValidationError as e:
        print(f"Validation error: {e}")
        return False
```

### Contract Testing

Use the OpenAPI spec for contract testing:

```python
import pytest
import requests
from openapi_spec_validator import validate_spec

def test_openapi_spec_valid():
    """Test that OpenAPI spec is valid"""
    spec = requests.get('http://localhost:8000/openapi.json').json()
    validate_spec(spec)  # Raises exception if invalid

def test_endpoints_match_spec():
    """Test that actual endpoints match OpenAPI spec"""
    spec = requests.get('http://localhost:8000/openapi.json').json()
    
    for path, methods in spec['paths'].items():
        for method in methods.keys():
            if method in ['get', 'post', 'put', 'delete']:
                # Test that endpoint exists and returns expected format
                response = requests.request(method, f'http://localhost:8000{path}')
                # Validate response against schema
```

## Monitoring and Analytics

### API Usage Analytics

Track API usage through OpenAPI metadata:

```python
from prometheus_client import Counter, Histogram, start_http_server

# Metrics
api_requests = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
api_duration = Histogram('api_request_duration_seconds', 'API request duration')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # Record metrics
    api_requests.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    api_duration.observe(duration)
    
    return response
```

### Documentation Analytics

Track documentation usage:

```html
<!-- Add analytics to Swagger UI -->
<script>
// Google Analytics for API docs
gtag('config', 'GA_TRACKING_ID', {
  custom_map: {'custom_parameter_1': 'api_endpoint'}
});

// Track API endpoint interactions
document.addEventListener('click', function(e) {
  if (e.target.matches('.opblock-summary')) {
    gtag('event', 'api_endpoint_click', {
      'custom_parameter_1': e.target.textContent.trim()
    });
  }
});
</script>
```

## Best Practices

### Documentation
1. **Keep specs updated**: Automatically sync with code changes
2. **Provide examples**: Include realistic request/response examples
3. **Use descriptions**: Add meaningful descriptions for all endpoints
4. **Version your API**: Use semantic versioning for API changes

### Code Generation
1. **Validate generated code**: Test generated clients thoroughly
2. **Customize templates**: Adapt to your coding standards
3. **Handle breaking changes**: Version client libraries appropriately
4. **Automate generation**: Include in CI/CD pipelines

### Testing
1. **Contract testing**: Validate API against specification
2. **Schema validation**: Ensure data consistency
3. **Performance testing**: Monitor API response times
4. **Security testing**: Validate authentication and authorization

---

For more information:
- [Authentication Configuration](authentication.md)
- [Integration Examples](examples.md)
- [REST API Setup](setup.md)
- [Complete API Reference](../rest-api-comprehensive.md)