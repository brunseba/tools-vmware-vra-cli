# Deployment Export Guide

The VMware vRA CLI provides powerful deployment export capabilities through the `deployment export-all` command. This comprehensive guide covers all aspects of exporting, organizing, and analyzing your vRA deployments.

## Overview

The `deployment export-all` command fetches all deployments from your vRA environment and groups them by their associated catalog items, exporting each group to separate JSON files. This is invaluable for:

- **Backup and Recovery**: Create comprehensive backups of your deployment configurations
- **Migration Planning**: Analyze deployment patterns before environment migrations  
- **Audit and Compliance**: Generate detailed reports of all deployments and their relationships
- **Analytics**: Understand usage patterns and catalog item adoption
- **Troubleshooting**: Investigate unsynced deployments and catalog item relationships

## Command Syntax

```bash
vmware-vra deployment export-all [OPTIONS]
```

### Available Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--project` | TEXT | None | Filter deployments by specific project ID |
| `--output-dir` | TEXT | `./exports` | Directory to save export files |
| `--include-resources` | FLAG | False | Include detailed resource information (slower) |
| `--no-unsynced` | FLAG | False | Exclude deployments not linked to catalog items |
| `--help` | FLAG | - | Show command help and exit |

## Basic Usage Examples

### 1. Simple Export (Default Settings)

Export all deployments with default settings:

```bash
vmware-vra deployment export-all
```

**Sample Output:**
```
✅ Export completed successfully!
Output directory: ./exports
Files created: 12

Export Statistics:
  Total deployments: 156
  Synced deployments: 142
  Unsynced deployments: 14
  Catalog items with deployments: 8
  Total catalog items: 23

Exported Files:
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Filename                               ┃ Catalog Item             ┃ Deployments ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ Ubuntu_Server_Template_abc123.json    │ Ubuntu Server Template  │          45 │
│ Windows_Server_2019_def456.json       │ Windows Server 2019     │          32 │
│ Docker_Container_ghi789.json          │ Docker Container        │          28 │
│ MySQL_Database_jkl012.json            │ MySQL Database          │          19 │
│ Load_Balancer_mno345.json             │ Load Balancer           │          12 │
│ Storage_Volume_pqr678.json            │ Storage Volume          │           4 │
│ Network_Segment_stu901.json           │ Network Segment         │           2 │
│ unsynced_deployments.json             │ Unsynced Deployments    │          14 │
│ export_summary.json                   │ Export Summary          │           - │
└────────────────────────────────────────┴──────────────────────────┴─────────────┘

ℹ️  14 unsynced deployments were included in unsynced_deployments.json

💡 View export_summary.json for detailed export information
```

### 2. Project-Specific Export

Export deployments for a specific project:

```bash
vmware-vra deployment export-all --project "development-env-123"
```

**Sample Output:**
```
✅ Export completed successfully!
Output directory: ./exports
Files created: 6

Export Statistics:
  Total deployments: 43
  Synced deployments: 41
  Unsynced deployments: 2
  Catalog items with deployments: 4
  Total catalog items: 23
```

### 3. Export with Resource Details

Include detailed resource information for each deployment:

```bash
vmware-vra deployment export-all --include-resources
```

**Sample Output:**
```
Exporting deployments grouped by catalog item (including resources)...

✅ Export completed successfully!
Output directory: ./exports
Files created: 12

ℹ️  Resource details included - this may have taken longer to complete
```

### 4. Custom Output Directory

Export to a specific directory:

```bash
vmware-vra deployment export-all --output-dir "/backup/vra-exports/$(date +%Y-%m-%d)"
```

### 5. Exclude Unsynced Deployments

Export only deployments that are properly linked to catalog items:

```bash
vmware-vra deployment export-all --no-unsynced
```

**Sample Output:**
```
✅ Export completed successfully!
Output directory: ./exports
Files created: 9

ℹ️  14 unsynced deployments were excluded (use without --no-unsynced to include them)
```

## Advanced Usage Examples

### 6. Comprehensive Backup Script

Create a complete backup with timestamps:

