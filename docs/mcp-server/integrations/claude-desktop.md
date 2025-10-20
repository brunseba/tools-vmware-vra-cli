# Claude Desktop Integration

This guide shows you how to integrate the VMware vRA MCP server with Claude Desktop for AI-powered infrastructure management.

## Prerequisites

- [Claude Desktop](https://claude.ai/desktop) installed
- VMware vRA MCP server installed and configured
- Active vRA authentication

## Configuration

### 1. Locate Claude Desktop Configuration

The configuration file location varies by operating system:

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```
~/.config/claude/claude_desktop_config.json
```

### 2. Configure MCP Server

Add the VMware vRA MCP server to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "vmware-vra": {
      "command": "vra-mcp-server",
      "env": {
        "VRA_LOG_LEVEL": "INFO"
      },
      "description": "VMware vRA infrastructure management"
    }
  }
}
```

### 3. Advanced Configuration

For more control over the MCP server behavior:

```json
{
  "mcpServers": {
    "vmware-vra": {
      "command": "python",
      "args": ["-m", "src.mcp.server"],
      "cwd": "/path/to/tools-vmware-vra-cli",
      "env": {
        "VRA_LOG_LEVEL": "DEBUG",
        "VRA_CONFIG_PATH": "/custom/path/.vra-cli/config.json",
        "VRA_TIMEOUT": "60"
      },
      "description": "VMware vRA infrastructure management with custom settings"
    }
  }
}
```

## Restart Claude Desktop

After updating the configuration:

1. Completely quit Claude Desktop
2. Restart the application
3. Look for the MCP server connection indicator

## Verification

### Check MCP Server Status

In Claude Desktop, you should see:
- MCP server connection indicator (usually a small icon)
- Available tools count (should show 26+ tools)

### Test Basic Functionality

Try these example prompts in Claude Desktop:

**Authentication Check:**
```
Can you check if I'm authenticated with vRA?
```

**List Catalog Items:**
```
What catalog items are available in my vRA environment?
```

**Deployment Status:**
```
Show me the current status of my deployments
```

## Usage Examples

### 1. VM Provisioning

**User:** "I need a new development VM for our web application project"

**Claude Response:** Claude will use the MCP tools to:
- Check available catalog items
- Suggest appropriate VM templates
- Request deployment with proper naming and project assignment
- Monitor deployment progress

### 2. Infrastructure Analysis

**User:** "Can you analyze our resource usage over the last 30 days?"

**Claude Response:** Claude will:
- Generate activity timeline reports
- Analyze catalog usage statistics
- Provide resource utilization insights
- Suggest optimization opportunities

### 3. Deployment Management

**User:** "Find and clean up any failed deployments older than 7 days"

**Claude Response:** Claude will:
- List deployments with status filtering
- Identify failed deployments by age
- Provide cleanup recommendations
- Execute deletions with confirmation

## Available Capabilities

Through the MCP integration, Claude can:

### Infrastructure Operations
- Provision new VMs and applications
- Manage deployment lifecycles
- Execute vRealize Orchestrator workflows
- Handle authentication and token management

### Analytics & Reporting
- Generate usage reports and trends
- Analyze resource utilization patterns
- Identify optimization opportunities
- Track deployment success rates

### Resource Management
- Apply and manage resource tags
- Monitor deployment resources
- Track resource relationships
- Manage resource governance

### Troubleshooting
- Diagnose deployment issues
- Find orphaned resources
- Analyze performance bottlenecks
- Provide remediation suggestions

## Best Practices

### 1. Context Setting

Provide clear context for better AI assistance:
```
"I'm working on the 'web-app-dev' project and need to provision 
3 identical VMs for load testing our new application release."
```

### 2. Incremental Operations

Break complex tasks into steps:
```
"First, show me available Linux VM templates, then help me 
provision 2 VMs with specific network configurations."
```

### 3. Confirmation Patterns

Claude will typically ask for confirmation before:
- Creating new deployments
- Deleting resources
- Making configuration changes
- Executing workflows

## Troubleshooting

### MCP Server Not Connecting

**Symptoms:**
- No MCP server indicator in Claude Desktop
- "Tool not available" errors

**Solutions:**
1. Check configuration file syntax
2. Verify server executable path
3. Ensure vRA authentication is valid
4. Check logs: `~/.vra-cli/logs/mcp-server.log`

### Authentication Issues

**Symptoms:**
- "Not authenticated" errors
- API permission errors

**Solutions:**
1. Re-authenticate: `vra auth login`
2. Check token expiration: `vra auth status`
3. Verify vRA connectivity
4. Confirm user permissions

### Tool Execution Errors

**Symptoms:**
- Specific tools failing
- Timeout errors
- Partial responses

**Solutions:**
1. Check vRA server status
2. Increase timeout settings
3. Verify network connectivity
4. Check vRA API rate limits

### Debug Mode

Enable detailed logging for troubleshooting:

```json
{
  "mcpServers": {
    "vmware-vra": {
      "command": "vra-mcp-server",
      "env": {
        "VRA_LOG_LEVEL": "DEBUG",
        "VRA_MCP_DEBUG": "true"
      }
    }
  }
}
```

## Performance Tips

### 1. Optimize Tool Usage

- Use filtering parameters to reduce data transfer
- Leverage caching for frequently accessed data
- Batch operations when possible

### 2. Resource Management

- Set reasonable page sizes for large result sets
- Use first_page_only for quick overviews
- Implement timeout handling for long operations

### 3. Network Optimization

- Ensure stable network connection to vRA
- Consider increasing timeout values for slow networks
- Use compression when available

## Next Steps

- [VS Code Continue Integration](vscode-continue.md)
- [Custom Client Development](custom-clients.md)
- [MCP Tools Reference](../tools-reference.md)
- [Advanced Configuration](../setup.md)