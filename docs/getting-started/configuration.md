# Configuration

VMware vRA CLI provides flexible configuration options to customize your experience. This guide covers all available configuration methods.

## Configuration Methods

The CLI supports multiple configuration sources, in order of precedence:

1. **Command-line arguments** (highest priority)
2. **Environment variables**
3. **Configuration file**
4. **Default values** (lowest priority)

## Configuration File

### Default Location

The CLI looks for configuration files in these locations:

- **Linux/macOS**: `~/.config/vmware-vra-cli/config.yaml`
- **Windows**: `%APPDATA%\vmware-vra-cli\config.yaml`

### Sample Configuration

Create a configuration file to set default values:

```yaml title="~/.config/vmware-vra-cli/config.yaml"
# VMware vRA CLI Configuration

# Default vRA server settings
server:
  url: "https://vra.company.com"
  tenant: "vsphere.local"
  verify_ssl: true
  timeout: 30

# Default project and template preferences
defaults:
  project: "Development"
  template: "Ubuntu Server 20.04 LTS"
  
# Output preferences
output:
  format: "table"  # table, json, yaml
  color: true
  verbose: false

# VM creation defaults
vm:
  cpu: 2
  memory: 4096  # MB
  disk: 20      # GB
  
# Authentication settings
auth:
  store_token: true
  token_lifetime: 3600  # seconds
  
# Logging configuration
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  file: "~/.local/share/vmware-vra-cli/vra-cli.log"
```

### Create Config Directory

Create the configuration directory and file:

```bash
# Linux/macOS
mkdir -p ~/.config/vmware-vra-cli
touch ~/.config/vmware-vra-cli/config.yaml

# Windows (PowerShell)
New-Item -ItemType Directory -Path "$env:APPDATA\vmware-vra-cli" -Force
New-Item -ItemType File -Path "$env:APPDATA\vmware-vra-cli\config.yaml" -Force
```

## Environment Variables

Set environment variables to configure the CLI:

### Authentication Variables

```bash
export VRA_URL="https://vra.company.com"
export VRA_USERNAME="admin@vsphere.local"
export VRA_TENANT="vsphere.local"
# Note: Don't set VRA_PASSWORD in production - use keyring instead
```

### Default Settings

```bash
export VRA_DEFAULT_PROJECT="Development"
export VRA_DEFAULT_TEMPLATE="Ubuntu Server 20.04 LTS"
export VRA_OUTPUT_FORMAT="json"
export VRA_VERIFY_SSL="true"
export VRA_TIMEOUT="60"
```

### Shell Profile Setup

Add to your shell profile (`.bashrc`, `.zshrc`, etc.):

```bash
# VMware vRA CLI Configuration
export VRA_URL="https://vra.company.com"
export VRA_DEFAULT_PROJECT="Development"
export VRA_OUTPUT_FORMAT="table"
```

## Command-Line Arguments

Override any setting using command-line arguments:

```bash
# Override server URL
vra --url "https://vra-prod.company.com" vm list

# Override output format
vra --format json vm templates

# Override default project
vra vm create --project "Production" --name "prod-vm-001"
```

## Configuration Management

### View Current Configuration

Display the effective configuration:

```bash
vra config show
```

### Set Configuration Values

```bash
# Set default project
vra config set defaults.project "Production"

# Set output format
vra config set output.format "json"

# Set server URL
vra config set server.url "https://vra-prod.company.com"
```

### Get Configuration Values

```bash
# Get specific value
vra config get server.url

# Get all defaults
vra config get defaults
```

### Reset Configuration

```bash
# Reset to defaults
vra config reset

# Reset specific section
vra config reset defaults
```

## Profiles

Manage multiple vRA environments using profiles:

### Create Profile

```bash
vra profile create production \
  --url "https://vra-prod.company.com" \
  --tenant "prod.local"
  
vra profile create development \
  --url "https://vra-dev.company.com" \
  --tenant "dev.local"
```

### Switch Profiles

