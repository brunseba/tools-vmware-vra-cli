# AI Assistant Preset: VMware vRA CLI Tools

This project is a comprehensive CLI tool and REST API server for VMware vRealize Automation (vRA) management with advanced reporting, workflow automation, and MCP (Model Context Protocol) integration.

## Project Overview

**Core Technologies:**
- Python 3.10+ with `uv` package manager
- Click CLI framework  
- FastAPI REST server
- MCP (Model Context Protocol) server
- VMware vRA REST API integration
- Docker containerization with multi-stage builds

**Key Components:**
- CLI tool (`vra-cli`) - 17+ commands for vRA management
- REST API server (`vra-rest-server`) - 21 HTTP endpoints
- MCP server - 26 tools for AI/LLM integration
- Advanced reporting & analytics engine
- vRealize Orchestrator workflow management
- Authentication & token management

## Architecture

```
src/
├── cli/               # CLI commands and interface
├── api/               # REST API server implementation  
├── mcp/               # MCP server and tools
├── core/              # Core vRA client and utilities
├── auth/              # Authentication management
├── reports/           # Advanced reporting engine
└── workflows/         # Workflow management
```

## Key Features

### CLI Commands (17+)
- Authentication: `login`, `logout`, `status`, `refresh`
- Catalog: `catalog list`, `catalog get`, `catalog schema`, `catalog request`
- Deployments: `deployments list`, `deployments get`, `deployments delete`, `deployments resources`
- Reports: `report activity-timeline`, `report catalog-usage`, `report resources-usage`, `report unsync`
- Workflows: `workflow list`, `workflow get-schema`, `workflow run`, `workflow get-run`, `workflow cancel-run`

### REST API (21 endpoints)
- `/auth/*` - Authentication management
- `/catalog/*` - Service catalog operations
- `/deployments/*` - Deployment lifecycle
- `/reports/*` - Advanced analytics (NEW!)
- `/workflows/*` - Workflow automation (NEW!)

### MCP Integration (26 tools)
Complete AI/LLM integration via Model Context Protocol with tools for:
- Authentication operations
- Catalog management
- Deployment operations  
- Advanced reporting and analytics
- Workflow execution and management

### Advanced Reporting
- **Activity Timeline**: Deployment trends, peak analysis, success rates
- **Catalog Usage**: Item utilization, success rates, resource allocation
- **Resources Usage**: Cross-deployment resource analysis
- **Unsync Analysis**: Orphaned deployments with remediation suggestions

## Development Workflow

### Package Management
- Uses `uv` as package manager (faster than pip)
- Dependencies in `pyproject.toml`
- Development dependencies separated

### Code Organization
- Source code in `src/` directory
- CLI managed by Click framework
- Separate modules for core functionality
- Type hints throughout codebase

### Testing Strategy
- Unit tests for all core functionality
- Integration tests with mock vRA responses
- CLI command testing
- REST API endpoint testing
- MCP server tool testing

### Docker Strategy
- Multi-stage builds for efficiency
- Slim base images when possible
- SBOM (Software Bill of Materials) generation
- OpenContainers labels
- Development and production configurations

## AI Assistant Guidelines

### Code Style & Standards
- Follow existing patterns in codebase
- Use type hints for all functions
- Click decorators for CLI commands
- FastAPI patterns for REST endpoints
- Comprehensive error handling
- Logging throughout application

### Testing Requirements
- Always include unit tests for new functionality
- Test both success and error cases
- Mock external vRA API calls
- Include timeout parameters in interactive tests
- Validate input parameters thoroughly

### Documentation Standards
- Update relevant documentation files:
  - `README.md` - Main project overview
  - `docs/index.md` - Feature documentation
  - `docs/mcp-server.md` - MCP tools reference
  - `docs/user-guide/cli-reference.md` - CLI commands
  - `docs/rest-api-comprehensive.md` - REST API reference
- Include examples in all documentation
- Document new CLI commands and REST endpoints
- Update MCP tools documentation

