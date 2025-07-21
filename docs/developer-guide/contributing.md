# Contributing Guide

Welcome to the VMware vRA CLI project! We're excited to have you contribute to making this tool better for the community.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10+** - The project requires Python 3.10 or higher
- **uv** - Package manager for Python projects
- **Git** - Version control system
- **Docker** (optional) - For running integration tests

### Development Environment Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/brun_s/vmware-vra-cli.git
   cd vmware-vra-cli
   ```

2. **Install dependencies using uv:**
   ```bash
   # Install development dependencies
   uv sync --extra dev --extra docs
   
   # Activate the virtual environment
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate     # Windows
   ```

3. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

4. **Verify installation:**
   ```bash
   # Run tests
   pytest
   
   # Check code formatting
   black --check src/ tests/
   
   # Run linting
   flake8 src/ tests/
   
   # Type checking
   mypy src/
   ```

## Development Workflow

### Branch Strategy

We follow a simplified Git flow:

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - Feature development branches
- `bugfix/*` - Bug fix branches
- `hotfix/*` - Critical production fixes

### Conventional Commits

We use conventional commit messages for automated changelog generation:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### Types:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Build process or auxiliary tool changes

#### Examples:
```bash
feat(tag): add tag management functionality
fix(auth): resolve token refresh issue
docs(api): update API documentation
test(catalog): add unit tests for catalog client
```

### Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Write code following our coding standards
   - Add tests for new functionality
   - Update documentation as needed

3. **Run pre-commit checks:**
   ```bash
   pre-commit run --all-files
   ```

4. **Run tests:**
   ```bash
   pytest --cov=src --cov-report=html
   ```

5. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat(scope): description of your changes"
   ```

6. **Push and create a pull request:**
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Standards

### Python Code Style

We follow PEP 8 with some modifications:

- **Line length**: 88 characters (Black default)
- **Import sorting**: Using isort with Black profile
- **Type hints**: Required for all public functions
- **Docstrings**: Google-style docstrings for all modules, classes, and functions

#### Example:
```python
from typing import Dict, List, Optional

def create_tag(
    key: str, 
    value: Optional[str] = None, 
    description: Optional[str] = None
) -> Dict[str, str]:
    """Create a new tag with the specified parameters.
    
    Args:
        key: The tag key (required)
        value: The tag value (optional)
        description: A description of the tag (optional)
        
    Returns:
        A dictionary containing the created tag information.
        
    Raises:
        ValueError: If the key is empty or invalid.
    """
    if not key:
        raise ValueError("Tag key cannot be empty")
    
    tag_data = {"key": key}
    if value is not None:
        tag_data["value"] = value
    if description is not None:
        tag_data["description"] = description
        
    return tag_data
```

### Project Structure

```
vmware-vra-cli/
├── src/vmware_vra_cli/          # Source code
│   ├── __init__.py
│   ├── cli.py                   # CLI entry point
│   └── api/                     # API clients
│       ├── __init__.py
│       └── catalog.py           # Service catalog client
├── tests/                       # Test files
│   ├── __init__.py
│   ├── test_catalog_api.py      # API tests
│   └── conftest.py              # Test configuration
├── docs/                        # Documentation
│   ├── index.md
│   ├── getting-started/
│   ├── user-guide/
│   └── developer-guide/
├── pyproject.toml               # Project configuration
├── README.md
└── main.py                      # CLI wrapper
```

## Testing Guidelines

### Unit Tests

Write comprehensive unit tests for all new functionality:

```python
import pytest
from requests_mock import Mocker
from vmware_vra_cli.api.catalog import CatalogClient, Tag

def test_create_tag():
    """Test tag creation functionality."""
    client = CatalogClient("https://vra.example.com", "token123")
    
    with Mocker() as m:
        # Mock the API response
        m.post(
            "https://vra.example.com/vco/api/tags",
            json={
                "id": "tag-123",
                "key": "environment",
                "value": "production",
                "description": "Production environment"
            }
        )
        
        # Test the functionality
        tag = client.create_tag(
            key="environment",
            value="production", 
            description="Production environment"
        )
        
        # Assertions
        assert tag.id == "tag-123"
        assert tag.key == "environment"
        assert tag.value == "production"
        assert tag.description == "Production environment"
```

### Test Organization

- **Unit tests**: Test individual functions and methods
- **Integration tests**: Test API interactions
- **End-to-end tests**: Test complete CLI workflows

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_catalog_api.py

# Run tests matching a pattern
pytest -k "test_tag"

# Run tests with verbose output
pytest -v
```

## Documentation

### Code Documentation

All code should be well-documented:

- **Module docstrings**: Describe the module's purpose
- **Class docstrings**: Explain the class functionality
- **Method docstrings**: Document parameters, return values, and exceptions
- **Type hints**: For all function parameters and return values

### User Documentation

When adding new features, update:

- User guide documentation
- API reference
- Command help text
- README examples

### Building Documentation

```bash
# Install docs dependencies
uv sync --extra docs

# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

## Adding New Features

### API Client Extensions

When adding new API functionality:

1. **Add Pydantic models** for data structures
2. **Implement client methods** with proper error handling
3. **Add comprehensive tests** with mocked responses
4. **Document the API endpoints** used

Example:
```python
class NewResource(BaseModel):
    """Represents a new resource in vRA."""
    id: str
    name: str
    status: str
    created_at: Optional[str] = None

class CatalogClient:
    def create_resource(self, name: str) -> NewResource:
        """Create a new resource."""
        url = f"{self.base_url}/api/resources"
        payload = {"name": name}
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        return NewResource(**response.json())
```

### CLI Command Extensions

When adding new CLI commands:

1. **Create command groups** for related functionality
2. **Use consistent option naming** across commands
3. **Support multiple output formats** (table, JSON, YAML)
4. **Add comprehensive help text**
5. **Include examples** in docstrings

Example:
```python
@main.group()
def resource():
    """Resource management operations."""
    pass

@resource.command('create')
@click.argument('name')
@click.option('--description', help='Resource description')
@click.pass_context
def create_resource(ctx, name, description):
    """Create a new resource.
    
    Examples:
        vra resource create "my-resource" --description "Test resource"
    """
    client = get_catalog_client()
    
    with console.status(f"Creating resource {name}..."):
        resource = client.create_resource(name, description)
    
    console.print(f"[green]✅ Resource created: {resource.id}[/green]")
```

## Quality Assurance

### Pre-commit Hooks

Our pre-commit configuration includes:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Code linting
- **mypy**: Static type checking
- **pytest**: Running tests

### Continuous Integration

GitHub Actions automatically:

- Run tests on multiple Python versions
- Check code formatting and linting
- Build and test documentation
- Generate coverage reports

### Performance Considerations

- **Use connection pooling** for API clients
- **Implement proper error handling** with retries
- **Cache frequently accessed data** when appropriate
- **Optimize CLI startup time** by lazy loading

## Release Process

### Version Management

We use semantic versioning (SemVer):

- `MAJOR.MINOR.PATCH`
- Increment MAJOR for breaking changes
- Increment MINOR for new features
- Increment PATCH for bug fixes

### Creating a Release

1. **Update version** in `pyproject.toml`
2. **Update changelog** with new features and fixes
3. **Create a git tag:**
   ```bash
   git tag -a v0.3.0 -m "Release version 0.3.0"
   git push origin v0.3.0
   ```
4. **GitHub Actions** will automatically build and publish

### Changelog Generation

We maintain a changelog following [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [0.3.0] - 2024-01-15

### Added
- Tag management functionality
- New CLI commands for resource tagging

### Changed
- Improved error handling in API client

### Fixed
- Authentication token refresh issue
```

## Community Guidelines

### Code Review Process

All contributions must go through code review:

1. **Create a pull request** with a clear description
2. **Ensure CI passes** (tests, linting, formatting)
3. **Request review** from maintainers
4. **Address feedback** promptly
5. **Squash commits** before merging

### Issue Reporting

When reporting issues:

- Use the issue template
- Provide clear reproduction steps
- Include relevant logs and error messages
- Specify your environment (OS, Python version, CLI version)

### Feature Requests

For new features:

- Check existing issues first
- Provide clear use case and motivation
- Consider implementation complexity
- Be willing to contribute the implementation

## Getting Help

- **Documentation**: Check the user guide and API reference
- **Issues**: Search existing GitHub issues
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact maintainers for security issues

## Recognition

Contributors will be recognized in:

- README.md contributors section
- Release notes
- Changelog entries

Thank you for contributing to VMware vRA CLI! 🎉
