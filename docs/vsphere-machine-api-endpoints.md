# VMware vRA API Endpoints for Cloud.vSphere.Machine Resources

## Overview
This document identifies the key API endpoints for retrieving vSphere virtual machine resources from VMware vRA (Aria Automation).

---

## 1. List All Resources (Filtered)

### Endpoint
```
GET /deployment/api/resources
```

### Description
Returns a paginated list of resources across all deployments. Best for filtering by resource type.

### Key Parameters
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `resourceTypes` | array[string] | Filter by resource type names | `Cloud.vSphere.Machine` |
| `projects` | array[string] | Filter by project IDs | `5dbd84b1-d715-4c6d-b530-4db83f68708b` |
| `page` | integer | Zero-based page index (default: 0) | `0` |
| `size` | integer | Page size (default: 20, max: 2000) | `100` |
| `expand` | array[string] | Expand related objects | `project`, `deployment`, `currentRequest` |
| `search` | string | Search in resource fields | `myvm` |
| `tags` | array[string] | Filter by tags | `env:prod` |
| `cloudAccounts` | array[string] | Filter by cloud account | |
| `origin` | array[string] | Resource origin filter | `DEPLOYED`, `DISCOVERED` |
| `$top` | integer | OData: Number of records | `100` |
| `$skip` | integer | OData: Skip records | `0` |
| `$filter` | string | OData: Filter expression | `name eq 'myvm'` |

### Example Request
```bash
curl -X GET "https://vra.example.com/deployment/api/resources?resourceTypes=Cloud.vSphere.Machine&projects=PROJECT_ID&size=100" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### Response Schema
Returns `PageResource` containing:
- `content[]`: Array of Resource objects
- `totalElements`: Total count
- `totalPages`: Number of pages
- `size`: Page size
- `number`: Current page
- `last`: Boolean indicating last page

---

## 2. Get Specific Resource Details

### Endpoint
```
GET /deployment/api/resources/{resourceId}
```

### Description
Returns detailed information about a specific resource by its ID.

### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `resourceId` | string (uuid) | Yes | Unique resource identifier |
| `expand` | array[string] | No | Expand: `project`, `deployment`, `currentRequest`, `inprogressRequests`, `user` |

### Example Request
```bash
curl -X GET "https://vra.example.com/deployment/api/resources/RESOURCE_ID?expand=deployment,currentRequest" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

### Response Schema
Returns a `Resource` object

---

## 3. List Resources for a Deployment

### Endpoint
```
GET /deployment/api/deployments/{deploymentId}/resources
```

### Description
Returns resources associated with a specific deployment. Use when you have a deployment ID.

### Key Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `deploymentId` | string (uuid) | Deployment ID (path parameter) |
| `resourceTypes` | array[string] | Filter by resource types |
| `names` | array[string] | Filter by exact resource names |
| `tags` | array[string] | Filter by tags |
| `expand` | array[string] | Expand: `currentRequest`, `inprogressRequests` |
| `page`, `size` | integers | Pagination |

### Example Request
```bash
curl -X GET "https://vra.example.com/deployment/api/deployments/DEPLOYMENT_ID/resources?resourceTypes=Cloud.vSphere.Machine" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

---

## Resource Object Properties

When you retrieve a Cloud.vSphere.Machine resource, the response includes:

### Standard Fields
```json
{
  "id": "uuid",
  "name": "VM name",
  "type": "Cloud.vSphere.Machine",
  "deploymentId": "uuid",
  "projectId": "uuid",
  "orgId": "uuid",
  "createdAt": "ISO 8601 timestamp",
  "description": "string",
  "origin": "DEPLOYED | DISCOVERED | ONBOARDED | MIGRATED",
  "syncStatus": "MISSING | STALE",
  "billable": "boolean",
  "expense": {
    "total": "number",
    "currency": "string"
  },
  "properties": {
    // VM-specific properties (see below)
  }
}
```

### Cloud.vSphere.Machine Properties
The `properties` field contains vSphere-specific details:
```json
{
  "properties": {
    "cpuCount": "integer",
    "totalMemoryMB": "integer",
    "powerState": "ON | OFF",
    "address": "IP address",
    "ipAddress": "IP address",
    "osType": "OS name",
    "guestOS": "Guest OS details",
    "datacenter": "Datacenter name",
    "cluster": "Cluster name",
    "resourcePool": "Resource pool name",
    "networks": ["array of network names"],
    "storageProfile": "Storage profile",
    "customProperties": {}
  }
}
```

---

## Recommended Approach for VM Inventory

### Option A: Fetch All VMs Directly (Most Efficient)
```bash
GET /deployment/api/resources?resourceTypes=Cloud.vSphere.Machine&size=2000
```
**Pros:**
- Single API call
- Direct filtering by resource type
- Can filter by project, tags, etc.

**Cons:**
- May require pagination for large inventories

### Option B: Per-Deployment Fetching
```bash
# 1. Get all deployments
GET /deployment/api/deployments?size=100

