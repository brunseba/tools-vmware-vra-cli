# VMware vRA CLI Reference Guide

This comprehensive reference guide covers all available commands, options, and usage patterns for the VMware vRA CLI tool.

## Global Options

All commands support these global options:

| Option | Description | Default |
|--------|-------------|---------|
| `--verbose`, `-v` | Enable verbose output with HTTP request/response details | `False` |
| `--format` | Output format: `table`, `json`, `yaml` | `table` |
| `--version` | Show CLI version and exit | - |
| `--help` | Show help message and exit | - |

### Global Option Examples

```bash
# Enable verbose logging for troubleshooting
vmware-vra --verbose catalog list

# Get JSON output instead of table
vmware-vra --format json deployment list

# Show version information
vmware-vra --version
```

## Authentication Commands (`auth`)

Manage authentication tokens and credentials.

### `auth login`

Authenticate to vRA using username and password.

**Syntax:**
```bash
vmware-vra auth login [OPTIONS]
```

**Options:**
| Option | Type | Description | Required |
|--------|------|-------------|----------|
| `--username` | TEXT | Username for vRA access | Yes* |
| `--password` | TEXT | Password for vRA access | Yes* |
| `--url` | TEXT | vRA server URL | No** |
| `--tenant` | TEXT | vRA tenant | No** |
| `--domain` | TEXT | Domain for multiple identity sources | No |

*Prompted if not provided  
**Uses configured default if available

**Examples:**
```bash
# Interactive login (prompts for credentials)
vmware-vra auth login

# Login with specific parameters
vmware-vra auth login \
    --username john.doe@company.com \
    --url https://vra.company.com \
    --tenant company.local

# Login with specific domain for multiple identity sources
vmware-vra auth login \
    --username administrator \
    --domain vsphere.local \
    --url https://vra.company.com
```

**Sample Output:**
```
✅ Authentication successful!
🔑 Tokens saved securely
💾 Configuration saved: https://vra.company.com
🏢 Tenant: company.local
🌐 Domain: vsphere.local
```

### `auth logout`

Clear stored authentication tokens.

**Syntax:**
```bash
vmware-vra auth logout
```

**Example:**
```bash
vmware-vra auth logout
```

**Sample Output:**
```
✅ Logged out successfully
```

### `auth status`

Check current authentication status.

**Syntax:**
```bash
vmware-vra auth status
```

**Example:**
```bash
vmware-vra auth status
```

**Sample Outputs:**
```
# Fully authenticated
✅ Authenticated (Access token available)
🔄 Refresh token available for automatic renewal

# Refresh token only
⚠️ Only refresh token available - will obtain new access token on next use

# Not authenticated
❌ Not authenticated
```

### `auth refresh`

Manually refresh the access token.

**Syntax:**
```bash
vmware-vra auth refresh
```

**Example:**
```bash
vmware-vra auth refresh
```

**Sample Output:**
```
✅ Access token refreshed successfully
```

## Configuration Commands (`config`)

Manage CLI configuration settings.

### `config show`

Display current configuration values.

**Syntax:**
```bash
vmware-vra config show
```

**Example:**
```bash
vmware-vra config show
```

**Sample Output (Table Format):**
```
                   VMware vRA CLI Configuration
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Setting       ┃ Value                                   ┃ Source                          ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Api Url       │ https://vra.company.com                 │ Config file                     │
│ Tenant        │ company.local                           │ Config file                     │
│ Domain        │ vsphere.local                           │ Config file                     │
│ Verify Ssl    │ True                                    │ Default                         │
│ Timeout       │ 30                                      │ Default                         │
└───────────────┴─────────────────────────────────────────┴─────────────────────────────────┘

Config file: /Users/username/.config/vmware-vra-cli/config.json
```

### `config set`

Set a configuration value.

**Syntax:**
```bash
vmware-vra config set KEY VALUE
```

