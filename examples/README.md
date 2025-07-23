# VMware vRA MCP Server Examples

This directory contains practical examples and configuration files for integrating with the VMware vRA MCP Server.

## Files Overview

### Python Client Examples
- **`mcp_client_examples.py`** - Comprehensive Python examples showing various integration patterns

### Configuration Examples
- **`claude_desktop_config.json`** - Configuration for Claude Desktop integration
- **`continue_config.json`** - Configuration for VS Code Continue extension

## Python Client Examples

The `mcp_client_examples.py` file demonstrates:

1. **Basic Connection** - How to connect and list available tools/resources
2. **VM Deployment** - Complete workflow for deploying virtual machines
3. **Monitoring Dashboard** - Resource monitoring and status reporting
4. **Batch Operations** - Concurrent operations and error handling

### Running the Examples

```bash
# Run all examples
python examples/mcp_client_examples.py

# Run specific examples
python examples/mcp_client_examples.py "basic"
python examples/mcp_client_examples.py "deployment"
python examples/mcp_client_examples.py "dashboard"
python examples/mcp_client_examples.py "batch"
```

### Prerequisites

Before running the examples, ensure:

1. **MCP Server is installed**:
   ```bash
   pip install vmware-vra-cli
   # or from source
   uv sync
   ```

2. **MCP Server is in PATH**:
   ```bash
   which vra-mcp-server
   ```

3. **VMware vRA environment is accessible**:
   - vRA server URL
   - Valid credentials
   - Network connectivity

### Configuration

Update the configuration sections in the examples with your actual values:

```python
config = {
    "username": "your-username@domain.com",
    "password": "your-password",  # Use env vars in production!
    "url": "https://your-vra-server.com",
    "tenant": "your-tenant",
    "project_id": "your-project-id"
}
```

## Claude Desktop Integration

### Setup Instructions

1. **Install the MCP server**:
   ```bash
   pip install vmware-vra-cli
   ```

2. **Copy the configuration**:
   ```bash
   # macOS
   cp examples/claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
   
   # Windows
   copy examples\claude_desktop_config.json %APPDATA%\Claude\claude_desktop_config.json
   
   # Linux
   cp examples/claude_desktop_config.json ~/.config/claude/claude_desktop_config.json
   ```

3. **Update the configuration** with your vRA server details:
   ```json
   {
     "mcpServers": {
       "vmware-vra": {
         "command": "vra-mcp-server",
         "args": ["--transport", "stdio"],
         "env": {
           "VRA_URL": "https://your-vra-server.com",
           "VRA_TENANT": "your-tenant",
           "VRA_VERIFY_SSL": "true"
         }
       }
     }
   }
   ```

4. **Restart Claude Desktop**

### Usage with Claude

Once configured, you can interact with VMware vRA through Claude:

```
Hi Claude! Can you help me list the available catalog items in my vRA environment?
```

```
Please authenticate to vRA with the following details:
- Username: admin@corp.local
- Password: [your password]
- URL: https://vra.example.com
- Tenant: corp.local
```

```
Can you deploy a CentOS VM with 4 CPU cores and 8GB RAM in the "dev-project" project?
```

## VS Code Continue Integration

### Setup Instructions

1. **Install Continue extension** in VS Code

2. **Update Continue configuration**:
   - Open VS Code Settings (Cmd/Ctrl + ,)
   - Search for "Continue"
   - Click "Edit in settings.json"
   - Merge the content from `examples/continue_config.json`

3. **Update the MCP server configuration** with your details:
   ```json
   "experimental": {
     "mcp": {
       "servers": [
         {
           "name": "vmware-vra",
           "description": "VMware vRealize Automation integration",
           "command": ["vra-mcp-server", "--transport", "stdio"],
           "env": {
             "VRA_URL": "https://your-vra-server.com",
             "VRA_TENANT": "your-tenant"
           }
         }
       ]
     }
   }
   ```

4. **Restart VS Code**

### Usage with Continue

Use Continue's chat interface to interact with vRA:

```
@mcp vmware-vra authenticate to my vRA server and list current deployments
```

```
@mcp vmware-vra deploy a new Ubuntu VM with hostname "web-server-01"
```

## Example Workflows

### 1. Infrastructure Assessment

```python
# Connect and authenticate
client = VraWorkflowClient()
await client.connect()
await client.authenticate(username, password, url, tenant)

# Get overview
dashboard = await client.get_dashboard_summary()
print(f"Total deployments: {dashboard['total_deployments']}")
print(f"Available catalog items: {dashboard['catalog_items']}")
```

### 2. Automated VM Deployment