```bash
#!/bin/bash
BACKUP_DIR="/backup/vra/$(date +%Y-%m-%d_%H-%M-%S)"
mkdir -p "$BACKUP_DIR"

echo "Starting vRA deployment export to $BACKUP_DIR..."
vmware-vra deployment export-all \
    --output-dir "$BACKUP_DIR" \
    --include-resources

echo "Export completed. Backup stored in: $BACKUP_DIR"
ls -la "$BACKUP_DIR"
```

### 7. Multi-Project Export

Export each project separately:

```bash
#!/bin/bash
PROJECTS=("dev-project-123" "staging-project-456" "prod-project-789")

for project in "${PROJECTS[@]}"; do
    echo "Exporting project: $project"
    vmware-vra deployment export-all \
        --project "$project" \
        --output-dir "./exports/${project}" \
        --include-resources
done
```

## Output File Structure

The export command creates several types of files in the output directory:

### 1. Catalog Item Files

**Naming Pattern:** `{catalog_item_name}_{catalog_item_id}.json`

**Example:** `Ubuntu_Server_Template_abc123.json`

**Sample Content:**
```json
{
  "catalog_item_id": "abc123",
  "catalog_item_info": {
    "id": "abc123",
    "name": "Ubuntu Server Template",
    "type": {
      "id": "com.vmw.blueprint",
      "name": "com.vmw.blueprint"
    },
    "status": "PUBLISHED",
    "version": "1.2",
    "description": "Standard Ubuntu 20.04 server template"
  },
  "export_timestamp": "2024-01-15T14:30:00.123456",
  "deployment_count": 45,
  "deployments": [
    {
      "id": "deployment-001",
      "name": "ubuntu-web-01",
      "status": "CREATE_SUCCESSFUL",
      "projectId": "dev-project-123", 
      "createdAt": "2024-01-10T09:15:30.000Z",
      "catalogItemId": "abc123",
      "catalogItemName": "Ubuntu Server Template",
      "_catalog_item_info": {
        "id": "abc123",
        "name": "Ubuntu Server Template",
        "type": "com.vmw.blueprint",
        "status": "PUBLISHED",
        "version": "1.2",
        "description": "Standard Ubuntu 20.04 server template"
      }
    }
  ]
}
```

### 2. Unsynced Deployments File

**Filename:** `unsynced_deployments.json`

**Sample Content:**
```json
{
  "export_timestamp": "2024-01-15T14:30:00.123456",
  "description": "Deployments that could not be linked to any catalog item",
  "deployment_count": 14,
  "deployments": [
    {
      "id": "deployment-orphan-001",
      "name": "legacy-vm-01",
      "status": "CREATE_SUCCESSFUL",
      "projectId": "legacy-project-456",
      "createdAt": "2023-12-01T10:20:30.000Z",
      "_unsynced_reason": "missing_catalog_references"
    },
    {
      "id": "deployment-orphan-002", 
      "name": "manual-deployment-02",
      "status": "CREATE_SUCCESSFUL",
      "projectId": "dev-project-123",
      "createdAt": "2024-01-05T15:45:20.000Z",
      "catalogItemId": "deleted-item-999",
      "_unsynced_reason": "catalog_item_deleted"
    }
  ]
}
```

### 3. Export Summary File

**Filename:** `export_summary.json`

**Sample Content:**
```json
{
  "export_timestamp": "2024-01-15T14:30:00.123456",
  "export_parameters": {
    "project_id": null,
    "include_resources": false,
    "include_unsynced": true
  },
  "statistics": {
    "total_deployments": 156,
    "synced_deployments": 142,
    "unsynced_deployments": 14,
    "catalog_items_with_deployments": 8,
    "total_catalog_items": 23
  },
  "exported_files": [
    {
      "filename": "Ubuntu_Server_Template_abc123.json",
      "filepath": "./exports/Ubuntu_Server_Template_abc123.json", 
      "catalog_item_id": "abc123",
      "catalog_item_name": "Ubuntu Server Template",
      "deployment_count": 45
    },
    {
      "filename": "Windows_Server_2019_def456.json",
      "filepath": "./exports/Windows_Server_2019_def456.json",
      "catalog_item_id": "def456", 
      "catalog_item_name": "Windows Server 2019",
      "deployment_count": 32
    }
  ],
  "files_created": 12
}
```