**Available Keys:**
- `api_url`: vRA server URL
- `tenant`: vRA tenant identifier
- `domain`: Authentication domain
- `verify_ssl`: SSL verification (true/false)
- `timeout`: Request timeout in seconds

**Examples:**
```bash
# Set vRA server URL
vmware-vra config set api_url https://vra.company.com

# Set tenant
vmware-vra config set tenant company.local

# Disable SSL verification (not recommended for production)
vmware-vra config set verify_ssl false

# Set timeout
vmware-vra config set timeout 60
```

**Sample Output:**
```
✅ Configuration updated: api_url = https://vra.company.com
Saved to: /Users/username/.config/vmware-vra-cli/config.json
```

### `config reset`

Reset configuration to defaults.

**Syntax:**
```bash
vmware-vra config reset [OPTIONS]
```

**Options:**
| Option | Description |
|--------|-------------|
| `--confirm` | Skip confirmation prompt |

**Examples:**
```bash
# Reset with confirmation prompt
vmware-vra config reset

# Reset without confirmation
vmware-vra config reset --confirm
```

### `config edit`

Edit configuration file in default editor.

**Syntax:**
```bash
vmware-vra config edit
```

**Example:**
```bash
vmware-vra config edit
```

## Service Catalog Commands (`catalog`)

Manage catalog items and requests.

### `catalog list`

List available catalog items.

**Syntax:**
```bash
vmware-vra catalog list [OPTIONS]
```

**Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--project` | TEXT | None | Filter by project ID |
| `--page-size` | INT | 100 | Items per page (max: 2000) |
| `--first-page-only` | FLAG | False | Fetch only first page |

**Examples:**
```bash
# List all catalog items
vmware-vra catalog list

# List items for specific project
vmware-vra catalog list --project dev-project-123

# List first page only (faster for large catalogs)
vmware-vra catalog list --first-page-only

# Get JSON output
vmware-vra --format json catalog list
```

**Sample Output (Table):**
```
                     Service Catalog Items (156 items)
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ ID                                     ┃ Name                     ┃ Type                ┃ Status    ┃ Version   ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━┩
│ blueprint-ubuntu-server-01             │ Ubuntu Server Template  │ blueprint           │ PUBLISHED │ 1.2       │
│ blueprint-windows-server-2019          │ Windows Server 2019     │ blueprint           │ PUBLISHED │ 2.1       │
│ workflow-create-user-account           │ Create User Account     │ workflow            │ PUBLISHED │ 1.0       │
│ blueprint-docker-container             │ Docker Container        │ blueprint           │ PUBLISHED │ 3.0       │
└────────────────────────────────────────┴──────────────────────────┴─────────────────────┴───────────┴───────────┘
```

### `catalog show`

Show details of a specific catalog item.

**Syntax:**
```bash
vmware-vra catalog show ITEM_ID
```

**Examples:**
```bash
# Show catalog item details
vmware-vra catalog show blueprint-ubuntu-server-01

# Get JSON output
vmware-vra --format json catalog show blueprint-ubuntu-server-01
```

**Sample Output (Table):**
```
                        Catalog Item: Ubuntu Server Template
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Property    ┃ Value                                                                                   ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ ID          │ blueprint-ubuntu-server-01                                                              │
│ Name        │ Ubuntu Server Template                                                                  │
│ Type        │ blueprint                                                                               │
│ Status      │ PUBLISHED                                                                               │
│ Version     │ 1.2                                                                                     │
│ Description │ Standard Ubuntu 20.04 server template with common configurations                       │
└─────────────┴─────────────────────────────────────────────────────────────────────────────────────────┘
```

### `catalog schema`

Show request schema for a catalog item.

**Syntax:**
```bash
vmware-vra catalog schema ITEM_ID
```

**Examples:**
```bash
# Show schema for catalog item
vmware-vra catalog schema blueprint-ubuntu-server-01