```bash
# Use production profile
vra profile use production

# Use development profile  
vra profile use development

# Show current profile
vra profile current

# List all profiles
vra profile list
```

### Profile Configuration

Each profile has its own configuration:

```bash
# Set defaults for current profile
vra config set defaults.project "WebApps"

# View profile-specific config
vra config show --profile production
```

## SSL Configuration

### Disable SSL Verification (Development Only)

!!! warning "Security Warning"
    Only disable SSL verification in development environments with self-signed certificates.

```bash
# Via environment variable
export VRA_VERIFY_SSL="false"

# Via config file
server:
  verify_ssl: false

# Via command line
vra --no-verify-ssl vm list
```

### Custom CA Certificate

For environments with custom CA certificates:

```bash
# Via environment variable
export VRA_CA_CERT="/path/to/ca-cert.pem"

# Via config file
server:
  ca_cert: "/path/to/ca-cert.pem"
```

## Logging Configuration

### Log Levels

Configure logging verbosity:

```bash
# Via environment variable
export VRA_LOG_LEVEL="DEBUG"

# Via config file
logging:
  level: "DEBUG"

# Via command line
vra --verbose vm create --name "test-vm"
```

### Log File Location

```bash
# Default locations:
# Linux/macOS: ~/.local/share/vmware-vra-cli/vra-cli.log
# Windows: %LOCALAPPDATA%\vmware-vra-cli\vra-cli.log

# Custom location via config
logging:
  file: "/var/log/vra-cli.log"
```

## Advanced Configuration

### Request Timeouts

```bash
# Via config file
server:
  timeout: 60  # seconds
  connect_timeout: 10
  read_timeout: 30
```

### Retry Configuration

```bash
# Via config file
server:
  retry_attempts: 3
  retry_delay: 1  # seconds
  retry_backoff: 2.0
```

### Output Customization

```bash
# Via config file
output:
  format: "table"      # table, json, yaml, csv
  color: true          # colorized output
  pager: true          # use pager for long output
  max_width: 120       # table width limit
  timestamp: false     # include timestamps
```

## Configuration Validation

Validate your configuration:

```bash
# Check configuration syntax
vra config validate

# Test connection with current config
vra config test

# Show resolved configuration
vra config show --resolved
```

## Example Configurations

### Development Environment

```yaml title="Development Config"
server:
  url: "https://vra-dev.company.com"
  tenant: "dev.local"
  verify_ssl: false

defaults:
  project: "Development"
  template: "Ubuntu Server 20.04 LTS"

output:
  format: "table"
  color: true
  verbose: true

logging:
  level: "DEBUG"
```

### Production Environment

```yaml title="Production Config"
server:
  url: "https://vra-prod.company.com"
  tenant: "prod.local"
  verify_ssl: true
  timeout: 60

defaults:
  project: "Production"
  
output:
  format: "json"
  color: false

logging:
  level: "INFO"
  file: "/var/log/vra-cli.log"
```

### CI/CD Environment

```bash title="CI/CD Environment Variables"
export VRA_URL="https://vra-ci.company.com"
export VRA_USERNAME="ci-service-account"
export VRA_DEFAULT_PROJECT="CI-CD"
export VRA_OUTPUT_FORMAT="json"
export VRA_LOG_LEVEL="WARNING"
export VRA_VERIFY_SSL="true"
```

## Troubleshooting

### Common Configuration Issues

#### Configuration Not Found

```bash
ERROR: Configuration file not found
```

**Solution**: Create the config directory and file:

```bash
mkdir -p ~/.config/vmware-vra-cli
touch ~/.config/vmware-vra-cli/config.yaml
```

#### Invalid YAML Syntax

```bash
ERROR: Invalid configuration file syntax
```

**Solution**: Validate your YAML syntax:

```bash
vra config validate
```

#### Environment Variable Not Working

**Solution**: Ensure variables are exported and in the correct format:

```bash
# Check current variables
env | grep VRA_

# Export variables
export VRA_URL="https://vra.company.com"
```

### Getting Help

For configuration help:

```bash
vra config --help
vra --help
```