# 2. For each deployment, get resources
GET /deployment/api/deployments/{id}/resources?resourceTypes=Cloud.vSphere.Machine
```
**Pros:**
- Organized by deployment
- Can add deployment context to each VM

**Cons:**
- Multiple API calls (N+1 problem)
- Slower for large inventories

### Option C: Combined Approach (Current Implementation)
```python
# Backend bulk endpoint that:
# 1. Fetches all deployments
# 2. Fetches resources for each deployment in parallel
# 3. Filters by resource type
# 4. Adds deployment context to each resource
```

---

## Additional Resource Endpoints

### Get Resource Actions
```
GET /deployment/api/resources/{resourceId}/actions
```
Returns available actions (Power On, Power Off, Resize, etc.) for the resource.

### Get Resource Type Information
```
GET /deployment/api/resource-types?ids=Cloud.vSphere.Machine
```
Returns schema and metadata about the Cloud.vSphere.Machine resource type.

### Resource Filters
```
GET /deployment/api/resources/filters
GET /deployment/api/resources/filters/{filterId}
```
Returns available filter options for resources (projects, tags, cloud accounts, etc.).

---

## Authentication

All endpoints require Bearer token authentication:
```bash
Authorization: Bearer <access_token>
```

Tokens can be obtained via:
```bash
POST /iaas/api/login
POST /csp/gateway/am/api/login
```

---

## Pagination Best Practices

1. **Use appropriate page size**: Default is 20, max is typically 2000
2. **Check `last` field**: Indicates if more pages exist
3. **Use `$top` and `$skip`**: For OData-style pagination
4. **Monitor `totalElements`**: Know total count upfront

---

## Error Responses

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 401 | Unauthorized - Invalid or expired token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource/Deployment doesn't exist |
| 422 | Validation Error - Invalid parameters |
| 500 | Internal Server Error |

---

## Example: Complete VM Inventory Workflow

```bash
#!/bin/bash
VRA_URL="https://vra.example.com"
TOKEN="your_access_token"
PROJECT_ID="your_project_id"

# Fetch all vSphere VMs in a project
curl -X GET "${VRA_URL}/deployment/api/resources" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -G \
  --data-urlencode "resourceTypes=Cloud.vSphere.Machine" \
  --data-urlencode "projects=${PROJECT_ID}" \
  --data-urlencode "size=100" \
  --data-urlencode "expand=deployment" \
  | jq '.content[] | {
      name: .name,
      id: .id,
      deployment: .deployment.name,
      cpu: .properties.cpuCount,
      memory: .properties.totalMemoryMB,
      powerState: .properties.powerState,
      ip: .properties.address
    }'
```

---

## Notes

1. **Resource Type Name**: Use exact string `Cloud.vSphere.Machine` (case-sensitive)
2. **Pagination**: Always implement for production (don't assume all data fits in one page)
3. **Caching**: Consider caching responses for 2-5 minutes to reduce API load
4. **Parallel Fetching**: Use concurrent requests for per-deployment fetching
5. **Property Variations**: Not all VMs have all properties (handle null/undefined gracefully)

---

## References

- OpenAPI Schema: `inputs/2020-08-25.json`
- VMware vRA Documentation: https://docs.vmware.com/en/vRealize-Automation/
- API Version: 2020-08-25
