# Architecture Presentations

This directory contains detailed reveal.js presentations covering all aspects of the VMware vRA CLI architecture and design.

## Presentations

### 📑 [Index](index.html) - Main Navigation
Start here to access all presentations.

### 🏗️  [01 - Architecture Overview](01-architecture-overview.html)
**Duration:** 45-60 minutes | **Slides:** ~50

**Topics Covered:**
- 5-Layer Architecture Pattern
- Design Patterns (Command, Strategy, Factory)
- Data Flow Architectures (Request, Auth, Config, MCP Server)
- Error Handling Strategies
- Performance Considerations
- Caching and Async Operations

### 🔧 [02 - Components Model](02-components-model.html)
**Duration:** 40-50 minutes | **Slides:** ~45

**Topics Covered:**
- CLI Layer Components
- Command Components (Auth, Catalog, Deployment, Workflow)
- MCP Server Components (FastAPI, Routers, Models)
- Service Components (Auth, Catalog, Deployment)
- Integration Components (API Client, Token Manager, Config Manager)
- Infrastructure Components (HTTP Client, Keyring, File System)
- Component Interfaces and Dependencies
- Component Lifecycle Management

### 📊 [03 - Data Models](03-data-models.html)
**Duration:** 35-45 minutes | **Slides:** ~40

**Topics Covered:**
- Entity Relationship Diagrams
- Core Data Models (Auth, Config, Catalog, Deployment, Tags, Workflows)
- Data Validation with Pydantic
- JSON Schemas
- Data Transformation and Serialization
- Model Converters

### 🔒 [04 - Security & Compliance](04-security-compliance.html)
**Duration:** 30-40 minutes | **Slides:** ~35

**Topics Covered:**
- Trust Boundaries and Security Zones
- Authentication Flow (Two-Phase)
- Token Management (Identity, Access, Refresh)
- Multi-Factor Authentication Support
- Data Classification (4 Levels)
- Encryption Requirements (At Rest, In Transit)
- Key Management
- Network Security (TLS Configuration)

## How to View

### Option 1: Direct File Access
```bash
open index.html
```

### Option 2: Local Web Server
```bash
cd docs/architecture-design/presentations
python3 -m http.server 8000
# Open http://localhost:8000/index.html
```

### Option 3: GitHub Pages
View online at: https://brunseba.github.io/tools-vmware-vra-cli/architecture-design/presentations/

## Navigation

**Keyboard Shortcuts:**
- Arrow keys - Navigate between slides
- Space - Next slide
- ESC - Slide overview
- S - Speaker notes
- F - Fullscreen
- Ctrl/Cmd + Shift + F - Search slides
- ? - Help menu

## Creating Additional Presentations

To create a new presentation, use this template structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>VMware vRA CLI - [Topic]</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.6.0/dist/reset.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.6.0/dist/reveal.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.6.0/dist/theme/black.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.6.0/plugin/highlight/monokai.css">
</head>
<body>
    <div class="reveal">
        <div class="slides">
            <!-- Your slides here -->
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/reveal.js@4.6.0/dist/reveal.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/reveal.js@4.6.0/plugin/highlight/highlight.js"></script>
    <script>
        Reveal.initialize({
            hash: true,
            slideNumber: 'c/t',
            transition: 'slide',
            plugins: [RevealHighlight]
        });
    </script>
</body>
</html>
```

## Status

- ✅ Index/Navigation - Complete
- ⏳ Architecture Overview - In Progress
- ⏳ Components Model - Planned
- ⏳ Data Models - Planned
- ⏳ Security & Compliance - Planned

## Contributing

When creating or updating presentations:

1. Keep content focused and detailed
2. Include code examples where relevant
3. Use consistent styling
4. Add speaker notes for complex topics
5. Test navigation between slides
6. Update this README with any changes

## Related Documentation

- [Architecture Overview (Markdown)](../architecture-overview.md)
- [Components Model (Markdown)](../components-model.md)
- [Data Models (Markdown)](../data-models.md)
- [Security & Compliance (Markdown)](../security-compliance.md)
