# VS Code Continue Integration

This guide shows you how to integrate the VMware vRA MCP server with VS Code Continue for AI-powered infrastructure management directly in your development environment.

## Prerequisites

- [Visual Studio Code](https://code.visualstudio.com/) installed
- [Continue extension](https://marketplace.visualstudio.com/items?itemName=Continue.continue) installed
- VMware vRA MCP server installed and configured
- Active vRA authentication

## Installation

### 1. Install Continue Extension

In VS Code:
1. Go to Extensions (Ctrl+Shift+X / Cmd+Shift+X)
2. Search for "Continue"
3. Install the Continue extension by Continue
4. Reload VS Code if prompted

### 2. Configure Continue

Open Continue configuration:
1. Open Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
2. Type "Continue: Open Config" and select it
3. This opens `~/.continue/config.json`

## Configuration

### Basic MCP Server Configuration

Add the VMware vRA MCP server to your Continue configuration:

```json
{
  "models": [
    {
      "title": "Claude 3.5 Sonnet",
      "provider": "anthropic",
      "model": "claude-3-5-sonnet-20241022",
      "apiKey": "your-api-key-here"
    }
  ],
  "mcpServers": {
    "vmware-vra": {
      "command": "vra-mcp-server",
      "env": {
        "VRA_LOG_LEVEL": "INFO"
      }
    }
  },
  "allowAnonymousTelemetry": false
}
```

### Advanced Configuration

For development or custom installations:

```json
{
  "models": [
    {
      "title": "Claude 3.5 Sonnet",
      "provider": "anthropic",
      "model": "claude-3-5-sonnet-20241022",
      "apiKey": "your-api-key-here"
    }
  ],
  "mcpServers": {
    "vmware-vra": {
      "command": "python",
      "args": ["-m", "src.mcp.server"],
      "cwd": "/path/to/tools-vmware-vra-cli",
      "env": {
        "VRA_LOG_LEVEL": "DEBUG",
        "VRA_CONFIG_PATH": "/custom/path/.vra-cli/config.json",
        "VRA_TIMEOUT": "60",
        "PYTHONPATH": "/path/to/tools-vmware-vra-cli"
      }
    }
  },
  "contextProviders": [
    {
      "name": "diff",
      "params": {}
    },
    {
      "name": "folder",
      "params": {
        "folders": ["~/projects"]
      }
    }
  ]
}
```

## Restart Continue

After updating the configuration:
1. Open Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
2. Type "Developer: Reload Window" and select it
3. Or restart VS Code completely

## Verification

### Check MCP Server Connection

1. Open Continue sidebar (click the Continue icon)
2. Look for MCP server connection status
3. Should show "vmware-vra" server with 26+ tools

### Test Basic Functionality

Use the Continue chat interface to test:

**Authentication Check:**
```
@continue Can you check if I'm authenticated with vRA?
```

**Infrastructure Overview:**
```
@continue What's the current status of our vRA deployments?
```

## Usage Patterns

### 1. Infrastructure as Code Integration

**Scenario:** Working on Terraform or similar IaC

```
@continue I'm updating this Terraform configuration. Can you check 
what similar VMs are already deployed in vRA so I can ensure 
consistency with our naming conventions?
```

Continue will:
- Use vRA MCP tools to list current deployments
- Analyze naming patterns
- Suggest consistent naming for new resources

### 2. Development Environment Management

**Scenario:** Setting up development environments

```
@continue I need to provision a new dev environment for this 
microservice. Based on the code in this workspace, what type 
of VM configuration would you recommend?
```

Continue will:
- Analyze your codebase context
- Check available vRA catalog items
- Recommend appropriate VM specifications
- Help provision the environment

### 3. Troubleshooting and Debugging

**Scenario:** Application deployment issues

```
@continue Our application deployment is failing. Can you check 
if there are any infrastructure issues with our VMs in the 
'web-app-staging' project?
```

Continue will:
- Check deployment status in vRA
- Analyze resource health
- Review recent deployment activities
- Suggest troubleshooting steps

## Development Workflows

### 1. Code-Driven Infrastructure

When working on infrastructure code, Continue can:

```
@continue Based on this Docker Compose file, help me provision 
the appropriate VMs in vRA for a production deployment.
```

### 2. Automated Testing Environments

For test environment management:

```
@continue I'm running these integration tests. Can you spin up 
a clean test environment and let me know when it's ready?
```

### 3. Resource Optimization

For performance analysis:

```
@continue Can you generate a resource usage report for our 
development VMs and suggest optimization opportunities?
```

## Available Commands

Through Continue, you can use natural language for:

### Infrastructure Operations
- "Provision a new VM for microservice X"
- "Scale up the database tier in staging"
- "Deploy a new environment based on this config"

### Monitoring & Analysis
- "Show me resource utilization trends"
- "Find any failed deployments from last week"
- "Generate a usage report for the dev team"

### Workflow Automation
- "Execute the database backup workflow"
- "Run the environment cleanup process"
- "Start the automated testing pipeline"

### Resource Management
- "Tag all VMs in project X with environment labels"
- "Find untagged resources that need governance"
- "Apply cost center tags to new deployments"

## Best Practices

### 1. Context Awareness

Continue can see your code context, so be specific:
```
@continue Looking at this microservice architecture, provision 
VMs for each service with appropriate resource allocations.
```

### 2. Project-Specific Configuration

Set project-specific vRA contexts:
```
@continue Set the default vRA project to 'mobile-app-dev' for 
this workspace so all infrastructure requests use that context.
```

### 3. Incremental Operations

Use Continue's conversation history:
```
@continue Now that you've provisioned those VMs, can you set up 
monitoring for them and create the appropriate tags?
```

## Integration Patterns

### 1. CI/CD Pipeline Integration

```javascript
// In your VS Code workspace, Continue can help with:
// - Infrastructure provisioning scripts
// - Deployment automation
// - Environment management

@continue Help me write a script that provisions test environments 
before running our integration tests, and cleans them up afterward.
```

### 2. Documentation Generation

```
@continue Based on our current vRA infrastructure, generate 
documentation for our deployment topology and resource dependencies.
```

### 3. Code Review Integration

```
@continue Review this infrastructure change and check if we have 
sufficient resources in vRA to support the new requirements.
```

## Troubleshooting

### MCP Server Not Loading

**Symptoms:**
- No vRA tools available in Continue
- MCP connection errors in logs

**Solutions:**
1. Check Continue configuration syntax
2. Verify server executable path: `which vra-mcp-server`
3. Test server manually: `vra-mcp-server --test`
4. Check Continue logs: View → Output → Continue

### Authentication Issues

**Symptoms:**
- "Not authenticated" responses
- vRA API errors

**Solutions:**
1. Authenticate in terminal: `vra auth login`
2. Verify status: `vra auth status`
3. Check token expiration
4. Restart Continue server

### Performance Issues

**Symptoms:**
- Slow responses
- Timeout errors
- Partial results

**Solutions:**
1. Increase timeout in configuration
2. Use filtering parameters in requests
3. Check network connectivity
4. Monitor vRA server load

### Debug Configuration

For troubleshooting, enable debug mode:

```json
{
  "mcpServers": {
    "vmware-vra": {
      "command": "vra-mcp-server",
      "env": {
        "VRA_LOG_LEVEL": "DEBUG",
        "VRA_MCP_DEBUG": "true",
        "VRA_CONTINUE_DEBUG": "true"
      }
    }
  }
}
```

## Advanced Features

### 1. Custom Prompts

Create project-specific prompts for common tasks:

```json
{
  "customCommands": [
    {
      "name": "Provision Dev Environment",
      "prompt": "Provision a new development environment in vRA with the standard configuration for this project type. Use appropriate naming conventions and apply required tags.",
      "description": "Quick dev environment setup"
    }
  ]
}
```

### 2. Workspace Templates

Configure workspace-specific vRA settings:

```json
{
  "contextProviders": [
    {
      "name": "vmware-vra-workspace",
      "params": {
        "defaultProject": "web-app-dev",
        "defaultTags": ["team:frontend", "env:development"],
        "preferredCatalogItems": ["ubuntu-20.04-vm", "centos-8-vm"]
      }
    }
  ]
}
```

## Security Considerations

### 1. Credential Management

- Use system keyring for vRA credentials
- Don't store passwords in Continue config
- Rotate tokens regularly

### 2. Permission Scoping

- Use minimal required vRA permissions
- Implement resource-based access controls
- Monitor API usage and access patterns

### 3. Code Context

- Be aware that Continue can see your code
- Avoid including sensitive information in prompts
- Use project-specific configurations

## Next Steps

- [Custom Client Development](custom-clients.md)
- [Claude Desktop Integration](claude-desktop.md)
- [MCP Tools Reference](../tools-reference.md)
- [Advanced Configuration](../setup.md)