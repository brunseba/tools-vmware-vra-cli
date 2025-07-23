# Resources Usage Reporting Guide

The `vra report resources-usage` command provides a comprehensive view of all resources across your vRA deployments, offering detailed insights into resource utilization, types, and distribution patterns.

## Overview

This reporting feature helps you:

- **Monitor Resource Utilization**: Get a consolidated view of all resources across deployments
- **Analyze Resource Distribution**: Understand which resource types are most commonly used
- **Track Resource States**: Monitor the health and status of your infrastructure
- **Identify Resource Patterns**: Discover usage patterns by catalog item, project, or deployment status
- **Optimize Resource Allocation**: Make informed decisions about resource management

## Command Syntax

```bash
vra report resources-usage [OPTIONS]
```

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--project` | TEXT | None | Filter by project ID |
| `--detailed-resources` | FLAG | True | Fetch detailed resource information (default enabled) |
| `--no-detailed-resources` | FLAG | False | Skip detailed resource fetching for faster execution |
| `--sort-by` | CHOICE | `catalog-item` | Sort by: `deployment-name`, `catalog-item`, `resource-count`, `status` |
| `--group-by` | CHOICE | `catalog-item` | Group by: `catalog-item`, `resource-type`, `deployment-status` |

## Performance Modes

### Detailed Mode (Default)
```bash
vra report resources-usage --detailed-resources
```

- Fetches complete resource information for each deployment
- Provides accurate resource counts and types
- Slower execution for environments with many deployments
- Recommended for comprehensive analysis

### Fast Mode
```bash
vra report resources-usage --no-detailed-resources
```

- Uses estimated resource counts based on deployment metadata
- Faster execution for large environments
- Less precise but suitable for quick overviews
- Recommended for initial assessments

## Grouping Options

### By Catalog Item (Default)
Groups deployments by their source catalog item, showing resource utilization per blueprint or workflow.

```bash
vra report resources-usage --group-by catalog-item
```

**Use Cases:**
- Identify which catalog items create the most resources
- Compare resource efficiency between different blueprints
- Plan catalog optimization initiatives

### By Resource Type
Groups deployments by their primary resource types.

```bash
vra report resources-usage --group-by resource-type
```

**Use Cases:**
- Understand your infrastructure composition
- Identify resource type concentrations
- Plan capacity for specific resource types

### By Deployment Status
Groups deployments by their current status (successful, failed, in-progress).

```bash
vra report resources-usage --group-by deployment-status
```

**Use Cases:**
- Monitor deployment health across your environment
- Identify failed deployments consuming resources
- Track deployment completion rates

## Sorting Options

### By Catalog Item (Default)
```bash
vra report resources-usage --sort-by catalog-item
```
Sorts alphabetically by catalog item name.

### By Resource Count
```bash
vra report resources-usage --sort-by resource-count
```
Sorts by total resource count (highest first).

### By Deployment Name
```bash
vra report resources-usage --sort-by deployment-name
```
Sorts alphabetically by deployment name.

### By Status
```bash
vra report resources-usage --sort-by status
```
Sorts by deployment status.

## Example Output

### Summary Section
```
📈 Resource Usage Summary
Total Deployments             156    All deployments in scope
Linked Deployments             134    Linked to catalog items
Unlinked Deployments            22    Cannot link to catalog items

Total Resources               1,234   Across all deployments
Unique Resource Types            8    Different resource types found
Unique Catalog Items            12    Catalog items with deployments
Avg Resources per Deployment   7.9   Average resource density
```

### Resource Type Breakdown
```
🔧 Resource Type Breakdown
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┓
┃ Resource Type                    ┃ Count ┃ Percentage ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━┩
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

### Detailed Deployment Information
The report shows detailed deployment information grouped according to your selected grouping option, including:

- Deployment names and IDs
- Resource counts per deployment
- Associated catalog items
- Deployment status and creation dates
- Resource type distributions

## Common Use Cases

### 1. Infrastructure Audit
Generate a comprehensive view of your entire vRA environment:

```bash
# Complete infrastructure overview
vra report resources-usage --detailed-resources --format json > infrastructure-audit.json

# Quick overview for large environments
vra report resources-usage --no-detailed-resources --group-by resource-type
```

### 2. Catalog Item Analysis
Analyze which catalog items are creating the most resources:

```bash
# Sort by resource consumption
vra report resources-usage --sort-by resource-count --group-by catalog-item

# Focus on specific project
vra report resources-usage --project prod-env --group-by catalog-item
```