### Git Workflow
- Use conventional commits (feat:, fix:, docs:, etc.)
- Generate commit messages after AI sessions
- Update version numbers appropriately
- Create meaningful branch names
- Include CHANGELOG updates for releases

### Development Commands
```bash
# Development setup
uv pip install -e ".[dev]"

# Run CLI locally
python -m src.cli --help

# Start REST server
python -m src.api.server

# Start MCP server  
python -m src.mcp.server

# Run tests
pytest src/tests/

# Lint and type check
ruff check src/
mypy src/

# Build Docker image
docker build -t vmware-vra-cli .

# Run with Docker Compose
docker compose up -d
```

### Common Tasks

#### Adding New CLI Commands
1. Create command function in appropriate `src/cli/` module
2. Use Click decorators and existing patterns
3. Add authentication checks where needed
4. Include comprehensive error handling
5. Add unit tests in `src/tests/cli/`
6. Update CLI reference documentation

#### Adding New REST Endpoints
1. Create endpoint in appropriate `src/api/` module
2. Follow FastAPI patterns and existing structure
3. Include request/response models
4. Add authentication middleware
5. Add comprehensive error responses
6. Update REST API documentation
7. Add integration tests

#### Adding New MCP Tools
1. Add tool definition in `src/mcp/tools.py`
2. Implement handler method with validation
3. Include authentication and error handling
4. Register tool in tools handler
5. Update MCP server documentation
6. Add tool tests

#### Adding New Reports
1. Create report logic in `src/reports/`
2. Add CLI command in `src/cli/reports.py`
3. Add REST endpoint in `src/api/reports.py`
4. Add MCP tool in `src/mcp/tools.py`
5. Include comprehensive data analysis
6. Format output for human readability
7. Add tests for all interfaces

### Authentication Patterns
- All operations require authentication except login
- Store tokens securely using keyring
- Implement token refresh logic
- Handle authentication errors gracefully
- Support multiple authentication methods

### Error Handling Standards
- Consistent error response formats
- Meaningful error messages for users
- Appropriate HTTP status codes for REST API
- Detailed logging for debugging
- Graceful degradation when possible

### Performance Considerations
- Implement pagination for large result sets
- Use connection pooling for HTTP requests
- Cache frequently accessed data appropriately
- Implement rate limiting for API endpoints
- Optimize database queries and API calls

### Security Best Practices
- Never log sensitive credentials
- Use secure token storage (keyring)
- Validate all input parameters
- Implement proper RBAC checks
- Use HTTPS in production environments
- Regular security dependency updates

## Project-Specific Context

### VMware vRA Integration
- Works with vRA Cloud and on-premises versions
- Supports multi-tenant environments
- Handles various resource types (VMs, networks, storage)
- Integrates with vRealize Orchestrator workflows
- Comprehensive error handling for vRA API responses

### Reporting Engine
- Generates actionable insights from vRA data
- Supports multiple time ranges and groupings  
- Provides trend analysis and peak usage detection
- Identifies optimization opportunities
- Root cause analysis for operational issues

### Workflow Integration
- Full vRealize Orchestrator workflow support
- Schema validation for workflow inputs
- Execution monitoring and status tracking
- Cancellation support for long-running workflows
- Error handling and retry logic

## Dependencies & Tools

### Core Dependencies
- `click` - CLI framework
- `fastapi` - REST API framework
- `requests` - HTTP client for vRA API
- `keyring` - Secure credential storage
- `pydantic` - Data validation
- `uvicorn` - ASGI server

### Development Dependencies
- `pytest` - Testing framework
- `ruff` - Linting and formatting
- `mypy` - Type checking
- `black` - Code formatting
- `pre-commit` - Git hooks

### Documentation Tools
- `mkdocs` - Documentation generation
- `mkdocs-material` - Documentation theme
- Mermaid diagram support
- PDF export capability

This preset enables AI assistants to understand the project structure, contribute effectively, and maintain consistency with established patterns and standards.