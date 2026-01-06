# VMware vRA CLI & MCP Server

[![Version](https://img.shields.io/pypi/v/vmware-vra-cli)](https://pypi.org/project/vmware-vra-cli/)
[![Python](https://img.shields.io/pypi/pyversions/vmware-vra-cli)](https://pypi.org/project/vmware-vra-cli/)
[![License](https://img.shields.io/github/license/brunseba/tools-vmware-vra-cli)](https://github.com/brunseba/tools-vmware-vra-cli/blob/main/LICENSE)
[![Tests](https://img.shields.io/github/actions/workflow/status/brunseba/tools-vmware-vra-cli/test.yml?branch=main&label=tests)](https://github.com/brunseba/tools-vmware-vra-cli/actions)
[![MCP Compatible](https://img.shields.io/badge/MCP-2025--06--28-blue.svg)](https://modelcontextprotocol.io/)
[![Documentation](https://img.shields.io/badge/docs-github--pages-blue)](https://brunseba.github.io/tools-vmware-vra-cli)

A comprehensive Python toolkit for VMware vRealize Automation 8 automation, featuring a powerful CLI, a fully compliant **Model Context Protocol (MCP) server** for LLM integration, and a traditional REST API server. This toolkit enables developers, system administrators, and AI assistants to automate VM provisioning, management, and infrastructure operations through multiple interfaces.

## Features

✨ **Service Catalog Integration**
- List, view, and request catalog items
- **Generic schema-driven catalog operations** with persistent cache
- Manage deployments (create, monitor, delete)
- Execute and monitor workflows
- Interactive forms with rich validation
- **Advanced Analytics & Reporting** with timeline analysis and resource insights

🔐 **Authentication & Security**
- Secure bearer token authentication
- System keyring integration for credential storage
- SSL/TLS support with custom CA certificates
- Multi-environment profile management

🎨 **Rich Terminal Experience**
- Beautiful tables with colors and styling
- Multiple output formats (table, JSON, YAML)
- Progress indicators and status updates
- Interactive prompts and confirmations

⚙️ **Configuration Flexibility**
- Environment variables support
- YAML/JSON configuration files
- Command-line argument overrides
- Profile-based multi-environment support

🌐 **REST API Server**
- HTTP REST API server for web integrations
- Same functionality as CLI in HTTP endpoints
- OpenAPI documentation with Swagger UI
- Programmatic access for automation pipelines

🤖 **MCP Server (NEW!)**
- True Model Context Protocol (MCP) compliant server (v2025-06-18)
- **26 specialized tools** for AI-powered infrastructure management
- Tools organized into 6 categories: Authentication, Catalog, Schema Catalog, Deployments, Reporting, Workflows
- JSON-RPC 2.0 over stdio transport
- Compatible with Claude Desktop, VS Code Continue, and custom MCP clients
- Advanced features: Schema-driven operations, comprehensive reporting, workflow execution

## Quick Start

### Installation

```bash
# Install with pipx (recommended)
pipx install vmware-vra-cli

# Or with pip
pip install vmware-vra-cli
```

### Basic Usage

```bash
# Authenticate
vra auth login

# List catalog items
vra catalog list

# Request a catalog item
vra catalog request <item-id> --project <project-id>

# List deployments
vra deployment list

# Execute a workflow
vra workflow run <workflow-id> --inputs '{"param": "value"}'
```

### REST API Server Usage

#### Local Development
```bash
# Start the REST API server
vra-rest-server

# Server will be available at http://localhost:8000
# Interactive API docs: http://localhost:8000/docs
```

#### Docker Compose (Recommended)
```bash
# Basic server setup
docker compose up -d

# With OpenAPI generation
docker compose --profile tools up -d

# With API documentation (Swagger UI)
docker compose --profile docs up -d

# With log monitoring
docker compose --profile monitoring up -d

# All services combined
docker compose --profile tools --profile docs --profile monitoring up -d
```

**Available Services:**
- **REST API Server**: `http://localhost:8000` - Main API server
- **Swagger UI**: `http://localhost:8090` - Interactive API documentation
- **Log Viewer**: `http://localhost:8080` - Real-time log monitoring (Dozzle)
- **OpenAPI JSON**: `./output/openapi.json` - Generated API specification

### MCP Server Usage

#### Local Development
```bash
# Start the MCP server
vra-mcp-server

# Server communicates via JSON-RPC 2.0 over stdio
# Compatible with Claude Desktop, VS Code Continue, etc.
```

#### Claude Desktop Integration
Add to your Claude Desktop configuration:
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

## Documentation

Comprehensive documentation is available at: **[https://brunseba.github.io/tools-vmware-vra-cli](https://brunseba.github.io/tools-vmware-vra-cli)**

- 📚 [Installation Guide](https://brunseba.github.io/tools-vmware-vra-cli/getting-started/installation/)
- 🚀 [Quick Start Tutorial](https://brunseba.github.io/tools-vmware-vra-cli/getting-started/quick-start/)
- ⚙️ [Configuration Options](https://brunseba.github.io/tools-vmware-vra-cli/getting-started/configuration/)
- 🔐 [Authentication Guide](https://brunseba.github.io/tools-vmware-vra-cli/user-guide/authentication/)
- 🌐 [REST API Server Guide](docs/rest-api-server.md)
- 🤖 [MCP Server Guide](docs/mcp-server.md)
- 🔄 [Compatibility Matrix](docs/compatibility-matrix.md)
- 📚 [API Reference](https://brunseba.github.io/tools-vmware-vra-cli/user-guide/api-reference/)

## Use Cases

### Development Teams
- **Rapid Environment Provisioning**: Create development VMs in seconds
- **CI/CD Integration**: Automate infrastructure provisioning in pipelines
- **Testing Infrastructure**: Spin up test environments on-demand

### System Administrators
- **Bulk Operations**: Manage hundreds of VMs efficiently
- **Infrastructure Automation**: Standardize deployment processes
- **Resource Management**: Monitor and cleanup unused resources

### DevOps Engineers
- **Infrastructure as Code**: Version-controlled infrastructure definitions
- **Automated Deployments**: Streamline application deployment workflows
- **Multi-Environment Management**: Consistent deployment across environments

## CLI Commands Overview

### Authentication
```bash
vra auth login          # Authenticate and store token
vra auth logout         # Clear stored credentials
vra auth status         # Check authentication status
```

### Service Catalog
```bash
vra catalog list        # List available catalog items
vra catalog show <id>   # Show catalog item details
vra catalog schema <id> # Show item request schema
vra catalog request <id> # Request a catalog item
```

### Generic Schema Catalog (NEW!)
```bash
vra schema-catalog load-schemas          # Load & cache schemas
vra schema-catalog list-schemas          # List cached schemas
vra schema-catalog search-schemas "VM"   # Search schemas
vra schema-catalog execute-schema <id>   # Interactive execution
vra schema-catalog clear-cache           # Clear persistent cache
```

### Deployments
```bash
vra deployment list     # List all deployments
vra deployment show <id> # Show deployment details
vra deployment delete <id> # Delete a deployment
vra deployment resources <id> # Show deployment resources
```

### Reports & Analytics (NEW!)
```bash
vra report activity-timeline    # Deployment activity over time
vra report catalog-usage        # Catalog item usage statistics
vra report resources-usage      # Comprehensive resource analysis
vra report unsync               # Unsynced deployments analysis
```

### Workflows
```bash
vra workflow list       # List available workflows
vra workflow run <id>   # Execute a workflow
```

### Tag Management
```bash
vra tag list            # List all tags
vra tag create <key>    # Create a new tag
vra tag show <id>       # Show tag details
vra tag assign <resource-id> <tag-id>  # Assign tag to resource
vra tag remove <resource-id> <tag-id>  # Remove tag from resource
vra tag resource-tags <resource-id>    # Show resource tags
```

## Configuration Example

```yaml
# ~/.config/vmware-vra-cli/config.yaml
server:
  url: "https://vra.company.com"
  tenant: "vsphere.local"
  verify_ssl: true

defaults:
  project: "Development"
  output_format: "table"

logging:
  level: "INFO"
```

## Development

### Prerequisites
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) for dependency management

### Setup

```bash
# Clone the repository
git clone https://github.com/brunseba/tools-vmware-vra-cli.git
cd tools-vmware-vra-cli

# Install dependencies
uv sync --extra dev --extra docs

# Install pre-commit hooks
uv run pre-commit install

# Run tests
uv run pytest

# Run CLI
uv run vra --help
```

### Project Structure

```
vmware-vra-cli/
├── src/vmware_vra_cli/    # Main package
│   ├── api/               # API clients
│   └── cli.py            # CLI implementation
├── tests/                # Test suite
├── docs/                 # Documentation
├── pyproject.toml        # Project configuration
└── mkdocs.yml           # Documentation config
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](docs/developer-guide/contributing.md) for details.

### Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
feat(catalog): add support for catalog item filtering
fix(auth): resolve token storage issue on macOS
docs(api): update authentication examples
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/brunseba/tools-vmware-vra-cli/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/brunseba/tools-vmware-vra-cli/discussions)
- 📖 **Documentation**: [GitHub Pages](https://brunseba.github.io/tools-vmware-vra-cli)

## Acknowledgments

- Built with [Click](https://click.palletsprojects.com/) for CLI framework
- Styled with [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- Based on [VMware vRA REST API](https://developer.broadcom.com/xapis/vrealize-automation-api/latest/) and [vRealize Orchestrator API](https://developer.broadcom.com/xapis/vrealize-orchestrator-api/latest/)
- Inspired by real-world DevOps automation needs

---

*Built with ❤️ for VMware administrators and developers*