# Always outputs JSON regardless of --format setting
vmware-vra catalog schema blueprint-ubuntu-server-01
```

**Sample Output:**
```json
{
  "type": "object",
  "properties": {
    "hostname": {
      "type": "string",
      "title": "Hostname",
      "description": "Server hostname"
    },
    "cpu": {
      "type": "integer",
      "title": "CPU Count",
      "default": 2,
      "minimum": 1,
      "maximum": 8
    },
    "memory": {
      "type": "string",
      "title": "Memory Size",
      "default": "4GB",
      "enum": ["2GB", "4GB", "8GB", "16GB"]
    }
  },
  "required": ["hostname"]
}
```

### `catalog request`

Request a catalog item deployment.

**Syntax:**
```bash
vmware-vra catalog request ITEM_ID [OPTIONS]
```

**Options:**
| Option | Type | Description | Required |
|--------|------|-------------|----------|
| `--inputs` | TEXT | Input parameters as JSON string | No |
| `--inputs-file` | PATH | Input parameters from YAML/JSON file | No |
| `--project` | TEXT | Project ID for the request | Yes |
| `--reason` | TEXT | Reason for the request | No |
| `--name` | TEXT | Deployment name | No |

**Examples:**
```bash
# Request with inline JSON inputs
vmware-vra catalog request blueprint-ubuntu-server-01 \
    --inputs '{"hostname": "web-server-01", "cpu": 4, "memory": "8GB"}' \
    --project dev-project-123 \
    --reason "Development web server"

# Request with inputs from file
vmware-vra catalog request blueprint-ubuntu-server-01 \
    --inputs-file server-config.yaml \
    --project dev-project-123 \
    --name "web-server-01"

# Simple request with minimal parameters
vmware-vra catalog request blueprint-ubuntu-server-01 \
    --project dev-project-123
```

**Sample inputs-file (server-config.yaml):**
```yaml
hostname: web-server-01
cpu: 4
memory: "8GB"
disk_size: "100GB"
network: "corporate-dmz"
install_packages:
  - nginx
  - docker
  - git
```

**Sample Output:**
```
✅ Request submitted successfully!
Deployment ID: deployment-12345-abcdef
Request ID: request-67890-ghijkl
```

## Deployment Commands (`deployment`)

Manage and export deployments.

### `deployment list`

List deployments.

**Syntax:**
```bash
vmware-vra deployment list [OPTIONS]
```

**Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--project` | TEXT | None | Filter by project ID |
| `--status` | TEXT | None | Filter by status |
| `--page-size` | INT | 100 | Items per page (max: 2000) |
| `--first-page-only` | FLAG | False | Fetch only first page |

**Examples:**
```bash
# List all deployments
vmware-vra deployment list

# List deployments for specific project
vmware-vra deployment list --project dev-project-123

# List only successful deployments
vmware-vra deployment list --status CREATE_SUCCESSFUL

# First page only for large environments
vmware-vra deployment list --first-page-only
```

**Sample Output:**
```
                               Deployments (89 items)
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ID                                     ┃ Name                   ┃ Status              ┃ Project           ┃ Created                       ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ deployment-12345-abcdef                │ web-server-01          │ CREATE_SUCCESSFUL   │ dev-project-123   │ 2024-01-15T09:30:00.000Z      │
│ deployment-67890-ghijkl                │ database-server-01     │ CREATE_SUCCESSFUL   │ dev-project-123   │ 2024-01-15T10:15:00.000Z      │
│ deployment-13579-mnopqr                │ load-balancer-01       │ CREATE_INPROGRESS   │ prod-project-456  │ 2024-01-15T11:00:00.000Z      │
└────────────────────────────────────────┴────────────────────────┴─────────────────────┴───────────────────┴───────────────────────────────┘
```

### `deployment show`

Show deployment details.

**Syntax:**
```bash
vmware-vra deployment show DEPLOYMENT_ID
```

