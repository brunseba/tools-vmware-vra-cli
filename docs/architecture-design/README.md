# Architecture & Design Documentation

This directory contains comprehensive architecture and design documentation for the VMware vRA CLI project.

## Contents

- **[Architecture Overview](architecture-overview.md)** - Complete system architecture and design patterns
- **[Components Model](components-model.md)** - Detailed component breakdown and interactions
- **[Context Diagram](context-diagram.md)** - High-level system context and external dependencies
- **[Data Models](data-models.md)** - Data structures, schemas, and object models
- **[Functional Requirements](functional-requirements.md)** - System capabilities and features
- **[Non-Functional Requirements](non-functional-requirements.md)** - Performance, scalability, and quality attributes
- **[Security and Compliance](security-compliance.md)** - Security architecture, threat model, and compliance

## Interactive Presentation

### 📊 [View Architecture Presentation](presentation.html)

A comprehensive reveal.js presentation covering all aspects of the system architecture and design.

**Topics Covered:**
- System Overview and Key Features
- Architecture Patterns (Layered, Command, Strategy, Factory)
- Core Components (CLI Engine, Authentication, API Client, Configuration, Output, MCP Server)
- MCP Server Architecture (26 specialized tools)
- Security & Compliance (zones, authentication, encryption, MFA)
- Data Models (Core, Configuration, API)
- Requirements (Functional and Non-Functional)
- Technology Stack

**How to View:**

1. **Option 1: Local File**
   ```bash
   # Open directly in browser
   open docs/architecture-design/presentation.html
   ```

2. **Option 2: Local Web Server**
   ```bash
   # Serve with Python
   cd docs/architecture-design
   python3 -m http.server 8000
   # Then open http://localhost:8000/presentation.html
   ```

3. **Option 3: GitHub Pages**
   View online at: https://brunseba.github.io/tools-vmware-vra-cli/architecture-design/presentation.html

**Navigation:**
- **Arrow keys** - Navigate between slides
- **Space** - Next slide
- **Esc** - Slide overview
- **S** - Speaker notes (if available)
- **F** - Fullscreen
- **?** - Help menu
- **Ctrl/Cmd + Shift + F** - Search slides

## Architecture Highlights

### Layered Architecture
The system uses a 5-layer architecture pattern:
1. **Presentation Layer** - CLI commands, web API, output formatters
2. **Application Layer** - Command handlers, validation, business logic
3. **Service Layer** - Domain-specific services
4. **Integration Layer** - API clients, token management
5. **Infrastructure Layer** - HTTP, keyring, filesystem, logging

### Key Design Patterns
- **Command Pattern** - CLI command execution
- **Strategy Pattern** - Output formatting
- **Factory Pattern** - Command instantiation
- **Repository Pattern** - Data access abstraction

### Security Features
- System keyring integration for secure credential storage
- TLS 1.2+ for all network communication
- AES-256 encryption for configuration files
- Multi-factor authentication support
- Token lifecycle management (8h access, 90d refresh)

### MCP Server (Model Context Protocol)
- **26 specialized tools** across 6 categories
- FastAPI-based RESTful API
- OpenAPI/Swagger documentation
- Docker deployment support
- Health monitoring and logging

## Technology Stack

### Core
- Python 3.10+
- Click (CLI framework)
- Requests (HTTP client)
- System Keyring (security)

### MCP Server
- FastAPI (web framework)
- Uvicorn (ASGI server)
- Pydantic (data validation)
- Docker & Docker Compose

### Development
- pytest (testing)
- MkDocs (documentation)
- uv (build system)
- pipx (installation)

## Contributing

When updating architecture documentation:

1. Keep all documents synchronized
2. Update the presentation if making significant changes
3. Use Mermaid diagrams for visual representations
4. Follow the established documentation structure
5. Include examples and code snippets where helpful

## Questions?

For questions about the architecture or design decisions:
- Review the detailed documentation files
- Check the presentation for visual explanations
- Consult the main project documentation: https://brunseba.github.io/tools-vmware-vra-cli
