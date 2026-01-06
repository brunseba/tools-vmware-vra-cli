# MCP Tools Reference

Complete reference for all 26+ tools available in the VMware vRA MCP server.

## Tool Categories

- [Authentication Tools](#authentication-tools) (4 tools)
- [Catalog Management Tools](#catalog-management-tools) (4 tools)  
- [Deployment Management Tools](#deployment-management-tools) (5 tools)
- [Advanced Reporting Tools](#advanced-reporting-tools) (4 tools)
- [Workflow Management Tools](#workflow-management-tools) (5 tools)
- [Tag Management Tools](#tag-management-tools) (4 tools)

---

## Authentication Tools

### vra_auth_login

Authenticate with VMware vRA and store credentials securely.

**Parameters:**
- `username` (required): vRA username (e.g., "admin@corp.local")
- `password` (required): User password
- `url` (required): vRA server URL (e.g., "https://vra.company.com")
- `tenant` (optional): Tenant domain (default: from URL)
- `domain` (optional): Authentication domain (default: "vsphere.local")

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
```json
{
  "success": true,
  "message": "Authentication successful",
  "token_stored": true,
  "expires_at": "2024-01-15T14:30:00Z"
}
```

### vra_auth_logout

Clear stored authentication tokens and credentials.

**Parameters:** None

**Example:**
```json
{}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully logged out"
}
```

### vra_auth_status

Check current authentication status and token validity.

**Parameters:** None

**Example:**
```json
{}
```

**Response:**
```json
{
  "authenticated": true,
  "username": "admin@corp.local",
  "server": "https://vra.company.com",
  "tenant": "corp.local",
  "token_expires": "2024-01-15T14:30:00Z",
  "time_remaining": "2 hours 15 minutes"
}
```

### vra_auth_refresh

Refresh the current authentication token.

**Parameters:** None

**Example:**
```json
{}
```

**Response:**
```json
{
  "success": true,
  "message": "Token refreshed successfully",
  "expires_at": "2024-01-15T16:30:00Z"
}
```

---

## Catalog Management Tools

### vra_list_catalog_items

List available catalog items with optional filtering.

**Parameters:**
- `project_id` (optional): Filter by project ID
- `page_size` (optional): Items per page (1-2000, default: 100)
- `first_page_only` (optional): Fetch only first page (default: false)
- `verbose` (optional): Enable verbose logging (default: false)

**Example:**
```json
{
  "project_id": "dev-project-123",
  "page_size": 50,
  "first_page_only": false
}
```

**Response:**
```json
{
  "success": true,
  "items": [
    {
      "id": "blueprint-ubuntu-20",
      "name": "Ubuntu Server 20.04",
      "type": "com.vmw.blueprint",
      "status": "PUBLISHED",
      "version": "2.1",
      "description": "Ubuntu 20.04 LTS server template"
    }
  ],
  "total_count": 25,
  "page_info": {
    "page_size": 50,
    "current_page": 1,
    "total_pages": 1
  }
}
```

### vra_get_catalog_item

Get detailed information about a specific catalog item.

**Parameters:**
- `catalog_item_id` (required): Catalog item identifier

**Example:**
```json
{
  "catalog_item_id": "blueprint-ubuntu-20"
}
```

**Response:**
```json
{
  "success": true,
  "catalog_item": {
    "id": "blueprint-ubuntu-20",
    "name": "Ubuntu Server 20.04",
    "type": "com.vmw.blueprint",
    "status": "PUBLISHED",
    "version": "2.1",
    "description": "Ubuntu 20.04 LTS server template",
    "created_by": "admin@corp.local",
    "created_at": "2024-01-10T10:00:00Z",
    "projects": ["dev-project-123"],
    "form": {
      "layout": {
        "pages": [
          {
            "title": "General",
            "sections": [
              {
                "fields": ["cpu_count", "memory_gb", "disk_size"]
              }
            ]
          }
        ]
      }
    }
  }
}
```

### vra_get_catalog_item_schema

Get the request schema for a catalog item, including input parameters and validation rules.

**Parameters:**
- `catalog_item_id` (required): Catalog item identifier

**Example:**
```json
{
  "catalog_item_id": "blueprint-ubuntu-20"
}
```

**Response:**
```json
{
  "success": true,
  "schema": {
    "catalog_item_id": "blueprint-ubuntu-20",
    "name": "Ubuntu Server 20.04",
    "inputs": {
      "cpu_count": {
        "type": "integer",
        "title": "CPU Count",
        "description": "Number of CPU cores",
        "default": 2,
        "minimum": 1,
        "maximum": 8
      },
      "memory_gb": {
        "type": "integer", 
        "title": "Memory (GB)",
        "description": "RAM allocation in GB",
        "default": 4,
        "minimum": 2,
        "maximum": 32
      },
      "disk_size": {
        "type": "integer",
        "title": "Disk Size (GB)",
        "description": "Primary disk size",
        "default": 50,
        "minimum": 20,
        "maximum": 500
      }
    },
    "required_inputs": ["cpu_count", "memory_gb"]
  }
}
```

### vra_request_catalog_item

Request deployment of a catalog item with specified parameters.

**Parameters:**
- `catalog_item_id` (required): Catalog item to deploy
- `project_id` (required): Target project ID
- `name` (required): Deployment name
- `description` (optional): Deployment description
- `inputs` (optional): Input parameters for the deployment
- `version` (optional): Specific catalog item version

**Example:**
```json
{
  "catalog_item_id": "blueprint-ubuntu-20",
  "project_id": "dev-project-123", 
  "name": "web-server-001",
  "description": "Development web server",
  "inputs": {
    "cpu_count": 4,
    "memory_gb": 8,
    "disk_size": 100,
    "environment": "development"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Deployment request submitted successfully",
  "deployment_id": "dep-12345-abcdef",
  "deployment_name": "web-server-001",
  "status": "CREATE_INPROGRESS",
  "estimated_completion": "5-10 minutes"
}
```

---

## Deployment Management Tools

### vra_list_deployments

List deployments with comprehensive filtering options.

**Parameters:**
- `project_id` (optional): Filter by project ID
- `status` (optional): Filter by deployment status
- `page_size` (optional): Items per page (1-2000, default: 100)
- `first_page_only` (optional): Fetch only first page (default: false)
- `verbose` (optional): Enable verbose logging (default: false)

**Example:**
```json
{
  "project_id": "dev-project-123",
  "status": "CREATE_SUCCESSFUL",
  "page_size": 20
}
```

**Response:**
```json
{
  "success": true,
  "deployments": [
    {
      "id": "dep-12345-abcdef",
      "name": "web-server-001",
      "status": "CREATE_SUCCESSFUL",
      "project_id": "dev-project-123",
      "project_name": "Development Project",
      "catalog_item_id": "blueprint-ubuntu-20",
      "catalog_item_name": "Ubuntu Server 20.04",
      "created_at": "2024-01-15T10:00:00Z",
      "created_by": "developer@corp.local",
      "resource_count": 3
    }
  ],
  "total_count": 45,
  "filter_info": {
    "project_id": "dev-project-123",
    "status_filter": "CREATE_SUCCESSFUL"
  }
}
```

### vra_get_deployment

Get detailed information about a specific deployment.

**Parameters:**
- `deployment_id` (required): Deployment identifier

**Example:**
```json
{
  "deployment_id": "dep-12345-abcdef"
}
```

**Response:**
```json
{
  "success": true,
  "deployment": {
    "id": "dep-12345-abcdef",
    "name": "web-server-001",
    "description": "Development web server",
    "status": "CREATE_SUCCESSFUL",
    "project_id": "dev-project-123",
    "project_name": "Development Project",
    "catalog_item_id": "blueprint-ubuntu-20",
    "catalog_item_name": "Ubuntu Server 20.04",
    "created_at": "2024-01-15T10:00:00Z",
    "created_by": "developer@corp.local",
    "last_updated": "2024-01-15T10:15:00Z",
    "inputs": {
      "cpu_count": 4,
      "memory_gb": 8,
      "disk_size": 100
    },
    "resource_count": 3,
    "expense": {
      "total_cost": 145.50,
      "currency": "USD"
    }
  }
}
```

### vra_delete_deployment

Delete a deployment and all its resources.

**Parameters:**
- `deployment_id` (required): Deployment to delete

**Example:**
```json
{
  "deployment_id": "dep-12345-abcdef"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Deployment deletion initiated",
  "deployment_id": "dep-12345-abcdef",
  "deployment_name": "web-server-001",
  "status": "DELETE_INPROGRESS",
  "estimated_completion": "3-5 minutes"
}
```

### vra_get_deployment_resources

Get all resources associated with a deployment.

**Parameters:**
- `deployment_id` (required): Deployment identifier

**Example:**
```json
{
  "deployment_id": "dep-12345-abcdef"
}
```

**Response:**
```json
{
  "success": true,
  "deployment_id": "dep-12345-abcdef",
  "deployment_name": "web-server-001",
  "resources": [
    {
      "id": "vm-789-xyz",
      "name": "web-server-001-vm",
      "type": "Cloud.vSphere.Machine",
      "status": "SUCCESS",
      "properties": {
        "address": "192.168.1.100",
        "cpu_count": 4,
        "memory_mb": 8192,
        "power_state": "poweredOn"
      }
    },
    {
      "id": "net-456-abc", 
      "name": "web-server-network",
      "type": "Cloud.vSphere.Network",
      "status": "SUCCESS",
      "properties": {
        "network_type": "existing",
        "assignment": "static"
      }
    }
  ],
  "resource_count": 2,
  "resource_types": ["Cloud.vSphere.Machine", "Cloud.vSphere.Network"]
}
```

### vra_export_deployments

Export deployment data for backup, analysis, or migration.

**Parameters:**
- `project_id` (optional): Filter by project ID
- `format` (optional): Export format ("json" or "csv", default: "json")
- `include_resources` (optional): Include detailed resource info (default: false)

**Example:**
```json
{
  "project_id": "dev-project-123",
  "format": "json",
  "include_resources": true
}
```

**Response:**
```json
{
  "success": true,
  "export_data": {
    "export_timestamp": "2024-01-15T11:00:00Z",
    "project_filter": "dev-project-123",
    "total_deployments": 12,
    "deployments": [
      {
        "id": "dep-12345-abcdef",
        "name": "web-server-001",
        "catalog_item": "Ubuntu Server 20.04",
        "status": "CREATE_SUCCESSFUL",
        "created_at": "2024-01-15T10:00:00Z",
        "resources": [
          {
            "name": "web-server-001-vm",
            "type": "Cloud.vSphere.Machine",
            "address": "192.168.1.100"
          }
        ]
      }
    ]
  },
  "summary": {
    "total_exports": 12,
    "total_resources": 28,
    "unique_catalog_items": 5
  }
}
```

---

## Advanced Reporting Tools

### vra_report_activity_timeline

Generate comprehensive activity timeline with trends and peak analysis.

**Parameters:**
- `project_id` (optional): Filter by project ID
- `days_back` (optional): Days back for analysis (1-365, default: 30)
- `group_by` (optional): Time grouping ("day", "week", "month", "year", default: "day")
- `statuses` (optional): Comma-separated status list

**Example:**
```json
{
  "days_back": 90,
  "group_by": "week",
  "project_id": "dev-project-123"
}
```

**Response:**
```json
{
  "success": true,
  "timeline_data": {
    "period": "90 days",
    "grouping": "week",
    "summary": {
      "total_deployments": 145,
      "successful_deployments": 132,
      "failed_deployments": 8,
      "in_progress_deployments": 5,
      "success_rate": 91.0,
      "trend": "increasing",
      "trend_percentage": 15.3,
      "peak_activity_period": "2024-W03",
      "peak_activity_count": 23,
      "unique_catalog_items": 8,
      "unique_projects": 3
    },
    "period_activity": {
      "2024-W01": {
        "total_deployments": 18,
        "successful_deployments": 16,
        "failed_deployments": 2,
        "unique_catalog_items": 4
      },
      "2024-W02": {
        "total_deployments": 21,
        "successful_deployments": 19,
        "failed_deployments": 1,
        "unique_catalog_items": 5
      }
    }
  },
  "insights": [
    "Deployment activity increased by 15.3% over the period",
    "Peak activity was in week 3 with 23 deployments",
    "Success rate of 91% is above industry average"
  ]
}
```

### vra_report_catalog_usage

Generate detailed catalog usage statistics with deployment and resource analysis.

**Parameters:**
- `project_id` (optional): Filter by project ID
- `include_zero` (optional): Include items with zero deployments (default: false)
- `sort_by` (optional): Sort by ("deployments", "resources", "name", default: "deployments")
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
```json
{
  "success": true,
  "usage_stats": [
    {
      "id": "blueprint-ubuntu-20",
      "name": "Ubuntu Server 20.04",
      "type": "com.vmw.blueprint",
      "deployment_count": 45,
      "resource_count": 135,
      "success_count": 42,
      "failed_count": 2,
      "in_progress_count": 1,
      "success_rate": 93.3,
      "avg_deployment_time": "8.5 minutes",
      "total_cost": 4567.89,
      "status_breakdown": {
        "CREATE_SUCCESSFUL": 42,
        "CREATE_FAILED": 2,
        "CREATE_INPROGRESS": 1
      }
    }
  ],
  "summary": {
    "total_catalog_items": 12,
    "active_items": 8,
    "total_deployments_system_wide": 156,
    "catalog_linked_deployments": 145,
    "unlinked_deployments": 11,
    "total_resources": 487,
    "average_deployments_per_active_item": 18.1,
    "total_system_cost": 15678.45
  },
  "recommendations": [
    "blueprint-ubuntu-20 has highest usage - consider optimization",
    "11 unlinked deployments found - review governance policies"
  ]
}
```

### vra_report_resources_usage

Generate comprehensive resource usage analysis across all deployments.

**Parameters:**
- `project_id` (optional): Filter by project ID
- `detailed_resources` (optional): Fetch detailed resource info (default: true)
- `sort_by` (optional): Sort by ("deployment-name", "catalog-item", "resource-count", "status")
- `group_by` (optional): Group by ("catalog-item", "resource-type", "deployment-status")

**Example:**
```json
{
  "detailed_resources": true,
  "sort_by": "resource-count",
  "group_by": "resource-type"
}
```

**Response:**
```json
{
  "success": true,
  "report_data": {
    "summary": {
      "total_deployments": 156,
      "total_resources": 487,
      "unique_resource_types": 12,
      "resource_type_breakdown": {
        "Cloud.vSphere.Machine": 145,
        "Cloud.vSphere.Network": 89,
        "Cloud.vSphere.Disk": 134,
        "Cloud.LoadBalancer": 12
      }
    },
    "deployment_analysis": [
      {
        "deployment_id": "dep-12345-abcdef",
        "deployment_name": "web-server-001",
        "catalog_item": "Ubuntu Server 20.04",
        "status": "CREATE_SUCCESSFUL",
        "resource_count": 5,
        "resources_by_type": {
          "Cloud.vSphere.Machine": 2,
          "Cloud.vSphere.Network": 1,
          "Cloud.vSphere.Disk": 2
        },
        "total_cost": 234.56
      }
    ],
    "resource_utilization": {
      "compute_resources": {
        "total_vcpus": 456,
        "total_memory_gb": 1824,
        "avg_cpu_per_vm": 3.1,
        "avg_memory_per_vm": 12.6
      },
      "storage_resources": {
        "total_disk_gb": 12450,
        "avg_disk_per_vm": 85.9
      }
    }
  },
  "insights": [
    "Average 3.1 resources per deployment",
    "Cloud.vSphere.Machine is most common resource type",
    "Total compute: 456 vCPUs, 1.8TB RAM"
  ]
}
```

### vra_report_unsync

Analyze deployments not linked to catalog items with root cause analysis.

**Parameters:**
- `project_id` (optional): Filter by project ID
- `detailed_resources` (optional): Include resource details (default: false)
- `reason_filter` (optional): Filter by specific reason

**Example:**
```json
{
  "detailed_resources": true,
  "project_id": "dev-project-123"
}
```

**Response:**
```json
{
  "success": true,
  "unsync_analysis": {
    "summary": {
      "total_unsynced_deployments": 11,
      "percentage_unsynced": 7.1,
      "total_affected_resources": 28,
      "estimated_cost_impact": 1234.56
    },
    "root_causes": {
      "catalog_item_deleted": 6,
      "manual_deployment": 3,
      "import_from_external": 2
    },
    "unsynced_deployments": [
      {
        "deployment_id": "dep-orphan-123",
        "deployment_name": "legacy-system-vm",
        "status": "CREATE_SUCCESSFUL",
        "created_at": "2023-12-01T10:00:00Z",
        "age_days": 45,
        "resource_count": 3,
        "likely_reason": "catalog_item_deleted",
        "recommended_action": "Link to similar catalog item or archive",
        "resources": [
          {
            "name": "legacy-vm-001",
            "type": "Cloud.vSphere.Machine",
            "status": "SUCCESS"
          }
        ]
      }
    ]
  },
  "remediation_suggestions": [
    "Review and link 6 deployments with deleted catalog items",
    "Consider creating catalog items for 3 manual deployments",
    "Archive or document 2 imported deployments"
  ]
}
```

---

## Workflow Management Tools

### vra_list_workflows

List available vRealize Orchestrator workflows.

**Parameters:**
- `page_size` (optional): Items per page (1-2000, default: 100)
- `first_page_only` (optional): Fetch only first page (default: false)
- `verbose` (optional): Enable verbose logging (default: false)

**Example:**
```json
{
  "page_size": 50,
  "first_page_only": false
}
```

**Response:**
```json
{
  "success": true,
  "workflows": [
    {
      "id": "workflow-backup-vm",
      "name": "Backup Virtual Machine",
      "description": "Create backup snapshot of VM",
      "version": "1.2.0",
      "category": "com.vmware.library.vc.vm",
      "input_parameters": 3,
      "output_parameters": 1
    }
  ],
  "total_count": 23,
  "page_info": {
    "page_size": 50,
    "current_page": 1,
    "total_pages": 1
  }
}
```

### vra_get_workflow_schema

Get workflow input/output schema and parameter definitions.

**Parameters:**
- `workflow_id` (required): Workflow identifier

**Example:**
```json
{
  "workflow_id": "workflow-backup-vm"
}
```

**Response:**
```json
{
  "success": true,
  "workflow_schema": {
    "id": "workflow-backup-vm",
    "name": "Backup Virtual Machine",
    "description": "Create backup snapshot of VM",
    "version": "1.2.0",
    "input_parameters": [
      {
        "name": "vm_name",
        "type": "string",
        "description": "Name of the virtual machine",
        "required": true
      },
      {
        "name": "snapshot_name",
        "type": "string",
        "description": "Name for the snapshot",
        "required": true
      },
      {
        "name": "include_memory",
        "type": "boolean",
        "description": "Include VM memory in snapshot",
        "required": false,
        "default": false
      }
    ],
    "output_parameters": [
      {
        "name": "snapshot_id",
        "type": "string",
        "description": "Created snapshot identifier"
      }
    ]
  }
}
```

### vra_run_workflow

Execute a workflow with specified input parameters.

**Parameters:**
- `workflow_id` (required): Workflow to execute
- `inputs` (optional): Input parameter values

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
```json
{
  "success": true,
  "message": "Workflow execution started",
  "execution_id": "exec-789-def456",
  "workflow_id": "workflow-backup-vm",
  "workflow_name": "Backup Virtual Machine",
  "state": "running",
  "started_at": "2024-01-15T11:00:00Z",
  "estimated_duration": "5-10 minutes"
}
```

### vra_get_workflow_run

Get workflow execution details and current status.

**Parameters:**
- `workflow_id` (required): Workflow identifier
- `execution_id` (required): Execution identifier

**Example:**
```json
{
  "workflow_id": "workflow-backup-vm",
  "execution_id": "exec-789-def456"
}
```

**Response:**
```json
{
  "success": true,
  "execution_details": {
    "execution_id": "exec-789-def456",
    "workflow_id": "workflow-backup-vm",
    "workflow_name": "Backup Virtual Machine",
    "state": "completed",
    "started_at": "2024-01-15T11:00:00Z",
    "completed_at": "2024-01-15T11:07:30Z",
    "duration": "7 minutes 30 seconds",
    "inputs": {
      "vm_name": "web-server-001",
      "snapshot_name": "backup-2024-01-15",
      "include_memory": true
    },
    "outputs": {
      "snapshot_id": "snapshot-456-abc789"
    },
    "status": "success"
  }
}
```

### vra_cancel_workflow_run

Cancel a running workflow execution.

**Parameters:**
- `workflow_id` (required): Workflow identifier
- `execution_id` (required): Execution to cancel

**Example:**
```json
{
  "workflow_id": "workflow-backup-vm", 
  "execution_id": "exec-789-def456"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Workflow execution cancelled",
  "execution_id": "exec-789-def456",
  "workflow_name": "Backup Virtual Machine",
  "previous_state": "running",
  "current_state": "cancelled",
  "cancelled_at": "2024-01-15T11:05:00Z"
}
```

---

## Tag Management Tools

### vra_list_tags

List all available tags in the system.

**Parameters:**
- `project_id` (optional): Filter by project scope
- `page_size` (optional): Items per page (default: 100)

**Example:**
```json
{
  "project_id": "dev-project-123",
  "page_size": 50
}
```

**Response:**
```json
{
  "success": true,
  "tags": [
    {
      "id": "tag-environment-dev",
      "key": "environment",
      "value": "development",
      "description": "Development environment tag",
      "created_by": "admin@corp.local",
      "created_at": "2024-01-10T10:00:00Z"
    }
  ],
  "total_count": 12
}
```

### vra_create_tag

Create a new tag with key-value pair.

**Parameters:**
- `key` (required): Tag key/name
- `value` (required): Tag value
- `description` (optional): Tag description

**Example:**
```json
{
  "key": "cost-center",
  "value": "engineering",
  "description": "Engineering department cost center"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Tag created successfully",
  "tag": {
    "id": "tag-cost-center-eng",
    "key": "cost-center",
    "value": "engineering",
    "description": "Engineering department cost center",
    "created_at": "2024-01-15T11:30:00Z"
  }
}
```

### vra_assign_tag

Assign a tag to a deployment or resource.

**Parameters:**
- `resource_id` (required): Deployment or resource ID
- `tag_id` (required): Tag to assign

**Example:**
```json
{
  "resource_id": "dep-12345-abcdef",
  "tag_id": "tag-environment-dev"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Tag assigned successfully",
  "resource_id": "dep-12345-abcdef",
  "resource_name": "web-server-001",
  "tag": {
    "key": "environment",
    "value": "development"
  }
}
```

### vra_get_tag_assignments

Get all tag assignments for a specific resource.

**Parameters:**
- `resource_id` (required): Resource identifier

**Example:**
```json
{
  "resource_id": "dep-12345-abcdef"
}
```

**Response:**
```json
{
  "success": true,
  "resource_id": "dep-12345-abcdef",
  "resource_name": "web-server-001",
  "tags": [
    {
      "id": "tag-environment-dev",
      "key": "environment",
      "value": "development"
    },
    {
      "id": "tag-owner-team",
      "key": "owner",
      "value": "frontend-team"
    }
  ],
  "tag_count": 2
}
```

---

## Error Responses

All tools return consistent error responses when issues occur:

```json
{
  "success": false,
  "error": "Authentication failed",
  "error_code": "AUTH_FAILED",
  "details": {
    "message": "Token has expired",
    "suggestion": "Please re-authenticate using vra_auth_login"
  }
}
```

## Common Error Codes

- `AUTH_FAILED` - Authentication or authorization error
- `NOT_FOUND` - Resource not found
- `INVALID_PARAMS` - Invalid parameters provided
- `API_ERROR` - vRA API returned an error
- `TIMEOUT` - Request timed out
- `SERVER_ERROR` - Internal server error

## Usage Tips

1. **Always check authentication first** using `vra_auth_status`
2. **Use pagination** for large result sets with `page_size` parameter  
3. **Filter results** when possible to improve performance
4. **Handle errors gracefully** and provide meaningful feedback
5. **Use verbose logging** during development for troubleshooting