**Examples:**
```bash
# Show deployment details
vmware-vra deployment show deployment-12345-abcdef

# Get YAML output
vmware-vra --format yaml deployment show deployment-12345-abcdef
```

**Sample Output (Table):**
```
                            Deployment: web-server-01
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Property           ┃ Value                                                                   ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ id                 │ deployment-12345-abcdef                                                 │
│ name               │ web-server-01                                                           │
│ status             │ CREATE_SUCCESSFUL                                                       │
│ projectId          │ dev-project-123                                                         │
│ catalogItemId      │ blueprint-ubuntu-server-01                                              │
│ createdAt          │ 2024-01-15T09:30:00.000Z                                                │
│ completedAt        │ 2024-01-15T09:45:00.000Z                                                │
│ inputs             │ {"hostname": "web-server-01", "cpu": 4, "memory": "8GB"}               │
└────────────────────┴─────────────────────────────────────────────────────────────────────────┘
```

### `deployment delete`

Delete a deployment.

**Syntax:**
```bash
vmware-vra deployment delete DEPLOYMENT_ID [OPTIONS]
```

**Options:**
| Option | Description |
|--------|-------------|
| `--confirm` | Skip confirmation prompt |

**Examples:**
```bash
# Delete with confirmation prompt
vmware-vra deployment delete deployment-12345-abcdef

# Delete without confirmation
vmware-vra deployment delete deployment-12345-abcdef --confirm
```

**Sample Output:**
```
✅ Deployment deployment-12345-abcdef deletion initiated
```

### `deployment resources`

Show deployment resources.

**Syntax:**
```bash
vmware-vra deployment resources DEPLOYMENT_ID
```

**Examples:**
```bash
# Show deployment resources
vmware-vra deployment resources deployment-12345-abcdef

# Get JSON output
vmware-vra --format json deployment resources deployment-12345-abcdef
```

**Sample Output:**
```
                      Resources for Deployment deployment-12345-abcdef
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓
┃ ID                                     ┃ Name                   ┃ Type                     ┃ Status            ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
│ vm-12345-abcdef                        │ web-server-01          │ Cloud.vSphere.Machine    │ SUCCESS           │
│ disk-67890-ghijkl                      │ web-server-01-disk1    │ Cloud.vSphere.Disk       │ SUCCESS           │
│ nic-13579-mnopqr                       │ web-server-01-nic0     │ Cloud.vSphere.Network    │ SUCCESS           │
└────────────────────────────────────────┴────────────────────────┴──────────────────────────┴───────────────────┘
```

### `deployment export-all`

Export all deployments grouped by catalog item.

**Syntax:**
```bash
vmware-vra deployment export-all [OPTIONS]
```

**Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--project` | TEXT | None | Filter deployments by project ID |
| `--output-dir` | TEXT | `./exports` | Directory to save export files |
| `--include-resources` | FLAG | False | Include resource details (slower) |
| `--no-unsynced` | FLAG | False | Exclude unsynced deployments |

For comprehensive details and examples, see the [Deployment Export Guide](deployment-export.md).

**Quick Examples:**
```bash
# Basic export
vmware-vra deployment export-all

# Export with resource details
vmware-vra deployment export-all --include-resources

# Export specific project
vmware-vra deployment export-all --project dev-project-123

# Export to custom directory
vmware-vra deployment export-all --output-dir /backup/vra-exports
```

## Tag Management Commands (`tag`)

Manage tags and resource tagging.

### `tag list`

List available tags.

**Syntax:**
```bash
vmware-vra tag list [OPTIONS]
```

**Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--search` | TEXT | None | Search term to filter tags |
| `--page-size` | INT | 100 | Items per page (max: 2000) |
| `--first-page-only` | FLAG | False | Fetch only first page |

**Examples:**
```bash
# List all tags
vmware-vra tag list

# Search for specific tags
vmware-vra tag list --search environment

# First page only
vmware-vra tag list --first-page-only
```

### `tag show`

Show details of a specific tag.