## Understanding Export Results

### Deployment Matching Logic

The export command uses intelligent matching to link deployments to catalog items:

1. **Direct Catalog Item ID Match**: Exact match on `catalogItemId` field
2. **Blueprint ID Match**: Match on `blueprintId` for blueprint-based deployments  
3. **Catalog Item Name Match**: Exact match on `catalogItemName` field
4. **Fuzzy Name Matching**: Similarity matching between deployment and catalog item names

### Unsynced Deployment Reasons

Deployments may be unsynced for several reasons:

- `missing_catalog_references`: No catalog item references in deployment metadata
- `catalog_item_deleted`: Referenced catalog item no longer exists
- `catalog_name_mismatch`: Catalog item name not found in current catalog
- `blueprint_deleted`: Referenced blueprint no longer exists  
- `external_creation`: Deployment created outside service catalog workflow

## Data Analysis Examples

### 1. Find Most Used Catalog Items

```bash
# Export deployments
vmware-vra deployment export-all --output-dir ./analysis

# Use jq to analyze export summary
cat ./analysis/export_summary.json | jq -r '
  .exported_files[] | 
  select(.catalog_item_name != "Unsynced Deployments") |
  "\(.deployment_count)\t\(.catalog_item_name)"
' | sort -rn | head -10
```

**Sample Output:**
```
45    Ubuntu Server Template
32    Windows Server 2019  
28    Docker Container
19    MySQL Database
12    Load Balancer
4     Storage Volume
2     Network Segment
```

### 2. Analyze Deployment Status Distribution

```bash
# Extract status information from all catalog item files
for file in ./exports/*.json; do
  if [[ "$file" != *"unsynced_deployments.json"* && "$file" != *"export_summary.json"* ]]; then
    echo "=== $(basename "$file") ==="
    cat "$file" | jq -r '.deployments[].status' | sort | uniq -c
  fi
done
```

### 3. Find Deployments by Date Range

```bash
# Find deployments created in last 30 days
for file in ./exports/*.json; do
  if [[ "$file" != *"unsynced_deployments.json"* && "$file" != *"export_summary.json"* ]]; then
    cat "$file" | jq -r --arg cutoff "$(date -d '30 days ago' -Iseconds)" '
      .deployments[] | 
      select(.createdAt > $cutoff) |
      "\(.createdAt)\t\(.name)\t\(.status)"
    '
  fi
done | sort
```

## Integration with Other Tools

### 1. Import to Database

Convert JSON exports to CSV for database import:

```bash
#!/bin/bash
# Create CSV header
echo "deployment_id,deployment_name,status,project_id,created_at,catalog_item_id,catalog_item_name" > deployments.csv

# Process all catalog item files
for file in ./exports/*.json; do
  if [[ "$file" != *"unsynced_deployments.json"* && "$file" != *"export_summary.json"* ]]; then
    cat "$file" | jq -r '.deployments[] | 
      [.id, .name, .status, .projectId, .createdAt, .catalogItemId // "", ._catalog_item_info.name // ""] | 
      @csv' >> deployments.csv
  fi
done
```

### 2. Generate Excel Report

