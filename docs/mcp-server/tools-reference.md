# MCP Tools Reference

Complete reference for all 26 tools available in the VMware vRA MCP server.

## Tool Categories

- [Authentication Tools](#authentication-tools) (1 tool)
- [Catalog Management Tools](#catalog-management-tools) (4 tools)
- [Schema Catalog Tools](#schema-catalog-tools) (8 tools)
- [Deployment Management Tools](#deployment-management-tools) (4 tools)
- [Advanced Reporting Tools](#advanced-reporting-tools) (4 tools)
- [Workflow Management Tools](#workflow-management-tools) (5 tools)

---

## Authentication Tools

### vra_authenticate

Authenticate to VMware vRA server and store credentials securely.

**Parameters:**
- `username` (required): vRA username
- `password` (required): User password
- `url` (required): vRA server URL (e.g., "https://vra.company.com")
- `tenant` (optional): Tenant domain
- `domain` (optional): Authentication domain

**Example:**
```json
{
  "username": "admin@corp.local",
  "password": "SecurePassword123",
  "url": "https://vra.company.com",
  "tenant": "corp.local",
  "domain": "vsphere.local"
}
```

**Response:**
```
Successfully authenticated to https://vra.company.com
```

---

## Catalog Management Tools

### vra_list_catalog_items

List VMware vRA catalog items with optional filtering.

**Parameters:**
- `project_id` (optional): Filter by project ID
- `page_size` (optional): Number of items per page (default: 100)
- `first_page_only` (optional): Fetch only first page (default: false)

**Example:**
```json
{
  "project_id": "dev-project-123",
  "page_size": 50,
  "first_page_only": false
}
```

**Response:**
```
Found 25 catalog items:
[
  {
    "id": "blueprint-ubuntu-20",
    "name": "Ubuntu Server 20.04",
    "type": "com.vmw.blueprint",
    ...
  }
]
```

### vra_get_catalog_item

Get details of a specific catalog item.

**Parameters:**
- `item_id` (required): Catalog item ID

**Example:**
```json
{
  "item_id": "blueprint-ubuntu-20"
}
```

### vra_get_catalog_item_schema

Get request schema for a catalog item.

**Parameters:**
- `item_id` (required): Catalog item ID

**Example:**
```json
{
  "item_id": "blueprint-ubuntu-20"
}
```

### vra_request_catalog_item

Request a catalog item deployment.

**Parameters:**
- `item_id` (required): Catalog item ID
- `project_id` (required): Project ID
- `inputs` (optional): Input parameters for the catalog item
- `reason` (optional): Reason for the request
- `name` (optional): Deployment name

**Example:**
```json
{
  "item_id": "blueprint-ubuntu-20",
  "project_id": "dev-project-123",
  "inputs": {
    "cpu_count": 4,
    "memory_gb": 8
  },
  "name": "web-server-001"
}
```

---

## Schema Catalog Tools

### vra_schema_load_schemas

Load catalog schemas from JSON files into persistent cache.

**Parameters:**
- `pattern` (optional): File pattern to match schema files (default: "*_schema.json")
- `force_reload` (optional): Force reload even if already loaded (default: false)

**Example:**
```json
{
  "pattern": "*_schema.json",
  "force_reload": false
}
```

**Response:**
```
Successfully loaded 73 catalog schemas from persistent cache
```

### vra_schema_list_schemas

List available catalog schemas from cache.

**Parameters:**
- `item_type` (optional): Filter by catalog item type
- `name_filter` (optional): Filter by name (case-insensitive substring match)

**Example:**
```json
{
  "name_filter": "VM"
}
```

**Response:**
```
Found 12 catalog schemas:
[
  {
    "id": "blueprint-ubuntu-20",
    "name": "Ubuntu Server 20.04",
    "type": "com.vmw.blueprint",
    "description": "Ubuntu 20.04 LTS server template"
  }
]
```

### vra_schema_search_schemas

Search catalog schemas by name or description.

**Parameters:**
- `query` (required): Search query (case-insensitive)

**Example:**
```json
{
  "query": "security group"
}
```

**Response:**
```
Found 5 schemas matching 'security group':
[...]
```

### vra_schema_show_schema

Show detailed schema information for a catalog item.

**Parameters:**
- `catalog_item_id` (required): Catalog item ID

**Example:**
```json
{
  "catalog_item_id": "blueprint-ubuntu-20"
}
```

**Response:**
```json
{
  "catalog_item": {
    "id": "blueprint-ubuntu-20",
    "name": "Ubuntu Server 20.04",
    "type": "com.vmw.blueprint",
    "description": "Ubuntu 20.04 LTS server template"
  },
  "fields": [
    {
      "name": "cpu_count",
      "title": "CPU Count",
      "type": "integer",
      "required": true,
      "description": "Number of CPU cores"
    }
  ]
}
```

### vra_schema_execute_schema

Execute a catalog item using its schema with AI-guided input collection.

**Parameters:**
- `catalog_item_id` (required): Catalog item ID
- `project_id` (required): vRA project ID
- `deployment_name` (optional): Custom deployment name
- `inputs` (optional): Input values dictionary
- `dry_run` (optional): Validate inputs without executing (default: false)

**Example:**
```json
{
  "catalog_item_id": "blueprint-ubuntu-20",
  "project_id": "dev-project-123",
  "deployment_name": "web-server-001",
  "inputs": {
    "cpu_count": 4,
    "memory_gb": 8,
    "disk_size": 100
  },
  "dry_run": false
}
```

**Response:**
```
Successfully executed Ubuntu Server 20.04
Deployment ID: dep-12345-abcdef
Request ID: req-789-xyz
Deployment Name: web-server-001
```

### vra_schema_generate_template

Generate input template for a catalog item.

**Parameters:**
- `catalog_item_id` (required): Catalog item ID
- `project_id` (required): vRA project ID

**Example:**
```json
{
  "catalog_item_id": "blueprint-ubuntu-20",
  "project_id": "dev-project-123"
}
```

**Response:**
```json
{
  "_metadata": {
    "catalog_item_id": "blueprint-ubuntu-20",
    "catalog_item_name": "Ubuntu Server 20.04",
    "project_id": "dev-project-123"
  },
  "cpu_count": 2,
  "memory_gb": 4,
  "disk_size": 50
}
```

### vra_schema_clear_cache

Clear the persistent schema registry cache.

**Parameters:** None

**Example:**
```json
{}
```

**Response:**
```
Schema cache cleared successfully
```

### vra_schema_registry_status

Show schema registry status and statistics.

**Parameters:** None

**Example:**
```json
{}
```

**Response:**
```json
{
  "total_schemas": 73,
  "schema_directories": 2,
  "types": {
    "com.vmw.blueprint": 45,
    "com.vmware.csp.iaas.blueprint.service": 28
  },
  "directories": [
    "/path/to/inputs/schema_exports",
    "/home/user/.vmware-vra-cli/schemas"
  ]
}
```

---

## Deployment Management Tools

### vra_list_deployments

List VMware vRA deployments with filtering.

**Parameters:**
- `project_id` (optional): Filter by project ID
- `status` (optional): Filter by status
- `page_size` (optional): Number of items per page (default: 100)
- `first_page_only` (optional): Fetch only first page (default: false)

**Example:**
```json
{
  "project_id": "dev-project-123",
  "status": "CREATE_SUCCESSFUL",
  "page_size": 50
}
```

### vra_get_deployment

Get details of a specific deployment.

**Parameters:**
- `deployment_id` (required): Deployment ID

**Example:**
```json
{
  "deployment_id": "dep-12345-abcdef"
}
```

### vra_get_deployment_resources

Get resources of a specific deployment.

**Parameters:**
- `deployment_id` (required): Deployment ID

**Example:**
```json
{
  "deployment_id": "dep-12345-abcdef"
}
```

**Response:**
```json
{
  "deployment_id": "dep-12345-abcdef",
  "deployment_name": "web-server-001",
  "resources": [
    {
      "id": "vm-789-xyz",
      "name": "web-server-001-vm",
      "type": "Cloud.vSphere.Machine",
      "status": "SUCCESS"
    }
  ]
}
```

### vra_delete_deployment

Delete a deployment.

**Parameters:**
- `deployment_id` (required): Deployment ID
- `confirm` (optional): Confirm deletion (default: true)

**Example:**
```json
{
  "deployment_id": "dep-12345-abcdef",
  "confirm": true
}
```

**Response:**
```
Deployment deletion initiated: dep-12345-abcdef
```

---

## Advanced Reporting Tools

### vra_report_activity_timeline

Generate deployment activity timeline report.

**Parameters:**
- `project_id` (optional): Filter by project ID
- `days_back` (optional): Days back for activity timeline (1-365, default: 30)
- `group_by` (optional): Group results by time period ("day", "week", "month", "year", default: "day")
- `statuses` (optional): Comma-separated list of statuses to include

**Example:**
```json
{
  "days_back": 90,
  "group_by": "week",
  "project_id": "dev-project-123"
}
```

**Response:**
```
📈 Activity Timeline Report (90 days, grouped by week)

📊 Summary:
• Total deployments: 145
• Successful: 132
• Failed: 8
• In progress: 5
• Success rate: 91.0%
• Trend: increasing (15.3%)
...
```

### vra_report_catalog_usage

Generate catalog usage report with deployment statistics.

**Parameters:**
- `project_id` (optional): Filter by project ID
- `include_zero` (optional): Include catalog items with zero deployments (default: false)
- `sort_by` (optional): Sort results by field ("deployments", "resources", "name", default: "deployments")
- `detailed_resources` (optional): Fetch exact resource counts (default: false)

**Example:**
```json
{
  "include_zero": false,
  "sort_by": "deployments",
  "detailed_resources": true
}
```

**Response:**
```
📊 Catalog Usage Report

📈 Summary:
• Total catalog items shown: 12
• Active items (with deployments): 8
• Total deployments (system-wide): 156
• Catalog-linked deployments: 145
...
```

### vra_report_resources_usage

Generate comprehensive resources usage report.

**Parameters:**
- `project_id` (optional): Filter by project ID
- `detailed_resources` (optional): Fetch detailed resource information (default: true)
- `sort_by` (optional): Sort deployments by field ("deployment-name", "catalog-item", "resource-count", "status", default: "catalog-item")
- `group_by` (optional): Group results by field ("catalog-item", "resource-type", "deployment-status", default: "catalog-item")

**Example:**
```json
{
  "detailed_resources": true,
  "sort_by": "resource-count",
  "group_by": "resource-type"
}
```

**Response:**
```
🔧 Resources Usage Report

📈 Summary:
• Total deployments: 156
• Total resources: 487
• Unique resource types: 12
...
```

### vra_report_unsync

Generate report of deployments not linked to catalog items.

**Parameters:**
- `project_id` (optional): Filter by project ID
- `detailed_resources` (optional): Fetch exact resource counts (default: false)
- `reason_filter` (optional): Filter by specific reason

**Example:**
```json
{
  "detailed_resources": false,
  "project_id": "dev-project-123"
}
```

**Response:**
```
🔍 Unsynced Deployments Report

📊 Summary:
• Total deployments: 156
• Linked deployments: 145
• ⚠️  Unsynced deployments: 11
• Unsynced percentage: 7.1%
...
```

---

## Workflow Management Tools

### vra_list_workflows

List available vRealize Orchestrator workflows.

**Parameters:**
- `page_size` (optional): Number of items per page (1-2000, default: 100)
- `first_page_only` (optional): Fetch only the first page (default: false)

**Example:**
```json
{
  "page_size": 50,
  "first_page_only": false
}
```

**Response:**
```
🔄 Available Workflows

Found 23 workflows:

1. Backup Virtual Machine
   • ID: workflow-backup-vm
   • Description: Create backup snapshot of VM
...
```

### vra_get_workflow_schema

Get workflow input/output schema.

**Parameters:**
- `workflow_id` (required): Workflow ID

**Example:**
```json
{
  "workflow_id": "workflow-backup-vm"
}
```

**Response:**
```
🔧 Workflow Schema: workflow-backup-vm

Name: Backup Virtual Machine
Description: Create backup snapshot of VM
Version: 1.2.0

📥 Input Parameters (3):
• vm_name (string): Name of the virtual machine
• snapshot_name (string): Name for the snapshot
• include_memory (boolean): Include VM memory in snapshot
...
```

### vra_run_workflow

Execute a workflow with given inputs.

**Parameters:**
- `workflow_id` (required): Workflow ID
- `inputs` (optional): Input parameters for the workflow

**Example:**
```json
{
  "workflow_id": "workflow-backup-vm",
  "inputs": {
    "vm_name": "web-server-001",
    "snapshot_name": "backup-2024-01-15",
    "include_memory": true
  }
}
```

**Response:**
```
▶️ Workflow Execution Started

• Workflow ID: workflow-backup-vm
• Execution ID: exec-789-def456
• Name: Backup Virtual Machine
• State: running
...
```

### vra_get_workflow_run

Get workflow execution details.

**Parameters:**
- `workflow_id` (required): Workflow ID
- `execution_id` (required): Execution ID

**Example:**
```json
{
  "workflow_id": "workflow-backup-vm",
  "execution_id": "exec-789-def456"
}
```

**Response:**
```
📊 Workflow Execution Details

• Execution ID: exec-789-def456
• State: completed
• Duration: 7 minutes 30 seconds
• Status: success
...
```

### vra_cancel_workflow_run

Cancel a running workflow execution.

**Parameters:**
- `workflow_id` (required): Workflow ID
- `execution_id` (required): Execution ID

**Example:**
```json
{
  "workflow_id": "workflow-backup-vm",
  "execution_id": "exec-789-def456"
}
```

**Response:**
```
✋ Workflow Execution Cancelled

• Execution ID: exec-789-def456
• Previous State: running
• Current State: cancelled
```

---

## Error Handling

All tools return consistent error responses when issues occur:

```json
{
  "type": "text",
  "text": "Error message here",
  "isError": true
}
```

**Common Error Scenarios:**
- **Authentication Required**: "Not authenticated. Please run vra_authenticate first."
- **Invalid Parameters**: "Tool execution error: [specific error]"
- **API Errors**: "Failed to [action]: [error details]"

## Usage Tips

1. **Always authenticate first** using `vra_authenticate`
2. **Load schemas for enhanced functionality** with `vra_schema_load_schemas`
3. **Use schema tools for guided deployments** - they provide better validation and user experience
4. **Leverage reporting tools** for insights into your vRA environment
5. **Use dry_run mode** in schema_execute_schema to validate inputs before deployment

## Integration Examples

### Claude Desktop
```json
{
  "mcpServers": {
    "vmware-vra": {
      "command": "vra-mcp-server",
      "env": {
        "VRA_URL": "https://vra.company.com"
      }
    }
  }
}
```

### VS Code Continue
```json
{
  "mcp": {
    "servers": {
      "vmware-vra": {
        "command": "vra-mcp-server"
      }
    }
  }
}
```
