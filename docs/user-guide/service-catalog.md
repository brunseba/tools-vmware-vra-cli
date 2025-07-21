# Service Catalog

The VMware vRA CLI provides powerful interactions with the Service Catalog, enabling management of catalog items and their deployments. This guide discusses all available operations and configurations.

## Catalog Commands

### List Catalog Items

List all available catalog items:

```bash
vra catalog list
```

You can filter by project:

```bash
vra catalog list --project development
```

### Show Catalog Item Details

Show details of a specific catalog item:

```bash
vra catalog show 5C<catalog-item-id5C>
```

### Request a Catalog Item

Request a new catalog item with inputs:

```bash
vra catalog request  5C<catalog-item-id5C> \
    --inputs '{"cpu": 2, "memory": "4G"}' \
    --project 5C<project-id5C>
```

Use a YAML/JSON file for complex parameters:

```bash
vra catalog request  5C<catalog-item-id5C> \
    --inputs-file inputs.yaml \
    --project 5C<project-id5C>
```

## Advanced Catalog Operations

### Catalog Item Schema

Show the request schema for a catalog item:

```bash
vra catalog schema 5C<catalog-item-id5C>
```

### Deployment Management

List all deployments:

```bash
vra deployment list
```

Show details of a specific deployment:

```bash
vra deployment show 5C<deployment-id5C>
```

Delete a deployment:

```bash
vra deployment delete 5C<deployment-id5C> --confirm
```

View deployment resources:

```bash
vra deployment resources <deployment-id>
```

### Export All Deployments

**NEW in v0.9.0**: Export all deployments grouped by catalog item:

```bash
vra deployment export-all
```

This powerful command exports all your deployments organized by catalog item to separate JSON files, making it perfect for:
- **Backup and recovery** operations
- **Migration planning** between environments
- **Audit and compliance** reporting
- **Usage analytics** and optimization

For comprehensive documentation, see the [Deployment Export Guide](deployment-export.md).

**Quick Examples:**

```bash
# Basic export to ./exports directory
vra deployment export-all

# Export with detailed resource information
vra deployment export-all --include-resources

# Export specific project to custom directory
vra deployment export-all --project dev-project-123 --output-dir /backup/vra

# Export excluding unsynced deployments
vra deployment export-all --no-unsynced
```

## Configuration and Best Practices

### Inputs Configuration

Define input parameters for catalog requests in a YAML or JSON file for complex setups.

#### Example inputs.yaml

```yaml
cpu: 2
memory: "4G"
disk: "100GB"
network: "corporate"
additionalDisks:
  - size: "500GB"

```

### Profiles and Environments

Switch between different profiles for dev and prod environments to manage access separately.

```bash
# List profiles
vra profile list

# Use production profile
vra profile use production
```

## Security Considerations

- **Use secure authentication** with bearer tokens directly from the CLI.
- **Do not store sensitive inputs** like passwords in files.
- **Validate SSL/TLS** for all direct API communications.

Always ensure your security policies comply with organization requirements and follow VMware recommendations for vRA installations.