```bash
# Install required tools
pip install pandas openpyxl

# Python script to create Excel report
cat << 'EOF' > create_excel_report.py
import pandas as pd
import json
import glob
from datetime import datetime

def create_report():
    all_deployments = []
    
    # Process all catalog item files
    for file_path in glob.glob('./exports/*.json'):
        if 'unsynced_deployments.json' in file_path or 'export_summary.json' in file_path:
            continue
            
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        for deployment in data['deployments']:
            all_deployments.append({
                'Deployment ID': deployment['id'],
                'Deployment Name': deployment['name'], 
                'Status': deployment['status'],
                'Project ID': deployment['projectId'],
                'Created At': deployment['createdAt'],
                'Catalog Item': data['catalog_item_info']['name'],
                'Catalog Item Type': data['catalog_item_info']['type']['name']
            })
    
    # Create DataFrame and save to Excel
    df = pd.DataFrame(all_deployments)
    df.to_excel(f'vra_deployments_{datetime.now().strftime("%Y%m%d")}.xlsx', index=False)
    print(f"Excel report created: vra_deployments_{datetime.now().strftime('%Y%m%d')}.xlsx")

if __name__ == "__main__":
    create_report()
EOF

python create_excel_report.py
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Authentication Errors

**Error:** `No valid authentication token found`

**Solution:**
```bash
# Re-authenticate
vmware-vra auth login --username your-username --url https://vra.example.com
```

#### 2. Permission Errors

**Error:** `Failed to list deployments: 403 Forbidden`

**Solution:** Ensure your user account has appropriate permissions:
- `Service Catalog User` role minimum
- `Project Administrator` for project-specific exports
- `Organization Administrator` for system-wide exports

#### 3. Large Export Timeouts

**Error:** Export appears to hang on large environments

**Solution:**
```bash
# Use project filtering to reduce scope
vmware-vra deployment export-all --project specific-project-id

# Or exclude resource details for faster export
vmware-vra deployment export-all --no-unsynced
```

#### 4. Disk Space Issues

**Error:** `No space left on device`

**Solution:**
```bash
# Check available space
df -h

# Use external storage location
vmware-vra deployment export-all --output-dir /mnt/external-storage/vra-exports
```

#### 5. JSON Parsing Errors

**Error:** Issues reading exported files

**Solution:**
```bash
# Validate JSON files
for file in ./exports/*.json; do
  echo "Validating: $file"
  python -m json.tool "$file" > /dev/null && echo "✓ Valid" || echo "✗ Invalid"
done
```

### Debugging Options

Enable verbose output for troubleshooting:

```bash
vmware-vra --verbose deployment export-all --output-dir ./debug-export
```

This will show:
- HTTP request/response details
- Deployment matching logic decisions  
- Resource fetching progress
- File creation details

## Best Practices

### 1. Regular Backups

Set up automated exports:

```bash
#!/bin/bash
# /etc/cron.daily/vra-export

BACKUP_ROOT="/backup/vra"
DATE=$(date +%Y-%m-%d)
BACKUP_DIR="$BACKUP_ROOT/$DATE"

mkdir -p "$BACKUP_DIR"

vmware-vra deployment export-all \
    --output-dir "$BACKUP_DIR" \
    --include-resources

# Keep only last 30 days of backups
find "$BACKUP_ROOT" -type d -name "20*" -mtime +30 -exec rm -rf {} \;
```

### 2. Storage Management

Monitor export sizes and implement rotation:

```bash
# Check export directory size
du -sh ./exports

# Compress older exports
find ./exports -name "*.json" -mtime +7 -exec gzip {} \;
```

### 3. Data Validation

Always validate critical exports:

```bash
# Verify export completeness
EXPECTED_DEPLOYMENTS=$(vmware-vra deployment list --format json | jq length)
EXPORTED_DEPLOYMENTS=$(cat ./exports/export_summary.json | jq '.statistics.total_deployments')

if [ "$EXPECTED_DEPLOYMENTS" -eq "$EXPORTED_DEPLOYMENTS" ]; then
    echo "✓ Export complete: $EXPORTED_DEPLOYMENTS deployments"
else
    echo "⚠ Potential export issue: Expected $EXPECTED_DEPLOYMENTS, got $EXPORTED_DEPLOYMENTS"
fi
```

### 4. Security Considerations

- **Secure Storage**: Store exports in encrypted, access-controlled locations
- **Data Sanitization**: Remove sensitive information before sharing exports
- **Retention Policies**: Implement appropriate data retention policies
- **Access Auditing**: Log and monitor access to export files

```bash
# Example: Remove sensitive fields before sharing
cat export.json | jq 'del(.deployments[].inputs.password, .deployments[].inputs.apiKey)' > sanitized_export.json
```

This comprehensive guide provides everything needed to effectively use the deployment export functionality in the VMware vRA CLI.
