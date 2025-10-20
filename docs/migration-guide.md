# Migration Guide

This guide helps you migrate between different interfaces of the VMware vRA toolkit: CLI, MCP Server, and REST API.

## Interface Overview

| Interface | Best For | Protocol | Integration |
|-----------|----------|----------|-------------|
| **CLI** | Manual operations, scripts, automation | Command line | Shell scripts, CI/CD |
| **MCP Server** | AI assistants, LLM integration | JSON-RPC over stdio | Claude, VS Code, custom AI |
| **REST API** | Web applications, HTTP clients | HTTP REST | Web apps, APIs, dashboards |

## Migration Scenarios

### 1. CLI to MCP Server

**Use Case**: Adding AI assistant capabilities to existing CLI workflows.

#### Before (CLI)
```bash
# Manual CLI operations
vra auth login --username admin --url https://vra.company.com
vra catalog list --project-id dev-project --page-size 50
vra catalog request blueprint-ubuntu --project-id dev-project --name "test-vm"
vra deployment list --status CREATE_SUCCESSFUL
```

#### After (MCP Server)
```python
# AI-driven operations via MCP client
with VRAMCPClient() as client:
    client.initialize()
    
    # AI assistant can now perform these operations
    auth_status = client.call_tool("vra_auth_status", {})
    catalog_items = client.call_tool("vra_list_catalog_items", {
        "project_id": "dev-project",
        "page_size": 50
    })
    deployment = client.call_tool("vra_request_catalog_item", {
        "catalog_item_id": "blueprint-ubuntu",
        "project_id": "dev-project",
        "name": "test-vm"
    })
    deployments = client.call_tool("vra_list_deployments", {
        "status": "CREATE_SUCCESSFUL"
    })
```

#### Migration Steps
1. **Install MCP server**: Same installation as CLI
2. **Configure AI assistant**: Add MCP server to Claude Desktop, VS Code Continue, etc.
3. **Convert scripts**: Transform bash/shell scripts into AI prompts
4. **Test workflows**: Verify AI assistant can perform required operations

**Benefits of Migration:**
- Natural language interface
- Context-aware operations
- Automated decision-making
- Integration with existing AI workflows

### 2. CLI to REST API

**Use Case**: Integrating vRA operations into web applications or HTTP-based systems.

#### Before (CLI)
```bash
#!/bin/bash
# Script for web application backend
vra auth status > /tmp/auth_status.json
vra catalog list --format json > /tmp/catalog.json
vra deployment list --project-id "$PROJECT_ID" --format json > /tmp/deployments.json
```

#### After (REST API)
```python
# Python web application integration
import requests

class VRAService:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def authenticate(self, username, password, url):
        response = self.session.post(f"{self.base_url}/auth/login", json={
            "username": username,
            "password": password,
            "url": url
        })
        return response.json()
    
    def get_catalog_items(self, project_id=None):
        params = {"project_id": project_id} if project_id else {}
        response = self.session.get(f"{self.base_url}/catalog/items", params=params)
        return response.json()
    
    def get_deployments(self, project_id=None):
        params = {"project_id": project_id} if project_id else {}
        response = self.session.get(f"{self.base_url}/deployments", params=params)
        return response.json()

# Usage in web framework (Flask, FastAPI, Django)
vra_service = VRAService()
catalog_items = vra_service.get_catalog_items(project_id="dev-project")
```

#### Migration Steps
1. **Start REST server**: `vra-rest-server`
2. **Replace CLI calls**: Convert shell commands to HTTP requests
3. **Update authentication**: Use `/auth/login` endpoint instead of CLI auth
4. **Handle responses**: Process JSON responses instead of CLI output
5. **Add error handling**: Implement HTTP error handling

**Benefits of Migration:**
- Web application integration
- Concurrent request handling
- Standard HTTP patterns
- Better error responses
- OpenAPI documentation

### 3. MCP Server to REST API

**Use Case**: Converting AI assistant integration to web application backend.