**Syntax:**
```bash
vmware-vra tag show TAG_ID
```

**Example:**
```bash
vmware-vra tag show tag-12345-abcdef
```

### `tag create`

Create a new tag.

**Syntax:**
```bash
vmware-vra tag create KEY [OPTIONS]
```

**Options:**
| Option | Type | Description |
|--------|------|-------------|
| `--value` | TEXT | Tag value (optional) |
| `--description` | TEXT | Tag description (optional) |

**Examples:**
```bash
# Create simple tag
vmware-vra tag create environment --value production

# Create tag with description
vmware-vra tag create cost-center \
    --value "IT-Infrastructure" \
    --description "Cost center for IT infrastructure resources"
```

### `tag update`

Update an existing tag.

**Syntax:**
```bash
vmware-vra tag update TAG_ID [OPTIONS]
```

**Options:**
| Option | Type | Description |
|--------|------|-------------|
| `--key` | TEXT | New tag key |
| `--value` | TEXT | New tag value |
| `--description` | TEXT | New tag description |

**Example:**
```bash
vmware-vra tag update tag-12345-abcdef \
    --value "development" \
    --description "Development environment resources"
```

### `tag delete`

Delete a tag.

**Syntax:**
```bash
vmware-vra tag delete TAG_ID [OPTIONS]
```

**Options:**
| Option | Description |
|--------|-------------|
| `--confirm` | Skip confirmation prompt |

**Example:**
```bash
vmware-vra tag delete tag-12345-abcdef --confirm
```

### `tag assign`

Assign a tag to a resource.

**Syntax:**
```bash
vmware-vra tag assign RESOURCE_ID TAG_ID [OPTIONS]
```

**Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--resource-type` | CHOICE | `deployment` | Resource type: `deployment` or `catalog-item` |

**Examples:**
```bash
# Assign tag to deployment
vmware-vra tag assign deployment-12345-abcdef tag-67890-ghijkl

# Assign tag to catalog item
vmware-vra tag assign blueprint-ubuntu-server-01 tag-environment-prod \
    --resource-type catalog-item
```

### `tag remove`

Remove a tag from a resource.

**Syntax:**
```bash
vmware-vra tag remove RESOURCE_ID TAG_ID [OPTIONS]
```

**Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--resource-type` | CHOICE | `deployment` | Resource type: `deployment` or `catalog-item` |
| `--confirm` | FLAG | False | Skip confirmation prompt |

**Example:**
```bash
vmware-vra tag remove deployment-12345-abcdef tag-67890-ghijkl --confirm
```

### `tag resource-tags`

Show tags assigned to a resource.

**Syntax:**
```bash
vmware-vra tag resource-tags RESOURCE_ID [OPTIONS]
```

**Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--resource-type` | CHOICE | `deployment` | Resource type: `deployment` or `catalog-item` |

**Example:**
```bash
vmware-vra tag resource-tags deployment-12345-abcdef
```

## Report Commands (`report`)

Generate analytics and reports.

### `report activity-timeline`

Generate deployment activity timeline.

**Syntax:**
```bash
vmware-vra report activity-timeline [OPTIONS]
```

**Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--project` | TEXT | None | Filter by project ID |
| `--days-back` | INT | 30 | Days back for timeline |
| `--group-by` | CHOICE | `day` | Group by: `day`, `week`, `month`, `year` |
| `--statuses` | TEXT | All | Comma-separated status list |

**Examples:**
```bash
# 30-day activity timeline
vmware-vra report activity-timeline

# Weekly activity for 90 days
vmware-vra report activity-timeline --days-back 90 --group-by week

# Only successful deployments
vmware-vra report activity-timeline \
    --statuses "CREATE_SUCCESSFUL,UPDATE_SUCCESSFUL"
```

### `report catalog-usage`

Generate catalog usage report.

**Syntax:**
```bash
vmware-vra report catalog-usage [OPTIONS]
```

**Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--project` | TEXT | None | Filter by project ID |
| `--include-zero` | FLAG | False | Include items with zero deployments |
| `--sort-by` | CHOICE | `deployments` | Sort by: `deployments`, `resources`, `name` |
| `--detailed-resources` | FLAG | False | Fetch exact resource counts |

**Examples:**
```bash
# Basic usage report
vmware-vra report catalog-usage

# Include all catalog items
vmware-vra report catalog-usage --include-zero --sort-by name

# Detailed resource counting
vmware-vra report catalog-usage --detailed-resources
```

### `report resources-usage`

Generate a consolidated resources usage report across all deployments.

**Syntax:**
```bash
vmware-vra report resources-usage [OPTIONS]
```

**Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--project` | TEXT | None | Filter by project ID |
| `--detailed-resources` | FLAG | True | Fetch detailed resource information (default enabled) |
| `--no-detailed-resources` | FLAG | False | Skip detailed resource fetching for faster execution |
| `--sort-by` | CHOICE | `catalog-item` | Sort by: `deployment-name`, `catalog-item`, `resource-count`, `status` |
| `--group-by` | CHOICE | `catalog-item` | Group by: `catalog-item`, `resource-type`, `deployment-status` |

**Examples:**
```bash
# Basic resources usage report
vmware-vra report resources-usage

# Fast report without detailed resource fetching
vmware-vra report resources-usage --no-detailed-resources

# Report for specific project, grouped by resource type
vmware-vra report resources-usage --project abc123 --group-by resource-type

# Detailed report sorted by resource count
vmware-vra report resources-usage --sort-by resource-count --detailed-resources
```

**Sample Output (Table):**
```
📊 Generating Resources Usage Report...
⚠️  Detailed resource fetching enabled - this may take longer for many deployments

📈 Resource Usage Summary
Total Deployments             156    All deployments in scope
Linked Deployments             134    Linked to catalog items
Unlinked Deployments            22    Cannot link to catalog items

Total Resources               1,234   Across all deployments
Unique Resource Types            8    Different resource types found
Unique Catalog Items            12    Catalog items with deployments
Avg Resources per Deployment   7.9   Average resource density

🔧 Resource Type Breakdown
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Resource Type                    ┃ Count ┃ Percentage ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Cloud.vSphere.Machine            │   345 │     28.0%  │
│ Cloud.vSphere.Disk               │   278 │     22.5%  │
│ Cloud.vSphere.Network            │   189 │     15.3%  │
│ Cloud.NSX.SecurityGroup          │   156 │     12.6%  │
│ Cloud.LoadBalancer               │    98 │      7.9%  │
│ Cloud.Storage.Volume             │    87 │      7.1%  │
│ Cloud.Database                   │    56 │      4.5%  │
│ Other                            │    25 │      2.0%  │
└──────────────────────────────────┴───────┴────────────┘
```

### `report unsync`

Generate unsynced deployments report.

**Syntax:**
```bash
vmware-vra report unsync [OPTIONS]
```

**Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--project` | TEXT | None | Filter by project ID |
| `--detailed-resources` | FLAG | False | Fetch exact resource counts |
| `--show-details` | FLAG | False | Show detailed analysis |
| `--reason-filter` | TEXT | None | Filter by specific reason |

**Examples:**
```bash
# Basic unsync report
vmware-vra report unsync

# Detailed analysis
vmware-vra report unsync --show-details

# Filter by specific reason
vmware-vra report unsync --reason-filter catalog_item_deleted
```

## Workflow Commands (`workflow`)

Manage and execute workflows.

### `workflow list`

List available workflows.

**Syntax:**
```bash
vmware-vra workflow list [OPTIONS]
```

**Options:**
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--page-size` | INT | 100 | Items per page (max: 2000) |
| `--first-page-only` | FLAG | False | Fetch only first page |

**Example:**
```bash
vmware-vra workflow list
```

### `workflow run`

Execute a workflow.

