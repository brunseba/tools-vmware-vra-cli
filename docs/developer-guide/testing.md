# Testing Guide

This document covers testing strategies and procedures for the VMware vRA CLI project.

## Test Structure

The project uses pytest for unit testing with the following structure:

```
tests/
├── unit/
│   ├── test_cli.py
│   ├── test_auth.py
│   └── test_api_client.py
├── integration/
│   ├── test_vra_integration.py
│   └── test_mcp_server.py
└── fixtures/
    ├── auth_responses.json
    └── catalog_data.json
```

## Running Tests

### Unit Tests
```bash
# Run all unit tests
pytest tests/unit/

# Run with coverage
pytest tests/unit/ --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_cli.py -v
```

### Integration Tests
```bash
# Run integration tests (requires vRA environment)
pytest tests/integration/ -v

# Skip integration tests
pytest tests/unit/ -m "not integration"
```

## Test Configuration

### Environment Variables
Set these environment variables for testing:

```bash
export VRA_TEST_URL="https://vra-test.company.com"
export VRA_TEST_USERNAME="test-user"
export VRA_TEST_PASSWORD="test-password"
export VRA_TEST_DOMAIN="vsphere.local"
```

### Test Fixtures
Common fixtures are defined in `tests/conftest.py`:

- `mock_vra_client`: Mock vRA API client
- `sample_deployment`: Sample deployment data
- `test_config`: Test configuration object

## Mock Data

Use the provided fixtures for consistent testing:

```python
def test_list_deployments(mock_vra_client, sample_deployment):
    # Test implementation using mock data
    pass
```

## CI/CD Integration

Tests run automatically on:
- Pull requests
- Main branch commits
- Release tags

See `.github/workflows/test.yml` for CI configuration.

## Test Coverage

Maintain minimum 80% test coverage:
- Unit tests: >90%
- Integration tests: >70%
- Overall: >80%

## Testing MCP Server

### MCP Protocol Testing
```python
import pytest
from mcp import server

def test_mcp_list_tools():
    # Test MCP tool listing
    pass

def test_mcp_call_tool():
    # Test MCP tool execution
    pass
```

### Testing with AI Clients
Use the MCP test client for end-to-end testing:

```bash
# Test MCP server communication
python -m mcp.test_client stdio -- python -m vmware_vra_cli.mcp_server
```

## Performance Testing

### Load Testing
```bash
# Test CLI performance with large datasets
python tests/performance/load_test.py

# Profile memory usage
python -m memory_profiler tests/performance/memory_test.py
```

### Benchmarking
Regular benchmarks for:
- API response times
- CLI command execution
- MCP tool performance

## Troubleshooting Tests

### Common Issues
1. **Authentication Failures**: Check test credentials
2. **Network Timeouts**: Verify vRA connectivity
3. **Mock Data Mismatches**: Update fixtures

### Debug Mode
```bash
# Run tests with debug logging
pytest -v -s --log-cli-level=DEBUG
```

## Adding New Tests

1. Follow naming convention: `test_<functionality>.py`
2. Use descriptive test names
3. Include docstrings for complex tests
4. Mock external dependencies
5. Test both success and failure cases

Example test structure:
```python
def test_authenticate_success(mock_vra_client):
    """Test successful authentication with valid credentials."""
    # Arrange
    client = mock_vra_client
    
    # Act
    result = client.authenticate("user", "pass")
    
    # Assert
    assert result.success is True
    assert result.token is not None
```