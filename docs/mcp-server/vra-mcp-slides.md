---
marp: true
theme: default
class: invert
paginate: true
style: |
  section {
    font-size: 20px;
  }
  h1 {
    font-size: 36px;
  }
  h2 {
    font-size: 28px;
  }
  h3 {
    font-size: 24px;
  }
  code {
    font-size: 16px;
  }
  pre {
    font-size: 14px;
  }
  ul, ol {
    font-size: 18px;
  }
  table {
    font-size: 16px;
  }
---

# VMware vRA MCP Tools
## Complete Reference Guide

---

## Overview

**26 Total Tools** organized into 6 categories:
- Authentication (1 tool)
- Catalog Management (4 tools)
- Schema Catalog (8 tools)
- Deployment Management (4 tools)
- Advanced Reporting (4 tools)
- Workflow Management (5 tools)

---

## Golden Rules

1. **Always authenticate first** using `vraauthenticate`
2. **Load schemas** with `vraschemaloadschemas` for enhanced functionality
3. **Use schema tools** for guided deployments (better validation)
4. **Leverage reporting tools** for environment insights
5. **Use dryrun mode** in `vraschemaexecuteschema` before deployment

---

## Authentication

### `vraauthenticate`
Authenticate to vRA server and store credentials securely.

**Required Parameters:**
- `username` – vRA username
- `password` – User password
- `url` – vRA server URL (e.g., https://vra.company.com)

**Optional Parameters:**
- `tenant` – Tenant domain
- `domain` – Authentication domain

---

## Catalog Management (1/2)

### `vralistcatalogitems`
List VMware vRA catalog items with optional filtering.

**Optional Parameters:**
- `projectid` – Filter by project ID
- `pagesize` – Number of items per page (default: 100)
- `firstpageonly` – Fetch only first page (default: false)

---

## Catalog Management (2/2)

### `vragetcatalogitem`
Get details of a specific catalog item.
- **Required:** `itemid`

### `vragetcatalogitemschema`
Get request schema for a catalog item.
- **Required:** `itemid`

### `vrarequestcatalogitem`
Request a catalog item deployment.
- **Required:** `itemid`, `projectid`
- **Optional:** `inputs`, `reason`, `name`

---

## Schema Catalog (1/3)

### `vraschemaloadschemas`
Load catalog schemas from JSON files into persistent cache.
- **Optional:** `pattern` (default: schema.json), `forcereload` (default: false)

### `vraschemalistschemas`
List available catalog schemas from cache.
- **Optional:** `itemtype`, `namefilter`

### `vraschemasearchschemas`
Search catalog schemas by name or description.
- **Required:** `query`

### `vraschemashowschema`
Show detailed schema information for a catalog item.
- **Required:** `catalogitemid`

---

## Schema Catalog (2/3)

### `vraschemaexecuteschema`
Execute a catalog item using its schema with AI-guided input collection.
- **Required:** `catalogitemid`, `projectid`
- **Optional:** `deploymentname`, `inputs`, `dryrun` (default: false)

### `vraschemageneratetemplate`
Generate input template for a catalog item.
- **Required:** `catalogitemid`, `projectid`

---
## Schema Catalog (3/3)

### `vraschemaclearcache`
Clear the persistent schema registry cache.
- **Parameters:** None

### `vraschemaregistrystatus`
Show schema registry status and statistics.
- **Parameters:** None

---

## Deployment Management (1/2)

### `vralistdeployments`
List VMware vRA deployments with filtering.
- **Optional:** `projectid`, `status`, `pagesize` (default: 100), `firstpageonly` (default: false)

### `vragetdeployment`
Get details of a specific deployment.
- **Required:** `deploymentid`

---

## Deployment Management (2/2)

### `vragetdeploymentresources`
Get resources of a specific deployment.
- **Required:** `deploymentid`

### `vradeletedeployment`
Delete a deployment.
- **Required:** `deploymentid`
- **Optional:** `confirm` (default: true)

---

## Advanced Reporting (1/2)

### `vrareportactivitytimeline`
Generate deployment activity timeline report.
- **Optional:** `projectid`, `daysback` (1-365, default: 30), `groupby` (day/week/month/year), `statuses`

### `vrareportcatalogusage`
Generate catalog usage report with deployment statistics.
- **Optional:** `projectid`, `includezero` (default: false), `sortby` (deployments/resources/name), `detailedresources` (default: false)

---

## Advanced Reporting (2/2)

### `vrareportresourcesusage`
Generate comprehensive resources usage report.
- **Optional:** `projectid`, `detailedresources` (default: true), `sortby`, `groupby`

### `vrareportunsync`
Generate report of deployments not linked to catalog items.
- **Optional:** `projectid`, `detailedresources` (default: false), `reasonfilter`

---

## Workflow Management (1/3)

### `vralistworkflows`
List available vRealize Orchestrator workflows.
- **Optional:** `pagesize` (1-2000, default: 100), `firstpageonly` (default: false)

### `vragetworkflowschema`
Get workflow input/output schema.
- **Required:** `workflowid`

---

## Workflow Management (2/3)

### `vrarunworkflow`
Execute a workflow with given inputs.
- **Required:** `workflowid`
- **Optional:** `inputs`

### `vragetworkflowrun`
Get workflow execution details.
- **Required:** `workflowid`, `executionid`

---

## Workflow Management (3/3)


### `vracancelworkflowrun`
Cancel a running workflow execution.
- **Required:** `workflowid`, `executionid`

---


## Typical Flow: New Deployment

```
1. vraauthenticate
   ↓
2. vralistcatalogitems (find blueprint)
   ↓
3. vraschemashowschema (view requirements)
   ↓
4. vraschemaexecuteschema (dryrun=true, validate)
   ↓
5. vraschemaexecuteschema (dryrun=false, execute)
```

---

## Typical Flow: Troubleshooting

```
1. vralistdeployments (list all deployments)
   ↓
2. vrareportactivitytimeline (check activity)
   ↓
3. vrareportunsync (find unlinked deployments)
   ↓
4. vragetdeploymentresources (inspect resources)
```

---

## Error Handling

All tools return consistent error response format:

```json
{
  "type": "text",
  "text": "Error message here",
  "isError": true
}
```

**Common Scenarios:**
- `Not authenticated` – Run `vraauthenticate` first
- `Invalid Parameters` – Check parameter names and types
- `API Errors` – Check vRA server connectivity

---

## VS Code MCP Configuration

### Prerequisites
1. VS Code with Continue extension installed
2. VMware vRA CLI installed: `pipx install vmware-vra-cli`
3. MCP server binary in PATH

---

## VS Code Setup (1/3)

### Configuration File Location
- **macOS/Linux**: `~/.continue/config.json`
- **Windows**: `%USERPROFILE%\.continue\config.json`

### Basic Configuration
```json
{
  "models": [...],
  "mcpServers": {
    "vmware-vra": {
      "command": "vra-mcp-server",
      "args": ["--transport", "stdio"]
    }
  }
}
```

---

## VS Code Setup (2/3)

### Advanced Configuration with Environment
```json
{
  "mcpServers": {
    "vmware-vra": {
      "command": "vra-mcp-server",
      "args": ["--transport", "stdio"],
      "env": {
        "VRA_URL": "https://vra.company.com",
        "VRA_TENANT": "vsphere.local",
        "VRA_VERIFY_SSL": "true",
        "VRA_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

---

## VS Code Setup (3/3)

### Verification Steps
1. Restart VS Code after configuration
2. Open Continue sidebar (Cmd/Ctrl+L)
3. Check for "vmware-vra" in available tools
4. Test with: "@vmware-vra authenticate to vRA"

### Troubleshooting
- Check Continue extension logs: View → Output → Continue
- Verify MCP server: Run `vra-mcp-server` in terminal
- Check PATH: Run `which vra-mcp-server` (Unix) or `where vra-mcp-server` (Windows)

---

## Quick Reference Summary

| Category | Tool Count | Primary Use |
|----------|-----------|-------------|
| Authentication | 1 | Login & credential caching |
| Catalog | 4 | Browse & request deployments |
| Schema | 8 | Guided deployment execution |
| Deployments | 4 | Manage existing deployments |
| Reporting | 4 | Environment insights & analytics |
| Workflows | 5 | vRO automation execution |