**Syntax:**
```bash
vmware-vra workflow run WORKFLOW_ID [OPTIONS]
```

**Options:**
| Option | Type | Description |
|--------|------|-------------|
| `--inputs` | TEXT | Input parameters as JSON string |
| `--inputs-file` | PATH | Input parameters from YAML/JSON file |

**Examples:**
```bash
# Run workflow with inline inputs
vmware-vra workflow run create-user-workflow \
    --inputs '{"username": "john.doe", "department": "IT"}'

# Run workflow with inputs file
vmware-vra workflow run create-user-workflow \
    --inputs-file user-inputs.yaml
```

## Output Formats

All list and show commands support three output formats:

### Table Format (Default)

Human-readable tables with aligned columns and formatting.

```bash
vmware-vra catalog list
```

### JSON Format

Machine-readable JSON for scripting and automation.

```bash
vmware-vra --format json catalog list
```

### YAML Format

Human-readable YAML format.

```bash
vmware-vra --format yaml catalog list
```

## Environment Variables

Override configuration using environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `VRA_URL` | vRA server URL | `https://vra.company.com` |
| `VRA_TENANT` | vRA tenant | `company.local` |
| `VRA_DOMAIN` | Authentication domain | `vsphere.local` |
| `VRA_VERIFY_SSL` | SSL verification | `true` or `false` |
| `VRA_TIMEOUT` | Request timeout | `60` |

**Example:**
```bash
export VRA_URL="https://vra-dev.company.com"
export VRA_TENANT="dev.company.local"
vmware-vra catalog list
```

## Common Usage Patterns

### Automation Scripts

```bash
#!/bin/bash
set -e

# Authenticate
vmware-vra auth login \
    --username "$VRA_USERNAME" \
    --password "$VRA_PASSWORD" \
    --url "$VRA_URL"

# Deploy infrastructure
DEPLOYMENT_ID=$(vmware-vra catalog request blueprint-web-app \
    --project "$PROJECT_ID" \
    --inputs-file webapp-config.yaml \
    --format json | jq -r '.deploymentId')

echo "Deployment created: $DEPLOYMENT_ID"

# Wait for deployment completion (custom logic)
while true; do
    STATUS=$(vmware-vra deployment show "$DEPLOYMENT_ID" --format json | jq -r '.status')
    if [[ "$STATUS" == "CREATE_SUCCESSFUL" ]]; then
        echo "Deployment completed successfully"
        break
    elif [[ "$STATUS" == "CREATE_FAILED" ]]; then
        echo "Deployment failed"
        exit 1
    fi
    sleep 30
done
```

### Batch Operations

```bash
#!/bin/bash
# Tag multiple deployments

DEPLOYMENTS=$(vmware-vra deployment list --format json | jq -r '.[].id')
TAG_ID="tag-environment-prod"

for deployment in $DEPLOYMENTS; do
    echo "Tagging deployment: $deployment"
    vmware-vra tag assign "$deployment" "$TAG_ID" --confirm
done
```

### Data Export Pipeline

```bash
#!/bin/bash
# Complete data export and analysis

EXPORT_DIR="/backup/vra/$(date +%Y-%m-%d)"
mkdir -p "$EXPORT_DIR"

# Export deployments
vmware-vra deployment export-all \
    --output-dir "$EXPORT_DIR" \
    --include-resources

# Generate reports
vmware-vra report catalog-usage --format json > "$EXPORT_DIR/catalog-usage.json"
vmware-vra report unsync --format json > "$EXPORT_DIR/unsync-report.json"
vmware-vra report activity-timeline --days-back 90 --format json > "$EXPORT_DIR/activity-timeline.json"

# Create summary
echo "Export completed: $EXPORT_DIR"
echo "Files created:"
ls -la "$EXPORT_DIR"
```

This comprehensive CLI reference provides complete coverage of all available commands, options, and usage patterns for the VMware vRA CLI tool.
