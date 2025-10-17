# VMware vRA MCP Server

The VMware vRA MCP Server provides a **Model Context Protocol (MCP) compliant** interface for LLM integration with VMware vRealize Automation. This server follows the official [MCP specification 2025-06-18](https://modelcontextprotocol.io/specification/2025-06-18) and enables AI assistants and language models to interact with vRA infrastructure.

!!! success "MCP Compliance"
    This server is fully compliant with the Model Context Protocol specification and can be used with any MCP-compatible client or LLM framework.

## Table of Contents

- [Quick Start](#quick-start)
- [MCP Protocol Features](#mcp-protocol-features)
- [Available Tools](#available-tools)
- [Available Resources](#available-resources)
- [Integration Examples](#integration-examples)
- [Transport Options](#transport-options)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Starting the MCP Server

The MCP server uses JSON-RPC 2.0 over standard I/O (stdio) as the primary transport:

```bash
# Start MCP server with stdio transport (default)
vra-mcp-server

# Explicitly specify stdio transport
vra-mcp-server --transport stdio
```

### Testing the MCP Server

You can test the server using any MCP client. Here's a simple test using a hypothetical MCP client:

```python
import asyncio
from mcp.client import McpClient

async def test_vra_mcp():
    # Connect to the MCP server
    client = McpClient()
    await client.connect_stdio("vra-mcp-server")
    
    # Initialize the connection
    await client.initialize({
        "clientInfo": {
            "name": "test-client",
            "version": "1.0.0"
        },
        "capabilities": {
            "tools": {}
        }
    })
    
    # List available tools
    tools = await client.list_tools()
    print("Available tools:", [tool["name"] for tool in tools["tools"]])
    
    # Use a tool
    result = await client.call_tool("vra_authenticate", {
        "username": "admin",
        "password": "password", 
        "url": "https://vra.company.com"
    })
    print("Authentication result:", result)
    
    await client.disconnect()

# Run the test
asyncio.run(test_vra_mcp())
```

## MCP Protocol Features

### Supported Capabilities

| Capability | Status | Description |
|------------|--------|-------------|
| **Tools** | ✅ **Supported** | Execute vRA operations as MCP tools |
| **Resources** | ✅ **Supported** | Access vRA data as MCP resources with subscription |
| **Prompts** | ❌ **Not Implemented** | Planned for future release |
| **Logging** | ✅ **Supported** | Server-side logging capability |

### Protocol Compliance

- ✅ **JSON-RPC 2.0**: Full compliance with JSON-RPC 2.0 specification
- ✅ **MCP Protocol Version**: 2025-06-18
- ✅ **Initialization Handshake**: Proper capability negotiation
- ✅ **Error Handling**: Standard JSON-RPC and MCP error codes
- ✅ **Message Validation**: Pydantic-based message validation

## Available Tools

The MCP server provides the following tools for vRA operations:

### Authentication Tools

#### `vra_authenticate`
Authenticate to VMware vRA server and store credentials.

**Parameters:**
- `username` (string, required): vRA username
- `password` (string, required): vRA password
- `url` (string, required): vRA server URL
- `tenant` (string, optional): vRA tenant
- `domain` (string, optional): vRA domain

**Example:**
```json
{
  "name": "vra_authenticate",
  "arguments": {
    "username": "admin",
    "password": "password",
    "url": "https://vra.company.com",
    "tenant": "vsphere.local"
  }
}
```

### Catalog Tools

#### `vra_list_catalog_items`
List available catalog items from the vRA service catalog.

**Parameters:**
- `project_id` (string, optional): Filter by project ID
- `page_size` (integer, optional): Number of items per page (default: 100)
- `first_page_only` (boolean, optional): Fetch only first page (default: false)

#### `vra_get_catalog_item`
Get details of a specific catalog item.

**Parameters:**
- `item_id` (string, required): Catalog item ID

#### `vra_get_catalog_item_schema`
Get the request schema for a catalog item.

**Parameters:**
- `item_id` (string, required): Catalog item ID

#### `vra_request_catalog_item`
Request a catalog item deployment.

**Parameters:**
- `item_id` (string, required): Catalog item ID
- `project_id` (string, required): Project ID
- `inputs` (object, optional): Input parameters for the catalog item
- `reason` (string, optional): Reason for the request
- `name` (string, optional): Deployment name

### Deployment Tools

#### `vra_list_deployments`
List vRA deployments.

**Parameters:**
- `project_id` (string, optional): Filter by project ID
- `status` (string, optional): Filter by status
- `page_size` (integer, optional): Number of items per page (default: 100)
- `first_page_only` (boolean, optional): Fetch only first page (default: false)

#### `vra_get_deployment`
Get details of a specific deployment.

**Parameters:**
- `deployment_id` (string, required): Deployment ID

#### `vra_get_deployment_resources`
Get resources of a specific deployment.

**Parameters:**
- `deployment_id` (string, required): Deployment ID

#### `vra_delete_deployment`
Delete a deployment.

**Parameters:**
- `deployment_id` (string, required): Deployment ID
- `confirm` (boolean, optional): Confirm deletion (default: true)

### Schema Catalog Tools (NEW!)

Advanced schema-driven catalog operations with persistent cache support.

#### `vra_schema_load_schemas`
Load catalog schemas from JSON files into persistent cache.

**Parameters:**
- `pattern` (string, optional): File pattern to match schema files (default: "*_schema.json")
- `force_reload` (boolean, optional): Force reload even if already loaded (default: false)

#### `vra_schema_list_schemas`
List available catalog schemas from cache.

**Parameters:**
- `item_type` (string, optional): Filter by catalog item type
- `name_filter` (string, optional): Filter by name (case-insensitive substring match)

#### `vra_schema_search_schemas`
Search catalog schemas by name or description.

**Parameters:**
- `query` (string, required): Search query (case-insensitive)

#### `vra_schema_show_schema`
Show detailed schema information for a catalog item.

**Parameters:**
- `catalog_item_id` (string, required): Catalog item ID

#### `vra_schema_execute_schema`
Execute a catalog item using its schema with AI-guided input collection.

**Parameters:**
- `catalog_item_id` (string, required): Catalog item ID
- `project_id` (string, required): vRA project ID
- `deployment_name` (string, optional): Custom deployment name
- `inputs` (object, optional): Input values dictionary
- `dry_run` (boolean, optional): Validate inputs without executing (default: false)

**Example:**
```json
{
  "name": "vra_schema_execute_schema",
  "arguments": {
    "catalog_item_id": "99abceaf-1da3-3fad-aae7-b55b5084112e",
    "project_id": "dev-project",
    "inputs": {
      "vmName": "web-server-001",
      "vCPUSize": 4,
      "vRAMSize": 8,
      "region": "MOP"
    },
    "dry_run": false
  }
}
```

#### `vra_schema_generate_template`
Generate input template for a catalog item.

**Parameters:**
- `catalog_item_id` (string, required): Catalog item ID
- `project_id` (string, required): vRA project ID

#### `vra_schema_clear_cache`
Clear the persistent schema registry cache.

**Parameters:** None

#### `vra_schema_registry_status`
Show schema registry status and statistics.

**Parameters:** None

## Available Resources

The MCP server exposes the following resources:

### `vra://catalog/items`
**Name:** VMware vRA Catalog Items  
**Description:** Access to vRA service catalog items  
**MIME Type:** application/json

Returns the current list of catalog items as JSON data.

### `vra://deployments`  
**Name:** VMware vRA Deployments  
**Description:** Access to vRA deployments  
**MIME Type:** application/json

Returns the current list of deployments as JSON data.

### `vra://config`
**Name:** VMware vRA Configuration  
**Description:** Current vRA server configuration  
**MIME Type:** application/json

Returns the current vRA server configuration (sensitive data excluded).

## Integration Examples

### Claude Desktop Integration

Add this to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "vmware-vra": {
      "command": "vra-mcp-server",
      "env": {
        "VRA_URL": "https://vra.company.com",
        "VRA_TENANT": "vsphere.local"
      }
    }
  }
}
```

### VS Code with Continue Integration

```json
{
  "mcp": {
    "servers": [
      {
        "name": "vmware-vra",
        "command": ["vra-mcp-server", "--transport", "stdio"]
      }
    ]
  }
}
```

### Python MCP Client

```python
import asyncio
import json
from mcp.client import McpClient

class VraMcpClient:
    def __init__(self):
        self.client = None
    
    async def connect(self):
        self.client = McpClient()
        await self.client.connect_stdio("vra-mcp-server")
        
        # Initialize connection
        init_result = await self.client.initialize({
            "clientInfo": {
                "name": "python-vra-client",
                "version": "1.0.0"
            },
            "capabilities": {
                "tools": {}
            }
        })
        print("Connected to MCP server:", init_result["serverInfo"]["name"])
    
    async def authenticate(self, username, password, url, tenant=None):
        result = await self.client.call_tool("vra_authenticate", {
            "username": username,
            "password": password,
            "url": url,
            "tenant": tenant
        })
        return result
    
    async def list_catalog_items(self, project_id=None):
        result = await self.client.call_tool("vra_list_catalog_items", {
            "project_id": project_id,
            "page_size": 50
        })
        return result
    
    async def request_vm(self, item_id, project_id, hostname, cpu=2, memory="4GB"):
        result = await self.client.call_tool("vra_request_catalog_item", {
            "item_id": item_id,
            "project_id": project_id,
            "inputs": {
                "hostname": hostname,
                "cpu": cpu,
                "memory": memory
            },
            "reason": "Requested via MCP"
        })
        return result
    
    async def disconnect(self):
        if self.client:
            await self.client.disconnect()

# Usage example
async def main():
    client = VraMcpClient()
    
    try:
        await client.connect()
        
        # Authenticate
        auth_result = await client.authenticate(
            "admin", "password", "https://vra.company.com", "vsphere.local"
        )
        print("Authentication:", auth_result)
        
        # List catalog items
        items = await client.list_catalog_items("my-project-id")
        print("Catalog items:", len(items))
        
        # Request a VM (example)
        if items:
            first_item = items[0]  # Assuming items are parsed from result
            vm_result = await client.request_vm(
                first_item["id"], 
                "my-project-id", 
                "test-vm-01"
            )
            print("VM request:", vm_result)
        
    finally:
        await client.disconnect()

asyncio.run(main())
```

## Transport Options

### Standard I/O (stdio)
**Default transport** - JSON-RPC 2.0 over stdin/stdout

```bash
vra-mcp-server --transport stdio
```

This is the standard MCP transport and works with most MCP clients including:
- Claude Desktop
- VS Code with Continue
- Custom MCP clients

### Future Transport Options

Additional transports may be added in future releases:
- WebSocket transport
- HTTP transport
- Named pipes (Windows)
- Unix domain sockets (Unix/Linux)

## Error Handling

The MCP server follows standard JSON-RPC 2.0 error handling:

### JSON-RPC Error Codes
- `-32700`: Parse error - Invalid JSON received
- `-32600`: Invalid request - JSON-RPC request is invalid
- `-32601`: Method not found - Requested method doesn't exist
- `-32602`: Invalid params - Invalid method parameters
- `-32603`: Internal error - Server internal error

### MCP-Specific Error Codes
- `-32000`: Invalid tool - Tool name not recognized
- `-32001`: Invalid resource - Resource URI not found
- `-32003`: Resource not found - Requested resource unavailable
- `-32004`: Tool execution error - Tool failed to execute

### Error Response Example

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32004,
    "message": "Tool execution error: Authentication failed",
    "data": {
      "tool": "vra_authenticate",
      "details": "Invalid credentials provided"
    }
  }
}
```

## Message Flow Examples

### Initialization Sequence

1. **Client sends initialize request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-06-18",
    "capabilities": {
      "tools": {}
    },
    "clientInfo": {
      "name": "my-client",
      "version": "1.0.0"
    }
  }
}
```

2. **Server responds with capabilities:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-06-18",
    "capabilities": {
      "tools": {},
      "resources": {"subscribe": true},
      "logging": {}
    },
    "serverInfo": {
      "name": "vmware-vra-mcp-server",
      "version": "0.11.0"
    }
  }
}
```

3. **Client sends initialized notification:**
```json
{
  "jsonrpc": "2.0",
  "method": "initialized"
}
```

### Tool Execution

1. **List available tools:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list"
}
```

2. **Execute a tool:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "vra_authenticate",
    "arguments": {
      "username": "admin",
      "password": "password",
      "url": "https://vra.company.com"
    }
  }
}
```

## Troubleshooting

### Common Issues

#### 1. Authentication Failures
**Symptom**: Tools return "Not authenticated" errors
**Solution**: First run `vra_authenticate` tool with valid credentials

#### 2. Connection Issues
**Symptom**: Client cannot connect to MCP server
**Solution**: Ensure `vra-mcp-server` is in PATH and executable

#### 3. Tool Execution Errors
**Symptom**: Tools fail with internal errors
**Solution**: Check server logs (stderr) for detailed error messages

#### 4. Resource Access Issues
**Symptom**: Resources return empty or error content
**Solution**: Ensure authentication is complete and vRA server is accessible

### Debug Mode

Enable verbose logging by setting environment variable:

```bash
export VRA_VERBOSE=true
vra-mcp-server
```

### Testing Connection

Test basic connectivity:

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | vra-mcp-server
```

Expected response should include server capabilities and info.

## Architecture

### Component Overview

```
┌─────────────────┐    JSON-RPC 2.0    ┌──────────────────┐
│   MCP Client    │ ←─────stdio────────→ │  vra-mcp-server  │
│  (Claude, etc.) │                     │                  │
└─────────────────┘                     └──────────────────┘
                                                  │
                                                  │ Uses
                                                  ▼
                                        ┌──────────────────┐
                                        │ vmware-vra-cli   │
                                        │   Core Logic     │
                                        │                  │
                                        │ • Authentication │
                                        │ • API Clients    │
                                        │ • Configuration  │
                                        └──────────────────┘
                                                  │
                                                  │ REST API
                                                  ▼
                                        ┌──────────────────┐
                                        │  VMware vRA      │
                                        │     Server       │
                                        └──────────────────┘
```

### Protocol Stack

1. **Transport Layer**: stdio JSON-RPC 2.0
2. **Protocol Layer**: MCP specification compliance
3. **Handler Layer**: Tool and resource implementations
4. **Business Layer**: VMware vRA API integration
5. **Data Layer**: VMware vRA REST APIs

## Security Considerations

### Authentication
- Credentials are stored securely using system keyring
- Authentication tokens are automatically refreshed
- No plaintext credentials in memory longer than necessary

### Transport Security
- stdio transport is secure for local communication
- Consider authentication mechanisms for remote access scenarios
- Future transports will include TLS support

### Data Privacy
- Configuration resources exclude sensitive data
- Error messages avoid exposing internal details
- Tool responses limit sensitive information exposure

## Additional Examples

### Complete Deployment Workflow

```python
import asyncio
import json
from typing import Dict, Any

class VraDeploymentWorkflow:
    def __init__(self, mcp_client):
        self.client = mcp_client
    
    async def deploy_vm(self, vm_config: Dict[str, Any]):
        """Complete VM deployment workflow."""
        try:
            # 1. Authenticate
            auth_result = await self.client.call_tool("vra_authenticate", {
                "username": vm_config["username"],
                "password": vm_config["password"],
                "url": vm_config["vra_url"],
                "tenant": vm_config.get("tenant", "vsphere.local")
            })
            
            if auth_result["isError"]:
                raise Exception(f"Authentication failed: {auth_result['content'][0]['text']}")
            
            print("✅ Authentication successful")
            
            # 2. List catalog items to find VM template
            catalog_result = await self.client.call_tool("vra_list_catalog_items", {
                "project_id": vm_config["project_id"]
            })
            
            catalog_items = json.loads(catalog_result["content"][0]["text"])
            vm_template = next(
                (item for item in catalog_items if vm_config["template_name"] in item["name"]),
                None
            )
            
            if not vm_template:
                raise Exception(f"VM template '{vm_config['template_name']}' not found")
            
            print(f"✅ Found VM template: {vm_template['name']}")
            
            # 3. Get catalog item schema
            schema_result = await self.client.call_tool("vra_get_catalog_item_schema", {
                "item_id": vm_template["id"]
            })
            
            schema = json.loads(schema_result["content"][0]["text"])
            print(f"✅ Retrieved schema with {len(schema.get('properties', {}))} input parameters")
            
            # 4. Request catalog item
            deploy_result = await self.client.call_tool("vra_request_catalog_item", {
                "item_id": vm_template["id"],
                "project_id": vm_config["project_id"],
                "name": vm_config["deployment_name"],
                "inputs": vm_config["inputs"],
                "reason": "Deployed via MCP automation"
            })
            
            if deploy_result["isError"]:
                raise Exception(f"Deployment failed: {deploy_result['content'][0]['text']}")
            
            deployment_info = json.loads(deploy_result["content"][0]["text"])
            deployment_id = deployment_info["id"]
            
            print(f"✅ Deployment requested: {deployment_id}")
            
            # 5. Monitor deployment status
            await self.monitor_deployment(deployment_id)
            
            return deployment_id
            
        except Exception as e:
            print(f"❌ Deployment failed: {str(e)}")
            raise
    
    async def monitor_deployment(self, deployment_id: str, timeout: int = 600):
        """Monitor deployment progress."""
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check deployment status
            status_result = await self.client.call_tool("vra_get_deployment", {
                "deployment_id": deployment_id
            })
            
            deployment = json.loads(status_result["content"][0]["text"])
            status = deployment["status"]
            
            print(f"🔄 Deployment status: {status}")
            
            if status == "CREATE_SUCCESSFUL":
                print("✅ Deployment completed successfully")
                
                # Get resources
                resources_result = await self.client.call_tool("vra_get_deployment_resources", {
                    "deployment_id": deployment_id
                })
                
                resources = json.loads(resources_result["content"][0]["text"])
                print(f"📋 Deployment has {len(resources)} resources")
                
                for resource in resources:
                    print(f"  - {resource['name']} ({resource['type']})")
                
                return
            
            elif status in ["CREATE_FAILED", "DELETE_SUCCESSFUL", "DELETE_FAILED"]:
                raise Exception(f"Deployment failed with status: {status}")
            
            # Wait before next check
            await asyncio.sleep(30)
        
        raise Exception(f"Deployment timeout after {timeout} seconds")

# Usage example
async def main():
    # Assuming you have an MCP client instance
    workflow = VraDeploymentWorkflow(mcp_client)
    
    vm_config = {
        "username": "admin@corp.local",
        "password": "password123",
        "vra_url": "https://vra.example.com",
        "tenant": "corp.local",
        "project_id": "project-123",
        "template_name": "CentOS 8",
        "deployment_name": "my-test-vm",
        "inputs": {
            "cpu": 2,
            "memory": 4096,
            "disk_size": 50,
            "hostname": "test-vm-01",
            "network": "vlan-100"
        }
    }
    
    try:
        deployment_id = await workflow.deploy_vm(vm_config)
        print(f"🎉 VM deployed successfully: {deployment_id}")
    except Exception as e:
        print(f"💥 Deployment failed: {e}")
```

### Resource Monitoring Dashboard

```python
class VraResourceMonitor:
    def __init__(self, mcp_client):
        self.client = mcp_client
    
    async def get_dashboard_data(self):
        """Get comprehensive dashboard data."""
        # Read all resources
        catalog_resource = await self.client.read_resource("vra://catalog/items")
        deployments_resource = await self.client.read_resource("vra://deployments")
        config_resource = await self.client.read_resource("vra://config")
        
        # Parse data
        catalog_items = json.loads(catalog_resource["contents"][0]["text"])
        deployments = json.loads(deployments_resource["contents"][0]["text"])
        config = json.loads(config_resource["contents"][0]["text"])
        
        # Generate dashboard
        dashboard = {
            "server_info": {
                "url": config.get("api_url"),
                "tenant": config.get("tenant"),
                "connection_status": "connected"
            },
            "catalog_summary": {
                "total_items": len(catalog_items),
                "item_types": self._count_by_key(catalog_items, "type"),
                "popular_items": sorted(catalog_items, key=lambda x: x.get("usage_count", 0), reverse=True)[:5]
            },
            "deployment_summary": {
                "total_deployments": len(deployments),
                "status_breakdown": self._count_by_key(deployments, "status"),
                "recent_deployments": sorted(deployments, key=lambda x: x.get("created_at", ""), reverse=True)[:5]
            },
            "resource_utilization": await self._calculate_resource_usage(deployments)
        }
        
        return dashboard
    
    def _count_by_key(self, items, key):
        """Count items by a specific key."""
        counts = {}
        for item in items:
            value = item.get(key, "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts
    
    async def _calculate_resource_usage(self, deployments):
        """Calculate resource utilization across deployments."""
        total_cpu = 0
        total_memory = 0
        total_storage = 0
        
        for deployment in deployments:
            if deployment.get("status") == "CREATE_SUCCESSFUL":
                # Get deployment resources
                try:
                    resources_result = await self.client.call_tool("vra_get_deployment_resources", {
                        "deployment_id": deployment["id"]
                    })
                    
                    resources = json.loads(resources_result["content"][0]["text"])
                    
                    for resource in resources:
                        if resource.get("type") == "Cloud.vSphere.Machine":
                            props = resource.get("properties", {})
                            total_cpu += props.get("cpu", 0)
                            total_memory += props.get("memory", 0)
                            total_storage += props.get("storage", 0)
                            
                except Exception:
                    continue  # Skip on error
        
        return {
            "total_cpu_cores": total_cpu,
            "total_memory_mb": total_memory,
            "total_storage_gb": total_storage
        }
    
    async def print_dashboard(self):
        """Print a formatted dashboard."""
        data = await self.get_dashboard_data()
        
        print("═" * 60)
        print("🏢 VMware vRA Dashboard")
        print("═" * 60)
        
        # Server info
        server = data["server_info"]
        print(f"🌐 Server: {server['url']}")
        print(f"🏢 Tenant: {server['tenant']}")
        print(f"🔗 Status: {server['connection_status']}")
        print()
        
        # Catalog summary
        catalog = data["catalog_summary"]
        print("📋 Catalog Summary:")
        print(f"  Total Items: {catalog['total_items']}")
        print("  Item Types:")
        for item_type, count in catalog["item_types"].items():
            print(f"    - {item_type}: {count}")
        print()
        
        # Deployment summary
        deploy = data["deployment_summary"]
        print("🚀 Deployment Summary:")
        print(f"  Total Deployments: {deploy['total_deployments']}")
        print("  Status Breakdown:")
        for status, count in deploy["status_breakdown"].items():
            print(f"    - {status}: {count}")
        print()
        
        # Resource utilization
        resources = data["resource_utilization"]
        print("💻 Resource Utilization:")
        print(f"  CPU Cores: {resources['total_cpu_cores']}")
        print(f"  Memory: {resources['total_memory_mb']} MB")
        print(f"  Storage: {resources['total_storage_gb']} GB")
        
        print("═" * 60)
```

## Performance Optimization

### Connection Pooling

The MCP server automatically manages connections to vRA:

```python
# Connections are pooled per authentication session
# Multiple tool calls reuse the same authenticated session
# Sessions automatically refresh tokens when needed
```

### Pagination Best Practices

```python
# For large datasets, use pagination
await client.call_tool("vra_list_catalog_items", {
    "page_size": 50,  # Reasonable page size
    "first_page_only": False  # Get all pages if needed
})

# For quick overview, use first page only
await client.call_tool("vra_list_deployments", {
    "page_size": 20,
    "first_page_only": True  # Faster for dashboards
})
```

### Resource Caching

Resources are cached for optimal performance:

- **Catalog items**: 5 minutes
- **Deployments**: 2 minutes
- **Configuration**: 10 minutes

```python
# Subsequent calls within cache period return cached data
resource1 = await client.read_resource("vra://catalog/items")  # Cache miss
resource2 = await client.read_resource("vra://catalog/items")  # Cache hit
```

## Advanced Configuration

### Environment Variables

Set default values via environment variables:

```bash
# Default server settings
export VRA_URL="https://vra.company.com"
export VRA_TENANT="corp.local"
export VRA_VERIFY_SSL="false"  # For dev environments

# Debug settings
export VRA_DEBUG="true"
export VRA_VERBOSE="true"

# Performance settings
export VRA_CACHE_TTL="300"  # 5 minutes
export VRA_TIMEOUT="30"     # 30 seconds
```

### Configuration File

Customize via `~/.vmware-vra-cli/config.yaml`:

```yaml
# Server configuration
api_url: "https://vra.company.com"
tenant: "corp.local"
verify_ssl: true

# MCP server settings
mcp_server:
  cache_ttl: 300
  max_page_size: 100
  default_page_size: 20
  timeout: 30
  
# Logging configuration
logging:
  level: "INFO"
  file: "~/.vmware-vra-cli/mcp-server.log"
```

## Testing and Development

### Running Tests

```bash
# Run all MCP server tests
pytest tests/test_mcp_server.py -v

# Run specific test categories
pytest tests/test_mcp_server.py::TestVraMcpServer -v
pytest tests/test_mcp_server.py::TestVraToolsHandler -v
pytest tests/test_mcp_server.py::TestStdioTransport -v

# Run integration tests
pytest tests/test_mcp_server.py::TestMcpIntegration -v

# Generate coverage report
pytest tests/test_mcp_server.py --cov=src/vmware_vra_cli/mcp_server
```

### Mock Server for Testing

```python
import asyncio
from unittest.mock import AsyncMock, MagicMock
from vmware_vra_cli.mcp_server.server import VraMcpServer

class MockVraMcpServer(VraMcpServer):
    """Mock MCP server for testing."""
    
    def __init__(self):
        super().__init__()
        self._mock_catalog_items = [
            {"id": "item-1", "name": "CentOS 8", "type": "VM"},
            {"id": "item-2", "name": "Ubuntu 20.04", "type": "VM"}
        ]
        self._mock_deployments = [
            {"id": "deploy-1", "name": "test-vm", "status": "CREATE_SUCCESSFUL"}
        ]
    
    async def _handle_tools_call(self, params):
        """Override tool calls with mock responses."""
        name = params.get("name")
        arguments = params.get("arguments", {})
        
        if name == "vra_authenticate":
            return {
                "isError": False,
                "content": [{"type": "text", "text": "Authentication successful"}]
            }
        elif name == "vra_list_catalog_items":
            return {
                "isError": False,
                "content": [{"type": "text", "text": json.dumps(self._mock_catalog_items)}]
            }
        elif name == "vra_list_deployments":
            return {
                "isError": False,
                "content": [{"type": "text", "text": json.dumps(self._mock_deployments)}]
            }
        
        return await super()._handle_tools_call(params)

# Usage in tests
async def test_with_mock_server():
    server = MockVraMcpServer()
    
    # Initialize
    await server._handle_message({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {"tools": {}},
            "clientInfo": {"name": "test", "version": "1.0"}
        }
    })
    
    await server._handle_message({"jsonrpc": "2.0", "method": "initialized"})
    
    # Test tool call
    result = await server._handle_message({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "vra_list_catalog_items",
            "arguments": {}
        }
    })
    
    assert not result["result"]["isError"]
    print("Mock server test passed!")
```

## Deployment Strategies

### Container Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY src/ ./src/
COPY setup.py .

# Install application
RUN pip install -e .

# Create non-root user
RUN useradd -m mcpuser
USER mcpuser

# Expose MCP server
CMD ["vra-mcp-server"]
```

```bash
# Build and run container
docker build -t vra-mcp-server .
docker run -i vra-mcp-server
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vra-mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: vra-mcp-server
  template:
    metadata:
      labels:
        app: vra-mcp-server
    spec:
      containers:
      - name: mcp-server
        image: vra-mcp-server:latest
        env:
        - name: VRA_URL
          valueFrom:
            secretKeyRef:
              name: vra-config
              key: url
        - name: VRA_TENANT
          valueFrom:
            secretKeyRef:
              name: vra-config
              key: tenant
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
  name: vra-mcp-service
spec:
  selector:
    app: vra-mcp-server
  ports:
  - port: 8080
    targetPort: 8080
```

---

**Built with ❤️ for LLM-powered VMware infrastructure automation**
