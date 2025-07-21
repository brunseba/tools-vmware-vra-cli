# Tag Management

The VMware vRA CLI provides comprehensive tag management functionality, enabling you to organize, categorize, and track resources in your vRA environment. Tags are key-value pairs that can be assigned to various resources such as deployments and catalog items.

## Overview

Tags in vRA serve multiple purposes:

- **Resource Organization**: Group related resources together
- **Cost Tracking**: Track resource usage by department, project, or owner
- **Automation**: Enable automated policies and workflows based on tags
- **Compliance**: Ensure resources meet organizational standards
- **Lifecycle Management**: Track resource lifecycle stages

## Tag Commands

### List Tags

List all available tags in your vRA environment:

```bash
vra tag list
```

Search for specific tags:

```bash
vra tag list --search "environment"
```

### Show Tag Details

Show detailed information about a specific tag:

```bash
vra tag show <tag-id>
```

### Create Tags

Create a simple tag with just a key:

```bash
vra tag create "environment"
```

Create a tag with key and value:

```bash
vra tag create "environment" --value "production"
```

Create a tag with description:

```bash
vra tag create "environment" --value "production" --description "Production environment tag"
```

### Update Tags

Update an existing tag:

```bash
vra tag update <tag-id> --key "env" --value "prod" --description "Updated production tag"
```

### Delete Tags

Delete a tag (with confirmation):

```bash
vra tag delete <tag-id>
```

Skip confirmation prompt:

```bash
vra tag delete <tag-id> --confirm
```

## Resource Tagging

### Assign Tags to Resources

Assign a tag to a deployment:

```bash
vra tag assign <deployment-id> <tag-id>
```

Assign a tag to a catalog item:

```bash
vra tag assign <catalog-item-id> <tag-id> --resource-type catalog-item
```

### Remove Tags from Resources

Remove a tag from a deployment:

```bash
vra tag remove <deployment-id> <tag-id>
```

Remove a tag from a catalog item:

```bash
vra tag remove <catalog-item-id> <tag-id> --resource-type catalog-item
```

### View Resource Tags

Show all tags assigned to a deployment:

```bash
vra tag resource-tags <deployment-id>
```

Show tags for a catalog item:

```bash
vra tag resource-tags <catalog-item-id> --resource-type catalog-item
```

## Tag Schema

### Tag Object Structure

```json
{
  "id": "string",
  "key": "string",
  "value": "string|null",
  "description": "string|null",
  "created_at": "string|null",
  "updated_at": "string|null",
  "created_by": "string|null",
  "updated_by": "string|null"
}
```

### Tag Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `id` | string | Yes | Unique identifier for the tag |
| `key` | string | Yes | Tag key/name (e.g., "environment") |
| `value` | string | No | Tag value (e.g., "production") |
| `description` | string | No | Human-readable description |
| `created_at` | string | No | ISO 8601 timestamp of creation |
| `updated_at` | string | No | ISO 8601 timestamp of last update |
| `created_by` | string | No | Username who created the tag |
| `updated_by` | string | No | Username who last updated the tag |

## Use Cases

### 1. Environment Management

Track different environments across your infrastructure:

```bash
# Create environment tags
vra tag create "environment" --value "development" --description "Development environment"
vra tag create "environment" --value "staging" --description "Staging environment"
vra tag create "environment" --value "production" --description "Production environment"

# Assign to deployments
vra tag assign <dev-deployment-id> <dev-tag-id>
vra tag assign <prod-deployment-id> <prod-tag-id>
```

### 2. Cost Center Tracking

Track resource usage by department or cost center:

```bash
# Create cost center tags
vra tag create "cost-center" --value "engineering" --description "Engineering department"
vra tag create "cost-center" --value "marketing" --description "Marketing department"
vra tag create "cost-center" --value "finance" --description "Finance department"

# Assign to resources
vra tag assign <engineering-vm> <engineering-tag-id>
```

### 3. Project Organization

Organize resources by project:

```bash
# Create project tags
vra tag create "project" --value "webapp-v2" --description "Web Application Version 2"
vra tag create "project" --value "mobile-app" --description "Mobile Application Project"

# Assign to catalog items and deployments
vra tag assign <webapp-catalog-item> <webapp-tag-id> --resource-type catalog-item
vra tag assign <webapp-deployment> <webapp-tag-id>
```

### 4. Lifecycle Management

Track resource lifecycle stages:

```bash
# Create lifecycle tags
vra tag create "lifecycle" --value "active" --description "Active resources"
vra tag create "lifecycle" --value "deprecated" --description "Deprecated resources"
vra tag create "lifecycle" --value "decommissioned" --description "Resources to be removed"

# Update resource lifecycle
vra tag assign <old-deployment> <deprecated-tag-id>
```

### 5. Compliance and Governance

Ensure resources meet compliance requirements:

```bash
# Create compliance tags
vra tag create "compliance" --value "gdpr-compliant" --description "GDPR compliant resources"
vra tag create "compliance" --value "hipaa-required" --description "HIPAA compliance required"
vra tag create "backup" --value "daily" --description "Daily backup schedule"

# Assign to sensitive resources
vra tag assign <sensitive-deployment> <gdpr-tag-id>
vra tag assign <medical-app-deployment> <hipaa-tag-id>
```

### 6. Owner and Contact Information

Track resource ownership:

```bash
# Create owner tags
vra tag create "owner" --value "john.doe@company.com" --description "Resource owner"
vra tag create "team" --value "devops" --description "Responsible team"
vra tag create "contact" --value "support@company.com" --description "Support contact"

# Assign ownership
vra tag assign <deployment-id> <owner-tag-id>
vra tag assign <deployment-id> <team-tag-id>
```

## Advanced Tagging Strategies

### Hierarchical Tagging

Use hierarchical tag structures for complex organizations:

```bash
# Create hierarchical tags
vra tag create "app.tier" --value "frontend" --description "Frontend application tier"
vra tag create "app.tier" --value "backend" --description "Backend application tier"
vra tag create "app.tier" --value "database" --description "Database tier"

# Region-specific tags
vra tag create "region.primary" --value "us-east-1" --description "Primary region"
vra tag create "region.backup" --value "us-west-2" --description "Backup region"
```

### Batch Operations

Use shell scripting for batch tag operations:

```bash
#!/bin/bash
# Batch tag creation for multiple environments

environments=("dev" "test" "stage" "prod")
cost_centers=("eng" "ops" "qa" "security")

# Create environment tags
for env in "${environments[@]}"; do
    vra tag create "environment" --value "$env" --description "$env environment"
done

# Create cost center tags
for cc in "${cost_centers[@]}"; do
    vra tag create "cost-center" --value "$cc" --description "$cc department"
done
```

### Tag Validation

Implement tag validation workflows:

```bash
#!/bin/bash
# Validate that critical deployments have required tags

deployment_id="$1"
required_tags=("environment" "owner" "cost-center")

# Get current tags
current_tags=$(vra tag resource-tags "$deployment_id" --format json)

# Check for required tags
for tag in "${required_tags[@]}"; do
    if ! echo "$current_tags" | grep -q "$tag"; then
        echo "Warning: Deployment $deployment_id missing required tag: $tag"
    fi
done
```

## Output Formats

All tag commands support multiple output formats:

### Table Format (Default)

```bash
vra tag list
```

### JSON Format

```bash
vra tag list --format json
```

### YAML Format

```bash
vra tag list --format yaml
```

## Best Practices

### 1. Tag Naming Conventions

- Use consistent naming conventions across your organization
- Use lowercase with hyphens: `cost-center`, `project-name`
- Avoid special characters that might cause issues in automation

### 2. Tag Strategy Planning

- Define your tagging strategy before implementation
- Document tag purposes and allowed values
- Implement governance policies for tag usage

### 3. Regular Maintenance

```bash
# Regular cleanup of unused tags
vra tag list --format json | jq -r '.[] | select(.created_at < "2024-01-01") | .id'

# Audit tag usage
vra deployment list --format json | jq -r '.[].id' | while read deployment; do
    echo "Deployment: $deployment"
    vra tag resource-tags "$deployment" --format json | jq -r '.[].key'
    echo "---"
done
```

### 4. Integration with Automation

Tags can be used in automation workflows and policies:

- **Cost Management**: Filter resources by cost-center tags for billing
- **Backup Policies**: Apply backup schedules based on backup tags  
- **Security Policies**: Apply security controls based on compliance tags
- **Lifecycle Management**: Automate resource cleanup based on lifecycle tags

## Troubleshooting

### Common Issues

1. **Tag Not Found**: Ensure the tag ID exists and you have permissions
2. **Resource Type Not Supported**: Check that the resource type supports tagging
3. **Permission Denied**: Verify you have the necessary permissions to manage tags

### Debug Commands

```bash
# Check tag existence
vra tag show <tag-id> --format json

# Verify resource exists
vra deployment show <deployment-id> --format json

# List all tags to find correct ID
vra tag list --format json | jq -r '.[] | "\(.id): \(.key)=\(.value)"'
```

## API Endpoints

The CLI uses these vRA API endpoints for tag management:

- `GET /vco/api/tags` - List tags
- `POST /vco/api/tags` - Create tag
- `GET /vco/api/tags/{id}` - Get tag details
- `PUT /vco/api/tags/{id}` - Update tag
- `DELETE /vco/api/tags/{id}` - Delete tag
- `POST /deployment/api/deployments/{id}/tags` - Assign tag to deployment
- `DELETE /deployment/api/deployments/{id}/tags/{tagId}` - Remove tag from deployment

---

*Tag management is essential for maintaining organized, compliant, and efficiently managed vRA environments.*