#### Before (MCP Server)
```python
# MCP client for AI assistant
def get_infrastructure_status():
    with VRAMCPClient() as client:
        client.initialize()
        
        auth = client.call_tool("vra_auth_status", {})
        deployments = client.call_tool("vra_list_deployments", {"page_size": 100})
        timeline = client.call_tool("vra_report_activity_timeline", {"days_back": 30})
        
        return {
            "auth": auth,
            "deployments": deployments,
            "timeline": timeline
        }
```

#### After (REST API)
```javascript
// JavaScript web application
class InfrastructureService {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    async getInfrastructureStatus() {
        const [auth, deployments, timeline] = await Promise.all([
            fetch(`${this.baseUrl}/auth/status`),
            fetch(`${this.baseUrl}/deployments?page_size=100`),
            fetch(`${this.baseUrl}/reports/activity-timeline?days_back=30`)
        ]);
        
        return {
            auth: await auth.json(),
            deployments: await deployments.json(),
            timeline: await timeline.json()
        };
    }
}
```

#### Migration Steps
1. **Map MCP tools to REST endpoints**: See [conversion table](#mcp-to-rest-conversion)
2. **Replace tool calls**: Convert MCP tool calls to HTTP requests
3. **Update response handling**: Process HTTP responses instead of MCP responses
4. **Implement web UI**: Build dashboard/interface for the functionality
5. **Add authentication**: Implement web-based authentication flow

### 4. REST API to CLI

**Use Case**: Converting web application functionality back to command-line tools for automation.

#### Before (REST API)
```bash
# HTTP requests via curl
curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"pass","url":"https://vra.com"}'

curl http://localhost:8000/catalog/items?project_id=dev-project
curl http://localhost:8000/deployments?status=CREATE_SUCCESSFUL
```

#### After (CLI)
```bash
# Direct CLI commands
vra auth login --username admin --url https://vra.com
vra catalog list --project-id dev-project  
vra deployment list --status CREATE_SUCCESSFUL
```

#### Migration Benefits
- Simpler authentication (stored credentials)
- Better output formatting for human reading
- Integration with shell scripting
- Reduced network overhead

## Conversion Tables

### MCP to REST Conversion

| MCP Tool | REST Endpoint | Method |
|----------|---------------|---------|
| `vra_auth_login` | `/auth/login` | POST |
| `vra_auth_logout` | `/auth/logout` | POST |
| `vra_auth_status` | `/auth/status` | GET |
| `vra_auth_refresh` | `/auth/refresh` | POST |
| `vra_list_catalog_items` | `/catalog/items` | GET |
| `vra_get_catalog_item` | `/catalog/items/{item_id}` | GET |
| `vra_get_catalog_item_schema` | `/catalog/items/{item_id}/schema` | GET |
| `vra_request_catalog_item` | `/catalog/items/{item_id}/request` | POST |
| `vra_list_deployments` | `/deployments` | GET |
| `vra_get_deployment` | `/deployments/{deployment_id}` | GET |
| `vra_delete_deployment` | `/deployments/{deployment_id}` | DELETE |
| `vra_get_deployment_resources` | `/deployments/{deployment_id}/resources` | GET |
| `vra_report_activity_timeline` | `/reports/activity-timeline` | GET |
| `vra_report_catalog_usage` | `/reports/catalog-usage` | GET |
| `vra_report_resources_usage` | `/reports/resources-usage` | GET |
| `vra_report_unsync` | `/reports/unsync` | GET |
| `vra_list_workflows` | `/workflows` | GET |
| `vra_get_workflow_schema` | `/workflows/{workflow_id}` | GET |
| `vra_run_workflow` | `/workflows/{workflow_id}/run` | POST |
| `vra_get_workflow_run` | `/workflows/{workflow_id}/executions/{execution_id}` | GET |
| `vra_cancel_workflow_run` | `/workflows/{workflow_id}/executions/{execution_id}/cancel` | PUT |

### CLI to REST Conversion

| CLI Command | REST Endpoint | Method |
|-------------|---------------|---------|
| `vra auth login` | `/auth/login` | POST |
| `vra auth logout` | `/auth/logout` | POST |
| `vra auth status` | `/auth/status` | GET |
| `vra catalog list` | `/catalog/items` | GET |
| `vra catalog get` | `/catalog/items/{item_id}` | GET |
| `vra catalog schema` | `/catalog/items/{item_id}/schema` | GET |
| `vra catalog request` | `/catalog/items/{item_id}/request` | POST |
| `vra deployment list` | `/deployments` | GET |
| `vra deployment get` | `/deployments/{deployment_id}` | GET |
| `vra deployment delete` | `/deployments/{deployment_id}` | DELETE |
| `vra deployment resources` | `/deployments/{deployment_id}/resources` | GET |
| `vra report activity-timeline` | `/reports/activity-timeline` | GET |
| `vra report catalog-usage` | `/reports/catalog-usage` | GET |
| `vra report resources-usage` | `/reports/resources-usage` | GET |
| `vra report unsync` | `/reports/unsync` | GET |
| `vra workflow list` | `/workflows` | GET |
| `vra workflow get-schema` | `/workflows/{workflow_id}` | GET |
| `vra workflow run` | `/workflows/{workflow_id}/run` | POST |

## Feature Parity Matrix

| Feature | CLI | MCP Server | REST API | Notes |
|---------|-----|------------|----------|-------|
| **Authentication** | ✅ | ✅ | ✅ | All support secure token storage |
| **Catalog Management** | ✅ | ✅ | ✅ | Full CRUD operations |
| **Deployment Operations** | ✅ | ✅ | ✅ | Create, read, update, delete |
| **Advanced Reporting** | ✅ | ✅ | ✅ | Analytics and insights |
| **Workflow Management** | ✅ | ✅ | ✅ | vRO workflow integration |
| **Tag Management** | ✅ | ✅ | ❌ | CLI and MCP only |
| **Export Functions** | ✅ | ✅ | ❌ | CLI and MCP only |
| **Interactive Output** | ✅ | ❌ | ❌ | CLI rich output only |
| **Natural Language** | ❌ | ✅ | ❌ | MCP with AI assistants only |
| **Web Integration** | ❌ | ❌ | ✅ | REST API only |
| **Concurrent Operations** | ❌ | Limited | ✅ | REST API best for concurrency |
| **Offline Capability** | ✅ | ❌ | ❌ | CLI only (cached data) |

## Migration Best Practices

### 1. Gradual Migration

Start with non-critical operations:
```bash
# Phase 1: Migrate read-only operations
# CLI: vra catalog list
# REST: GET /catalog/items

# Phase 2: Migrate simple write operations  
# CLI: vra catalog request
# REST: POST /catalog/items/{item_id}/request

# Phase 3: Migrate complex workflows
# Advanced reporting, multi-step operations
```

### 2. Parallel Running

Run multiple interfaces simultaneously during migration:
```bash
# Keep CLI for emergency operations
vra auth login --username admin --url https://vra.com

# Use REST API for application integration
curl -X GET http://localhost:8000/auth/status

# Add MCP for AI assistance
# Configure Claude Desktop with MCP server
```

### 3. Data Consistency

Ensure consistent authentication across interfaces:
```python
# Share authentication tokens
def sync_authentication():
    # CLI stores token in keyring
    cli_auth = get_cli_token()
    
    # REST server uses same token
    rest_headers = {"Authorization": f"Bearer {cli_auth}"}
    
    # MCP server accesses same keyring
    mcp_auth = get_keyring_token()
```

### 4. Error Handling

Map error handling between interfaces:
```python
# CLI error handling
try:
    result = subprocess.run(['vra', 'catalog', 'list'], 
                          capture_output=True, check=True)
except subprocess.CalledProcessError as e:
    handle_cli_error(e.returncode, e.stderr)

# REST API error handling  
try:
    response = requests.get('/catalog/items')
    response.raise_for_status()
except requests.HTTPError as e:
    handle_http_error(e.response.status_code, e.response.json())

# MCP error handling
response = client.call_tool("vra_list_catalog_items", {})
if "error" in response:
    handle_mcp_error(response["error"])
```

### 5. Testing Strategy

Test all interfaces during migration:
```python
def test_catalog_operations():
    # Test CLI
    cli_result = run_cli_command(['vra', 'catalog', 'list'])
    
    # Test REST API
    rest_result = requests.get('/catalog/items').json()
    
    # Test MCP
    mcp_result = client.call_tool("vra_list_catalog_items", {})
    
    # Verify consistent results
    assert_equivalent_data(cli_result, rest_result, mcp_result)
```

## Common Migration Issues

### 1. Authentication Differences

**Issue**: Different authentication flows between interfaces.

**Solution**:
```python
# Unified authentication service
class UnifiedAuth:
    def __init__(self):
        self.token_store = KeyringTokenStore()
    
    def authenticate_cli(self, username, password, url):
        # CLI authentication
        return self.token_store.store_token(username, url, token)
    
    def authenticate_rest(self, credentials):
        # REST authentication  
        return self.token_store.get_token_for_api()
    
    def authenticate_mcp(self):
        # MCP uses stored token
        return self.token_store.get_current_token()
```

### 2. Data Format Differences

**Issue**: Different output formats (CLI text, REST JSON, MCP structured).

**Solution**:
```python
# Data normalization layer
class DataNormalizer:
    def normalize_catalog_item(self, data, source_format):
        if source_format == 'cli':
            return self.parse_cli_output(data)
        elif source_format == 'rest':
            return self.parse_rest_response(data)
        elif source_format == 'mcp':
            return self.parse_mcp_response(data)
        
        return standardized_format
```

### 3. Error Handling Inconsistencies

**Issue**: Different error formats and codes.

**Solution**:
```python
# Unified error handling
class UnifiedErrorHandler:
    def handle_error(self, error, source):
        if source == 'cli':
            return self.map_cli_error(error)
        elif source == 'rest':
            return self.map_http_error(error)
        elif source == 'mcp':
            return self.map_mcp_error(error)
        
        return StandardError(message, code, details)
```

## Performance Considerations

### Interface Performance Comparison

| Operation | CLI | MCP Server | REST API | Notes |
|-----------|-----|------------|----------|-------|
| **Startup Time** | Fast | Medium | Slow | CLI fastest, REST server startup |
| **Single Request** | Medium | Medium | Fast | HTTP optimized |
| **Bulk Operations** | Fast | Medium | Fast | CLI batch mode, REST concurrent |
| **Memory Usage** | Low | Medium | High | Server processes |
| **Network Overhead** | None | Low | Medium | Local vs HTTP |

### Optimization Strategies

1. **Use appropriate interface for use case**:
   - CLI: Scripts and automation
   - MCP: AI-driven operations  
   - REST: Web applications

2. **Implement caching**: Share cached data between interfaces

3. **Connection pooling**: For REST API and MCP connections

4. **Batch operations**: Where supported by the interface

## Migration Checklist

### Pre-Migration
- [ ] Inventory current CLI usage
- [ ] Identify target interface (MCP/REST)
- [ ] Plan migration phases
- [ ] Set up test environment

### During Migration  
- [ ] Install target interface
- [ ] Configure authentication
- [ ] Convert operations gradually
- [ ] Test functionality parity
- [ ] Monitor performance
- [ ] Update documentation

### Post-Migration
- [ ] Validate all operations work
- [ ] Update CI/CD pipelines
- [ ] Train team on new interface
- [ ] Monitor system health
- [ ] Plan CLI deprecation (if applicable)

## Support and Resources

- **CLI Reference**: [CLI Reference Guide](user-guide/cli-reference.md)
- **MCP Documentation**: [MCP Server Guide](mcp-server.md)
- **REST API Documentation**: [REST API Reference](rest-api-comprehensive.md)
- **Examples**: Check the `examples/` directory for migration examples
- **Community**: GitHub Discussions for migration questions

---

Need help with migration? Open an issue on [GitHub](https://github.com/brunseba/tools-vmware-vra-cli/issues) with the `migration` label.