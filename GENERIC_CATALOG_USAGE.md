# Generic Catalog Operations - Usage Guide

The VMware vRA CLI now supports **generic, schema-driven catalog operations** that can work with any service catalog item described by a JSON schema file.

## 🚀 Quick Start

### 1. Load Your Schemas
```bash
# Load schemas from your exported schema directory
vra schema-catalog load-schemas --schema-dir ./inputs/schema_exports

# Load with custom pattern
vra schema-catalog load-schemas --pattern "*_schema.json"
```

### 2. Explore Available Items
```bash
# List all available catalog schemas
vra schema-catalog list-schemas

# Filter by type
vra schema-catalog list-schemas --type "VMware Aria Automation Templates"

# Filter by name
vra schema-catalog list-schemas --name "Virtual Machine"

# Search schemas
vra schema-catalog search-schemas "backup"
```

### 3. Inspect Schema Details
```bash
# Show detailed schema information
vra schema-catalog show-schema 99abceaf-1da3-3fad-aae7-b55b5084112e

# Export input template for a catalog item
vra schema-catalog export-inputs-template vm-create-inputs.json 99abceaf-1da3-3fad-aae7-b55b5084112e --project-id my-project-id
```

### 4. Execute Catalog Items
```bash
# Interactive execution with guided prompts
vra schema-catalog execute-schema 99abceaf-1da3-3fad-aae7-b55b5084112e --project-id my-project-id

# Use pre-filled input file
vra schema-catalog execute-schema 99abceaf-1da3-3fad-aae7-b55b5084112e --project-id my-project-id --input-file vm-inputs.json

# Dry run (validate without executing)
vra schema-catalog execute-schema 99abceaf-1da3-3fad-aae7-b55b5084112e --project-id my-project-id --dry-run

# Skip optional fields for faster execution
vra schema-catalog execute-schema 99abceaf-1da3-3fad-aae7-b55b5084112e --project-id my-project-id --skip-optional
```

## 🎯 Real-World Examples

### Example 1: Virtual Machine Creation
```bash
# 1. Find VM creation catalog items
vra schema-catalog search-schemas "Virtual Machine Create"

# 2. Inspect the schema
vra schema-catalog show-schema 99abceaf-1da3-3fad-aae7-b55b5084112e

# 3. Export template for batch operations
vra schema-catalog export-inputs-template vm-template.json 99abceaf-1da3-3fad-aae7-b55b5084112e --project-id dev-project

# 4. Customize the template (edit vm-template.json)
{
  "vmName": "web-server-001",
  "vCPUSize": 4,
  "vRAMSize": 8,
  "osDiskSize": 100,
  "region": "MOP",
  "asgName": "web-tier-asg",
  "imageName": "KPC-Win2K22"
}

# 5. Execute with custom inputs
vra schema-catalog execute-schema 99abceaf-1da3-3fad-aae7-b55b5084112e \
  --project-id dev-project \
  --deployment-name web-server-001-deployment \
  --input-file vm-template.json
```

### Example 2: Application Security Group Management
```bash
# 1. List security group operations
vra schema-catalog list-schemas --name "Security Group"

# 2. Create ASG interactively
vra schema-catalog execute-schema f2f10f4b-451b-387f-8f14-9d713726bd81 --project-id security-project
# CLI will prompt for:
# - Region: [dropdown with available regions]
# - ASG Name: [text input with pattern validation]
# - NSG Name: [dropdown with available NSGs]
# - Tenant Name: [pre-filled with default]

# 3. Remove ASG with minimal prompts
vra schema-catalog execute-schema 0dd2244a-20a3-3678-ae5d-e6e8d7b7b746 \
  --project-id security-project \
  --skip-optional
```

### Example 3: Batch Operations
```bash
# 1. Export templates for multiple operations
vra schema-catalog export-inputs-template disk-resize-template.json 86c73043-386c-3f94-af40-7dbde006300c --project-id ops-project

# 2. Create multiple input files
cp disk-resize-template.json disk-resize-vm1.json
cp disk-resize-template.json disk-resize-vm2.json
# Edit each file with specific VM details

# 3. Execute batch operations
for input_file in disk-resize-vm*.json; do
  echo "Processing $input_file..."
  vra schema-catalog execute-schema 86c73043-386c-3f94-af40-7dbde006300c \
    --project-id ops-project \
    --input-file "$input_file" \
    --deployment-name "disk-resize-$(basename $input_file .json)"
done
```

## 🔧 Advanced Features

### Schema Registry Management
```bash
# Check registry status
vra schema-catalog status

# Load from multiple directories
vra schema-catalog load-schemas --schema-dir /path/to/schemas1
vra schema-catalog load-schemas --schema-dir /path/to/schemas2

# Reload schemas (useful during development)
vra schema-catalog load-schemas --pattern "*_schema.json"
```

### Input Validation Features
- **Type validation**: Automatic type conversion (string, number, boolean, array)
- **Range validation**: Min/max values for numbers, min/max length for strings
- **Pattern validation**: Regular expression matching for strings
- **Choice validation**: Dropdown selection from predefined values
- **Dependency handling**: Fields that depend on other field values
- **Dynamic defaults**: Fields with computed default values

### Supported Schema Features
- ✅ **JSON Schema Draft-07** compatible
- ✅ **Dynamic data sources** (`$data` for API calls)
- ✅ **Dynamic defaults** (`$dynamicDefault` for computed values)
- ✅ **Cross-field dependencies** ({{variable}} substitution)
- ✅ **Validation constraints** (min, max, pattern, enum)
- ✅ **Required vs optional** fields
- ✅ **Multiple catalog types** (Templates + Workflows)

## 📊 Schema Statistics

From the analyzed 47 catalog schemas:
- **VMware Aria Automation Templates**: 4 items
- **Automation Orchestrator Workflows**: 43 items
- **Field types**: string, number, boolean, array
- **Advanced features**: 15+ schemas with dynamic data sources
- **Validation rules**: Pattern matching, range validation, choice lists

## 🎛️ Configuration

### Default Schema Directories
The CLI automatically searches these locations:
1. `./inputs/schema_exports/` (current directory)
2. `./schemas/` (current directory)  
3. `~/.vmware-vra-cli/schemas/` (user home)

### Environment Variables
```bash
export VRA_SCHEMA_DIR="/custom/schema/path"
export VRA_DEFAULT_PROJECT="my-default-project"
export VRA_SKIP_CONFIRMATION="false"  # Set to 'true' for automation
```

## 🚨 Error Handling

The system provides comprehensive error handling:
- **Schema validation errors** with specific field details
- **Input validation errors** with correction guidance
- **API execution errors** with detailed error messages
- **File operation errors** for schema loading and template export
- **Authentication errors** with token refresh attempts

## 🔮 Future Enhancements

Potential improvements for the generic catalog system:
1. **Dynamic data resolution** - Real API calls for `$data` sources
2. **Conditional fields** - Show/hide fields based on other values
3. **Batch execution** - Execute multiple catalog items in parallel
4. **Workflow templates** - Multi-step catalog item sequences
5. **Integration with MCP server** - AI-assisted catalog operations
6. **Configuration profiles** - Save and reuse common input patterns

---

This generic catalog system transforms the CLI from a fixed-function tool into a **universal VMware vRA automation platform** that can adapt to any service catalog configuration through JSON schema files.