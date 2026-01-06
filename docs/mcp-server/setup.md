# MCP Server Setup

This guide walks you through setting up the VMware vRA MCP (Model Context Protocol) server for AI assistant integration.

## Prerequisites

- Python 3.10 or later
- VMware vRA 8 access with appropriate permissions
- AI assistant that supports MCP protocol (Claude Desktop, VS Code Continue, etc.)

## Installation

### Using pipx (Recommended)
```bash
pipx install vmware-vra-cli
```

### Using pip
```bash
pip install vmware-vra-cli
```

### Development Installation
```bash
git clone https://github.com/brunseba/tools-vmware-vra-cli.git
cd tools-vmware-vra-cli
uv pip install -e ".[dev]"
```

## Configuration

### 1. Server Configuration

Create a configuration file at `~/.vra-cli/config.json`:

```json
{
  "vra_url": "https://vra.company.com",
  "tenant": "corp.local",
  "domain": "vsphere.local",
  "mcp_server": {
    "log_level": "INFO",
    "max_tools": 50,
    "timeout": 30
  }
}
```

### 2. Authentication Setup

The MCP server uses the same authentication as the CLI tool:

```bash
# Authenticate with vRA (this stores credentials securely)
vra auth login --username admin --url https://vra.company.com
```

## Starting the MCP Server

### Manual Start
```bash
# Start the MCP server
vra-mcp-server

# Server will start on stdio for MCP protocol communication
# You'll see initialization messages in the logs
```

### Docker Deployment
```bash
docker run -d \
  --name vra-mcp-server \
  -v ~/.vra-cli:/root/.vra-cli \
  vmware-vra-cli:latest \
  vra-mcp-server
```

## Verification

Test that the server is working:

```bash
# Check server capabilities
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-28", "capabilities": {}}}' | vra-mcp-server
```

Expected response includes:
- Server name and version
- Available tools (26+ tools)
- Protocol capabilities

## Available Tools

The MCP server provides 26 specialized tools:

### Authentication (1 tool)
- `vra_authenticate` - Authenticate with vRA and store credentials securely

### Catalog Management (4 tools)
- `vra_list_catalog_items` - List available catalog items
- `vra_get_catalog_item` - Get catalog item details
- `vra_get_catalog_item_schema` - Get item request schema
- `vra_request_catalog_item` - Request catalog item deployment

### Schema Catalog (8 tools)
- `vra_schema_load_schemas` - Load catalog schemas from JSON files into persistent cache
- `vra_schema_list_schemas` - List available catalog schemas from cache
- `vra_schema_search_schemas` - Search catalog schemas by name or description
- `vra_schema_show_schema` - Show detailed schema information for a catalog item
- `vra_schema_execute_schema` - Execute a catalog item using its schema with AI-guided input collection
- `vra_schema_generate_template` - Generate input template for a catalog item
- `vra_schema_clear_cache` - Clear the persistent schema registry cache
- `vra_schema_registry_status` - Show schema registry status and statistics

### Deployment Management (4 tools)
- `vra_list_deployments` - List deployments with filtering
- `vra_get_deployment` - Get deployment details
- `vra_delete_deployment` - Delete deployment
- `vra_get_deployment_resources` - Get deployment resources

### Advanced Reporting (4 tools)
- `vra_report_activity_timeline` - Generate activity timeline reports
- `vra_report_catalog_usage` - Analyze catalog item usage
- `vra_report_resources_usage` - Comprehensive resource analysis
- `vra_report_unsync` - Find unsynced deployments

### Workflow Management (5 tools)
- `vra_list_workflows` - List vRO workflows
- `vra_get_workflow_schema` - Get workflow input/output schema
- `vra_run_workflow` - Execute workflow with inputs
- `vra_get_workflow_run` - Get workflow execution status
- `vra_cancel_workflow_run` - Cancel running workflow

## Troubleshooting

### Common Issues

**Server won't start**
- Check Python version (3.10+ required)
- Verify vRA authentication: `vra auth status`
- Check configuration file format

**AI assistant can't connect**
- Ensure server is running on stdio mode
- Check AI assistant MCP configuration
- Verify protocol version compatibility (2025-06-28)

**Authentication errors**
- Re-authenticate: `vra auth login`
- Check network connectivity to vRA
- Verify credentials and permissions

### Debug Mode

Start server with debug logging:
```bash
VRA_LOG_LEVEL=DEBUG vra-mcp-server
```

### Logs

Check logs for troubleshooting:
```bash
# View recent logs
tail -f ~/.vra-cli/logs/mcp-server.log

# Check authentication logs
grep "auth" ~/.vra-cli/logs/mcp-server.log
```

## Next Steps

- [Claude Desktop Integration](integrations/claude-desktop.md)
- [VS Code Continue Integration](integrations/vscode-continue.md)
- [Custom Client Development](integrations/custom-clients.md)
- [MCP Tools Reference](tools-reference.md)