### 3. Resource Type Planning
Understand your resource type distribution:

```bash
# Group by resource type to see infrastructure composition
vra report resources-usage --group-by resource-type --detailed-resources

# Export for capacity planning
vra report resources-usage --group-by resource-type --format yaml > resource-planning.yaml
```

### 4. Deployment Health Monitoring
Monitor deployment status and associated resources:

```bash
# View deployments by status
vra report resources-usage --group-by deployment-status

# Focus on failed deployments
vra report resources-usage --group-by deployment-status --sort-by status
```

### 5. Project-Specific Analysis
Analyze resources within specific projects:

```bash
# Development project analysis
vra report resources-usage --project dev-project-123 --detailed-resources

# Compare projects by exporting multiple reports
vra report resources-usage --project dev-env --format json > dev-resources.json
vra report resources-usage --project prod-env --format json > prod-resources.json
```

## Integration with Other Commands

### Combined with Export
```bash
# Generate comprehensive reports
vra deployment export-all --include-resources --output-dir ./backup
vra report resources-usage --detailed-resources --format json > ./backup/resource-usage.json
vra report catalog-usage --detailed-resources --format json > ./backup/catalog-usage.json
```

### Automation Scripts
```bash
#!/bin/bash
# Daily resource monitoring script

DATE=$(date +%Y-%m-%d)
REPORT_DIR="./reports/$DATE"
mkdir -p "$REPORT_DIR"

# Generate multiple resource reports
vra report resources-usage --detailed-resources --format json > "$REPORT_DIR/resources-detailed.json"
vra report resources-usage --group-by resource-type --format json > "$REPORT_DIR/resources-by-type.json"
vra report resources-usage --group-by deployment-status --format json > "$REPORT_DIR/resources-by-status.json"

# Generate summary
vra report resources-usage --no-detailed-resources > "$REPORT_DIR/resources-summary.txt"

echo "Resource reports generated in $REPORT_DIR"
```

## Output Formats

### Table Format (Default)
Human-readable tables with comprehensive breakdowns and visual formatting.

### JSON Format
```bash
vra report resources-usage --format json
```
Machine-readable format for automation, scripting, and integration with other tools.

### YAML Format
```bash
vra report resources-usage --format yaml
```
Human-readable structured format, ideal for configuration management and documentation.

## Performance Considerations

### Large Environments
For environments with 500+ deployments:

1. **Use Fast Mode Initially**: `--no-detailed-resources` for quick overviews
2. **Filter by Project**: Use `--project` to limit scope
3. **Export to Files**: Use `--format json` and save to files for analysis
4. **Run During Off-Hours**: Detailed mode can be resource-intensive

### Optimization Tips

1. **Project-Based Analysis**: Analyze projects separately rather than all at once
2. **Staged Reporting**: Use fast mode first, then detailed mode for specific areas of interest
3. **Automation**: Schedule regular reports during low-usage periods
4. **Data Export**: Export to JSON/YAML for analysis in external tools

## Troubleshooting

### Common Issues

#### Authentication Errors
```bash
# Ensure you're authenticated
vra auth status
vra auth login  # if needed
```

#### Performance Issues
```bash
# Use fast mode for large environments
vra report resources-usage --no-detailed-resources

# Filter to specific project
vra report resources-usage --project specific-project-id
```

#### Empty Results
```bash
# Check if deployments exist
vra deployment list --first-page-only

# Verify project ID
vra deployment list --project your-project-id
```

### Debugging

Enable verbose output for troubleshooting:
```bash
vra --verbose report resources-usage --detailed-resources
```

## Best Practices

1. **Regular Monitoring**: Schedule weekly resource usage reports
2. **Project Segmentation**: Analyze projects separately for focused insights
3. **Historical Tracking**: Export reports to files for trend analysis
4. **Performance Awareness**: Use appropriate mode (fast/detailed) based on environment size
5. **Integration**: Combine with other reporting commands for comprehensive analysis
6. **Documentation**: Include resource usage reports in operational documentation

## Related Commands

- `vra report catalog-usage`: Analyze catalog item usage patterns
- `vra report unsync`: Identify deployments not linked to catalog items
- `vra deployment export-all`: Export complete deployment data
- `vra deployment list`: List deployments with basic information
- `vra deployment resources`: Show resources for a specific deployment

The resources usage report is a powerful tool for understanding your vRA infrastructure. Use it regularly to maintain visibility into your resource utilization and make informed decisions about capacity planning and optimization.