```python
# Deploy multiple VMs
vm_configs = [
    {"name": "web-01", "template": "Ubuntu 20.04", "cpu": 2, "memory": 4096},
    {"name": "web-02", "template": "Ubuntu 20.04", "cpu": 2, "memory": 4096},
    {"name": "db-01", "template": "CentOS 8", "cpu": 4, "memory": 8192}
]

deployment_ids = []
for config in vm_configs:
    deployment_id = await client.deploy_vm(
        config["template"],
        project_id,
        config["name"],
        {"cpu": config["cpu"], "memory": config["memory"]}
    )
    deployment_ids.append(deployment_id)

print(f"Deployed {len(deployment_ids)} VMs successfully")
```

### 3. Resource Monitoring

```python
# Monitor all deployments
deployments = await client.get_deployments()

for deployment in deployments:
    if deployment["status"] == "CREATE_INPROGRESS":
        print(f"⏳ {deployment['name']}: In progress...")
    elif deployment["status"] == "CREATE_SUCCESSFUL":
        print(f"✅ {deployment['name']}: Ready")
    elif deployment["status"] == "CREATE_FAILED":
        print(f"❌ {deployment['name']}: Failed")
```

### 4. Cleanup Operations

```python
# Clean up test deployments
deployments = await client.get_deployments()
test_deployments = [d for d in deployments if d["name"].startswith("test-")]

for deployment in test_deployments:
    await client.delete_deployment(deployment["id"])
    print(f"🗑️ Deleted: {deployment['name']}")
```

## Troubleshooting

### Common Issues

1. **MCP Server Not Found**
   ```
   FileNotFoundError: vra-mcp-server not found
   ```
   **Solution**: Ensure the MCP server is installed and in PATH:
   ```bash
   pip install vmware-vra-cli
   which vra-mcp-server
   ```

2. **Authentication Failures**
   ```
   Authentication failed: Invalid credentials
   ```
   **Solution**: Verify credentials and network connectivity:
   ```bash
   # Test connectivity
   curl -k https://your-vra-server.com/csp/gateway/am/api/health
   ```

3. **JSON-RPC Errors**
   ```
   Tool call failed: Method not found
   ```
   **Solution**: Ensure you're using a compatible MCP server version:
   ```bash
   vra-mcp-server --help
   ```

4. **Resource Access Issues**
   ```
   Failed to read resource: Not authenticated
   ```
   **Solution**: Always authenticate before accessing resources:
   ```python
   await client.authenticate(username, password, url, tenant)
   ```

### Debug Mode

Enable debug logging for troubleshooting:

```bash
export VRA_DEBUG=true
export VRA_VERBOSE=true
python examples/mcp_client_examples.py
```

### Logging

Check MCP server logs:

```bash
# Run with stderr capture
python examples/mcp_client_examples.py 2> mcp_server.log

# Review logs
tail -f mcp_server.log
```

## Best Practices

### Security

1. **Use environment variables** for credentials:
   ```python
   import os
   config = {
       "username": os.getenv("VRA_USERNAME"),
       "password": os.getenv("VRA_PASSWORD"),
       "url": os.getenv("VRA_URL"),
       "tenant": os.getenv("VRA_TENANT", "vsphere.local")
   }
   ```

2. **Enable SSL verification** in production:
   ```json
   "env": {
     "VRA_VERIFY_SSL": "true"
   }
   ```

### Performance

1. **Use batch operations** when possible:
   ```python
   # Good: Concurrent requests
   tasks = [
       client.get_catalog_items(),
       client.get_deployments(),
       client.get_dashboard_summary()
   ]
   results = await asyncio.gather(*tasks)
   
   # Avoid: Sequential requests
   catalog = await client.get_catalog_items()
   deployments = await client.get_deployments()
   dashboard = await client.get_dashboard_summary()
   ```

2. **Use pagination** for large datasets:
   ```python
   items = await client.get_catalog_items()  # Gets all pages
   
   # Or limit to first page for quick overview
   items = await client.mcp_client.call_tool("vra_list_catalog_items", {
       "page_size": 50,
       "first_page_only": True
   })
   ```

### Error Handling

1. **Always use try-catch blocks**:
   ```python
   try:
       result = await client.deploy_vm(...)
   except Exception as e:
       print(f"Deployment failed: {e}")
       # Implement retry logic or cleanup
   ```

2. **Check result status**:
   ```python
   result = await client.mcp_client.call_tool("vra_authenticate", {...})
   if result["isError"]:
       raise Exception(f"Auth failed: {result['content'][0]['text']}")
   ```

## Contributing

To add new examples:

1. **Create example function** following the naming pattern
2. **Add comprehensive error handling**
3. **Include configuration comments**
4. **Update this README** with the new example
5. **Test thoroughly** with different scenarios

## Support

- **Documentation**: [MCP Server Guide](../docs/mcp-server.md)
- **Issues**: [GitHub Issues](https://github.com/brun_s/vmware-vra-cli/issues)
- **Discussions**: [GitHub Discussions](https://github.com/brun_s/vmware-vra-cli/discussions)
