# Practical Examples and Use Cases

This guide provides real-world examples and common usage patterns for the VMware vRA CLI tool, demonstrating how to solve typical infrastructure automation challenges.

## Basic Workflow Examples

### Example 1: Daily Development VM Setup

Automate the creation of development VMs with standardized configurations:

```bash
#!/bin/bash
# dev-vm-setup.sh

# Configuration
PROJECT_ID="dev-project-123"
CATALOG_ITEM="blueprint-ubuntu-dev"
DEV_TAG="tag-environment-dev"

# Function to create a dev VM
create_dev_vm() {
    local vm_name=$1
    local developer=$2
    
    echo "Creating development VM: $vm_name for $developer"
    
    # Request the catalog item
    DEPLOYMENT_ID=$(vmware-vra catalog request "$CATALOG_ITEM" \
        --project "$PROJECT_ID" \
        --name "$vm_name" \
        --inputs "{\"hostname\": \"$vm_name\", \"owner\": \"$developer\", \"cpu\": 4, \"memory\": \"8GB\"}" \
        --reason "Development environment for $developer" \
        --format json | jq -r '.deploymentId')
    
    if [[ "$DEPLOYMENT_ID" != "null" && -n "$DEPLOYMENT_ID" ]]; then
        echo "✅ Deployment created: $DEPLOYMENT_ID"
        
        # Wait for completion
        echo "⏳ Waiting for deployment to complete..."
        wait_for_deployment "$DEPLOYMENT_ID"
        
        # Add development environment tag
        vmware-vra tag assign "$DEPLOYMENT_ID" "$DEV_TAG"
        echo "🏷️ Tagged as development environment"
        
        # Create developer-specific tag
        DEV_TAG_ID=$(vmware-vra tag create "developer" --value "$developer" \
            --description "VM owner: $developer" --format json | jq -r '.id')
        vmware-vra tag assign "$DEPLOYMENT_ID" "$DEV_TAG_ID"
        
        echo "✅ Development VM ready: $vm_name"
    else
        echo "❌ Failed to create deployment"
        exit 1
    fi
}

# Function to wait for deployment completion
wait_for_deployment() {
    local deployment_id=$1
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        STATUS=$(vmware-vra deployment show "$deployment_id" --format json | jq -r '.status')
        
        case "$STATUS" in
            "CREATE_SUCCESSFUL")
                echo "✅ Deployment completed successfully"
                return 0
                ;;
            "CREATE_FAILED")
                echo "❌ Deployment failed"
                return 1
                ;;
            "CREATE_INPROGRESS")
                echo "⏳ Still in progress... (attempt $attempt/$max_attempts)"
                ;;
        esac
        
        sleep 30
        ((attempt++))
    done
    
    echo "⏰ Deployment timed out"
    return 1
}

# Main execution
if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <vm-name> <developer-email>"
    exit 1
fi

# Authenticate if needed
vmware-vra auth status | grep -q "Authenticated" || vmware-vra auth login

# Create the VM
create_dev_vm "$1" "$2"
```

### Example 2: Bulk VM Cleanup

Clean up multiple VMs based on tags or naming patterns:

```bash
#!/bin/bash
# cleanup-old-vms.sh

# Configuration
DAYS_OLD=7
DRY_RUN=${DRY_RUN:-true}  # Set to false to actually delete

echo "🧹 VM Cleanup Script"
echo "Looking for VMs older than $DAYS_OLD days..."

if [[ "$DRY_RUN" == "true" ]]; then
    echo "🔍 DRY RUN MODE - No actual deletions will occur"
fi

# Get all deployments
DEPLOYMENTS=$(vmware-vra deployment list --format json)

# Find old deployments
OLD_DEPLOYMENTS=$(echo "$DEPLOYMENTS" | jq -r --argjson days_old "$DAYS_OLD" '
    .[] | 
    select(.createdAt != null) |
    select((now - ((.createdAt | sub("\\+.*$"; "") | strptime("%Y-%m-%dT%H:%M:%S") | mktime))) / 86400 > $days_old) |
    .id
')

if [[ -z "$OLD_DEPLOYMENTS" ]]; then
    echo "✅ No old deployments found to clean up"
    exit 0
fi

echo "📋 Found $(echo "$OLD_DEPLOYMENTS" | wc -l) old deployments:"

# Process each old deployment
while IFS= read -r deployment_id; do
    if [[ -z "$deployment_id" ]]; then
        continue
    fi
    
    # Get deployment details
    DEPLOYMENT_INFO=$(vmware-vra deployment show "$deployment_id" --format json)
    DEPLOYMENT_NAME=$(echo "$DEPLOYMENT_INFO" | jq -r '.name')
    DEPLOYMENT_STATUS=$(echo "$DEPLOYMENT_INFO" | jq -r '.status')
    CREATED_AT=$(echo "$DEPLOYMENT_INFO" | jq -r '.createdAt')
    
    echo "🔍 Processing: $DEPLOYMENT_NAME ($deployment_id)"
    echo "   Status: $DEPLOYMENT_STATUS"
    echo "   Created: $CREATED_AT"
    
    # Check if deployment has 'temporary' or 'development' tags
    TAGS=$(vmware-vra tag resource-tags "$deployment_id" --format json 2>/dev/null || echo "[]")
    IS_TEMP=$(echo "$TAGS" | jq -r '.[] | select(.key == "lifecycle" and .value == "temporary") | .id')
    IS_DEV=$(echo "$TAGS" | jq -r '.[] | select(.key == "environment" and .value == "development") | .id')
    
    SHOULD_DELETE=false
    
    # Only delete if it's tagged as temporary or development
    if [[ -n "$IS_TEMP" ]] || [[ -n "$IS_DEV" ]]; then
        SHOULD_DELETE=true
        echo "   🏷️ Tagged for cleanup (temporary or development)"
    else
        echo "   ⚠️  No cleanup tags found - skipping for safety"
    fi
    
    if [[ "$SHOULD_DELETE" == "true" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            echo "   🔍 [DRY RUN] Would delete: $DEPLOYMENT_NAME"
        else
            echo "   🗑️ Deleting: $DEPLOYMENT_NAME"
            if vmware-vra deployment delete "$deployment_id" --confirm; then
                echo "   ✅ Deletion initiated for $DEPLOYMENT_NAME"
            else
                echo "   ❌ Failed to delete $DEPLOYMENT_NAME"
            fi
        fi
    fi
    
    echo
done <<< "$OLD_DEPLOYMENTS"

echo "🏁 Cleanup script completed"

if [[ "$DRY_RUN" == "true" ]]; then
    echo "💡 Run with DRY_RUN=false to perform actual deletions"
fi
```

## Advanced Automation Examples

### Example 3: Environment Migration

Export from one environment and prepare for migration to another:

```bash
#!/bin/bash
# environment-migration.sh

SOURCE_ENV="development"
TARGET_ENV="staging"
BACKUP_DIR="/backup/vra-migration/$(date +%Y-%m-%d)"

echo "🚚 Environment Migration: $SOURCE_ENV → $TARGET_ENV"
echo "📁 Backup directory: $BACKUP_DIR"

# Step 1: Export current environment
echo "📦 Step 1: Exporting current environment..."
mkdir -p "$BACKUP_DIR"

vmware-vra deployment export-all \
    --project "$SOURCE_ENV" \
    --output-dir "$BACKUP_DIR" \
    --include-resources

# Step 2: Generate migration analysis
echo "📊 Step 2: Generating migration analysis..."

# Get export summary
EXPORT_SUMMARY=$(cat "$BACKUP_DIR/export_summary.json")
TOTAL_DEPLOYMENTS=$(echo "$EXPORT_SUMMARY" | jq '.statistics.total_deployments')
CATALOG_ITEMS=$(echo "$EXPORT_SUMMARY" | jq '.statistics.catalog_items_with_deployments')

echo "Migration Analysis:"
echo "  Total deployments to migrate: $TOTAL_DEPLOYMENTS"
echo "  Catalog items involved: $CATALOG_ITEMS"
echo

# Step 3: Validate catalog items exist in target
echo "🔍 Step 3: Validating catalog items in target environment..."

MISSING_ITEMS=()
for file in "$BACKUP_DIR"/*.json; do
    if [[ "$file" == *"unsynced_deployments.json"* ]] || [[ "$file" == *"export_summary.json"* ]]; then
        continue
    fi
    
    CATALOG_ITEM_ID=$(cat "$file" | jq -r '.catalog_item_id')
    CATALOG_ITEM_NAME=$(cat "$file" | jq -r '.catalog_item_info.name')
    
    echo "   Checking: $CATALOG_ITEM_NAME ($CATALOG_ITEM_ID)"
    
    # Check if catalog item exists in target (assuming we switch environments)
    if ! vmware-vra catalog show "$CATALOG_ITEM_ID" >/dev/null 2>&1; then
        echo "   ⚠️  Missing in target: $CATALOG_ITEM_NAME"
        MISSING_ITEMS+=("$CATALOG_ITEM_NAME")
    else
        echo "   ✅ Available in target: $CATALOG_ITEM_NAME"
    fi
done

# Step 4: Generate migration report
echo "📋 Step 4: Generating migration report..."

cat << EOF > "$BACKUP_DIR/migration-report.md"
# Migration Report: $SOURCE_ENV → $TARGET_ENV

## Summary
- **Date**: $(date)
- **Source Environment**: $SOURCE_ENV
- **Target Environment**: $TARGET_ENV
- **Total Deployments**: $TOTAL_DEPLOYMENTS
- **Catalog Items**: $CATALOG_ITEMS

## Catalog Item Validation

### Available in Target
$(for file in "$BACKUP_DIR"/*.json; do
    if [[ "$file" != *"unsynced_deployments.json"* ]] && [[ "$file" != *"export_summary.json"* ]]; then
        CATALOG_ITEM_ID=$(cat "$file" | jq -r '.catalog_item_id')
        CATALOG_ITEM_NAME=$(cat "$file" | jq -r '.catalog_item_info.name')
        DEPLOYMENT_COUNT=$(cat "$file" | jq -r '.deployment_count')
        if vmware-vra catalog show "$CATALOG_ITEM_ID" >/dev/null 2>&1; then
            echo "- ✅ **$CATALOG_ITEM_NAME** ($DEPLOYMENT_COUNT deployments)"
        fi
    fi
done)

### Missing in Target
$(for item in "${MISSING_ITEMS[@]}"; do
    echo "- ❌ **$item** - Needs to be created or mapped"
done)

## Next Steps

1. **Address Missing Catalog Items**: Create or map missing catalog items in target environment
2. **Review Configurations**: Validate input parameters are compatible
3. **Plan Migration Strategy**: Decide on recreation vs. import approach
4. **Test Migration**: Start with a small subset of deployments
5. **Execute Migration**: Run full migration once validated

## Files Generated
- \`export_summary.json\` - Complete export statistics
- \`*_<catalog-id>.json\` - Individual catalog item deployments
- \`unsynced_deployments.json\` - Deployments without catalog associations
- \`migration-report.md\` - This report

EOF

echo "✅ Migration analysis complete!"
echo "📄 Report saved: $BACKUP_DIR/migration-report.md"

if [[ ${#MISSING_ITEMS[@]} -gt 0 ]]; then
    echo "⚠️  Warning: ${#MISSING_ITEMS[@]} catalog items missing in target environment"
    echo "📋 Review migration-report.md for details"
fi
```

### Example 4: Automated Testing Pipeline

Integration with CI/CD for infrastructure testing:

```bash
#!/bin/bash
# infrastructure-test-pipeline.sh

# CI/CD Pipeline Integration for Infrastructure Testing
set -e

PIPELINE_ID=${CI_PIPELINE_ID:-"local-$(date +%s)"}
PROJECT_ID=${TEST_PROJECT_ID:-"test-project-123"}
CATALOG_ITEM=${TEST_CATALOG_ITEM:-"blueprint-test-vm"}
CLEANUP_ON_SUCCESS=${CLEANUP_ON_SUCCESS:-"true"}

echo "🔬 Infrastructure Test Pipeline"
echo "Pipeline ID: $PIPELINE_ID"
echo "Project: $PROJECT_ID"
echo "Catalog Item: $CATALOG_ITEM"

# Test configuration
TESTS=(
    "test_vm_creation"
    "test_vm_connectivity"
    "test_vm_configuration"
    "test_vm_performance"
)

DEPLOYMENT_ID=""
TEST_RESULTS=()

# Cleanup function
cleanup() {
    if [[ -n "$DEPLOYMENT_ID" ]] && [[ "$CLEANUP_ON_SUCCESS" == "true" ]]; then
        echo "🧹 Cleaning up test deployment: $DEPLOYMENT_ID"
        vmware-vra deployment delete "$DEPLOYMENT_ID" --confirm || true
    fi
}
trap cleanup EXIT

# Test 1: VM Creation
test_vm_creation() {
    echo "🧪 Test 1: VM Creation"
    
    local vm_name="test-vm-${PIPELINE_ID}"
    
    DEPLOYMENT_ID=$(vmware-vra catalog request "$CATALOG_ITEM" \
        --project "$PROJECT_ID" \
        --name "$vm_name" \
        --inputs '{"cpu": 2, "memory": "4GB", "disk": "50GB"}' \
        --reason "Automated infrastructure test - Pipeline $PIPELINE_ID" \
        --format json | jq -r '.deploymentId')
    
    if [[ "$DEPLOYMENT_ID" == "null" ]] || [[ -z "$DEPLOYMENT_ID" ]]; then
        echo "❌ Failed to create test deployment"
        return 1
    fi
    
    echo "✅ Deployment request submitted: $DEPLOYMENT_ID"
    
    # Wait for completion with timeout
    local max_wait=1800  # 30 minutes
    local waited=0
    
    while [[ $waited -lt $max_wait ]]; do
        local status=$(vmware-vra deployment show "$DEPLOYMENT_ID" --format json | jq -r '.status')
        
        case "$status" in
            "CREATE_SUCCESSFUL")
                echo "✅ VM creation successful"
                return 0
                ;;
            "CREATE_FAILED")
                echo "❌ VM creation failed"
                vmware-vra deployment show "$DEPLOYMENT_ID"
                return 1
                ;;
            "CREATE_INPROGRESS")
                echo "⏳ VM creation in progress... (${waited}s elapsed)"
                sleep 30
                waited=$((waited + 30))
                ;;
            *)
                echo "⚠️ Unknown status: $status"
                sleep 30
                waited=$((waited + 30))
                ;;
        esac
    done
    
    echo "⏰ VM creation timed out after ${max_wait}s"
    return 1
}

# Test 2: VM Connectivity
test_vm_connectivity() {
    echo "🧪 Test 2: VM Connectivity"
    
    # Get VM IP address from resources
    local resources=$(vmware-vra deployment resources "$DEPLOYMENT_ID" --format json)
    local vm_ip=$(echo "$resources" | jq -r '.[] | select(.type | contains("Machine")) | .properties.address // empty' | head -n1)
    
    if [[ -z "$vm_ip" ]] || [[ "$vm_ip" == "null" ]]; then
        echo "❌ Could not determine VM IP address"
        return 1
    fi
    
    echo "🔍 Testing connectivity to VM: $vm_ip"
    
    # Test ping connectivity
    if ping -c 3 "$vm_ip" >/dev/null 2>&1; then
        echo "✅ VM is reachable via ping"
    else
        echo "❌ VM is not reachable via ping"
        return 1
    fi
    
    # Test SSH connectivity (if applicable)
    if command -v nc >/dev/null 2>&1; then
        if nc -z -w5 "$vm_ip" 22 2>/dev/null; then
            echo "✅ VM SSH port is accessible"
        else
            echo "⚠️ VM SSH port is not accessible (may be expected)"
        fi
    fi
    
    return 0
}

# Test 3: VM Configuration
test_vm_configuration() {
    echo "🧪 Test 3: VM Configuration"
    
    local deployment_info=$(vmware-vra deployment show "$DEPLOYMENT_ID" --format json)
    local inputs=$(echo "$deployment_info" | jq '.inputs')
    
    echo "🔍 Verifying deployment configuration..."
    
    # Check if inputs match expected values
    local expected_cpu=2
    local actual_cpu=$(echo "$inputs" | jq -r '.cpu // empty')
    
    if [[ "$actual_cpu" == "$expected_cpu" ]]; then
        echo "✅ CPU configuration correct: $actual_cpu"
    else
        echo "❌ CPU configuration mismatch: expected $expected_cpu, got $actual_cpu"
        return 1
    fi
    
    local expected_memory="4GB"
    local actual_memory=$(echo "$inputs" | jq -r '.memory // empty')
    
    if [[ "$actual_memory" == "$expected_memory" ]]; then
        echo "✅ Memory configuration correct: $actual_memory"
    else
        echo "❌ Memory configuration mismatch: expected $expected_memory, got $actual_memory"
        return 1
    fi
    
    return 0
}

# Test 4: VM Performance (placeholder)
test_vm_performance() {
    echo "🧪 Test 4: VM Performance"
    echo "⚠️ Performance testing not implemented in this example"
    echo "✅ Performance test placeholder passed"
    return 0
}

# Main test execution
echo "🚀 Starting infrastructure tests..."

# Authenticate
if ! vmware-vra auth status | grep -q "Authenticated"; then
    echo "🔐 Authentication required"
    exit 1
fi

# Run tests
FAILED_TESTS=0
for test in "${TESTS[@]}"; do
    echo
    echo "===========================================" 
    if $test; then
        TEST_RESULTS+=("✅ $test: PASSED")
    else
        TEST_RESULTS+=("❌ $test: FAILED")
        ((FAILED_TESTS++))
    fi
    echo "==========================================="
done

# Summary
echo
echo "📊 Test Summary:"
for result in "${TEST_RESULTS[@]}"; do
    echo "  $result"
done

echo
if [[ $FAILED_TESTS -eq 0 ]]; then
    echo "🎉 All tests passed!"
    exit 0
else
    echo "💥 $FAILED_TESTS test(s) failed!"
    exit 1
fi
```

## Monitoring and Analytics Examples

### Example 5: Resource Usage Dashboard

Generate a comprehensive resource usage report:

```bash
#!/bin/bash
# resource-usage-dashboard.sh

OUTPUT_DIR="./reports/$(date +%Y-%m-%d)"
mkdir -p "$OUTPUT_DIR"

echo "📊 Generating Resource Usage Dashboard"
echo "📁 Output directory: $OUTPUT_DIR"

# Generate all reports
echo "📈 Generating catalog usage report..."
vmware-vra report catalog-usage --detailed-resources --include-zero \
    --format json > "$OUTPUT_DIR/catalog-usage.json"

echo "📅 Generating activity timeline..."
vmware-vra report activity-timeline --days-back 90 --group-by day \
    --format json > "$OUTPUT_DIR/activity-timeline.json"

echo "🔍 Generating unsync report..."
vmware-vra report unsync --detailed-resources \
    --format json > "$OUTPUT_DIR/unsync-report.json"

echo "📦 Exporting all deployments..."
vmware-vra deployment export-all \
    --output-dir "$OUTPUT_DIR/exports" \
    --include-resources

# Generate resources usage report
echo "📊 Generating resources usage report..."
vmware-vra report resources-usage --detailed-resources \
    --format json > "$OUTPUT_DIR/resources-usage.json"

# Generate HTML dashboard
cat << 'EOF' > "$OUTPUT_DIR/dashboard.html"
<!DOCTYPE html>
<html>
<head>
    <title>vRA Resource Usage Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .chart-container { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
        .stats { display: flex; gap: 20px; margin: 20px 0; }
        .stat-card { flex: 1; padding: 20px; background: #f5f5f5; border-radius: 8px; text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; color: #2196F3; }
    </style>
</head>
<body>
    <div class="container">
        <h1>vRA Resource Usage Dashboard</h1>
        <p>Generated: <span id="timestamp"></span></p>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number" id="total-deployments">-</div>
                <div>Total Deployments</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="active-items">-</div>
                <div>Active Catalog Items</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="unsynced-count">-</div>
                <div>Unsynced Deployments</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h2>Catalog Item Usage</h2>
            <canvas id="catalogChart"></canvas>
        </div>
        
        <div class="chart-container">
            <h2>Activity Timeline (Last 90 Days)</h2>
            <canvas id="timelineChart"></canvas>
        </div>
    </div>
    
    <script>
        // Load and process data
        document.getElementById('timestamp').textContent = new Date().toLocaleString();
        
        // This would normally load from the JSON files
        // For demo purposes, showing structure only
        fetch('./catalog-usage.json')
            .then(response => response.json())
            .then(data => {
                // Update statistics
                document.getElementById('total-deployments').textContent = 
                    data.summary?.total_deployments_system_wide || 0;
                document.getElementById('active-items').textContent = 
                    data.summary?.active_items || 0;
                
                // Create catalog usage chart
                const ctx1 = document.getElementById('catalogChart').getContext('2d');
                new Chart(ctx1, {
                    type: 'bar',
                    data: {
                        labels: data.catalog_items?.slice(0, 10).map(item => item.name) || [],
                        datasets: [{
                            label: 'Deployments',
                            data: data.catalog_items?.slice(0, 10).map(item => item.deployment_count) || [],
                            backgroundColor: 'rgba(33, 150, 243, 0.8)'
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: { beginAtZero: true }
                        }
                    }
                });
            })
            .catch(err => console.error('Error loading catalog usage data:', err));
        
        fetch('./unsync-report.json')
            .then(response => response.json())
            .then(data => {
                document.getElementById('unsynced-count').textContent = 
                    data.summary?.unsynced_deployments || 0;
            })
            .catch(err => console.error('Error loading unsync data:', err));
            
        fetch('./activity-timeline.json')
            .then(response => response.json())
            .then(data => {
                // Create timeline chart
                const ctx2 = document.getElementById('timelineChart').getContext('2d');
                const periods = Object.keys(data.period_activity || {}).sort();
                
                new Chart(ctx2, {
                    type: 'line',
                    data: {
                        labels: periods,
                        datasets: [{
                            label: 'Total Deployments',
                            data: periods.map(p => data.period_activity[p]?.total_deployments || 0),
                            borderColor: 'rgb(33, 150, 243)',
                            tension: 0.1
                        }, {
                            label: 'Successful',
                            data: periods.map(p => data.period_activity[p]?.successful_deployments || 0),
                            borderColor: 'rgb(76, 175, 80)',
                            tension: 0.1
                        }, {
                            label: 'Failed',
                            data: periods.map(p => data.period_activity[p]?.failed_deployments || 0),
                            borderColor: 'rgb(244, 67, 54)',
                            tension: 0.1
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: { beginAtZero: true }
                        }
                    }
                });
            })
            .catch(err => console.error('Error loading timeline data:', err));
    </script>
</body>
</html>
EOF

echo "✅ Dashboard generated: $OUTPUT_DIR/dashboard.html"
echo "🌐 Open the HTML file in your browser to view the dashboard"

# Generate summary report
cat << EOF > "$OUTPUT_DIR/summary.txt"
vRA Resource Usage Summary
Generated: $(date)

=== Quick Stats ===
$(vmware-vra deployment list --first-page-only | grep -E "Deployments \([0-9]+ items\)" || echo "Deployments: Unable to fetch")
$(vmware-vra catalog list --first-page-only | grep -E "Service Catalog Items \([0-9]+ items\)" || echo "Catalog Items: Unable to fetch")

=== Files Generated ===
- catalog-usage.json      : Detailed catalog item usage statistics
- activity-timeline.json  : 90-day deployment activity timeline
- unsync-report.json      : Analysis of unsynced deployments
- exports/                : Complete deployment export
- dashboard.html          : Interactive HTML dashboard
- summary.txt            : This summary file

=== Next Steps ===
1. Open dashboard.html in your browser
2. Review catalog-usage.json for optimization opportunities
3. Check unsync-report.json for deployment issues
4. Use exports/ for backup or migration planning

EOF

echo "📄 Summary saved: $OUTPUT_DIR/summary.txt"
echo "🎉 Resource usage dashboard generation complete!"
```

## Error Handling and Best Practices

### Example 6: Robust Error Handling

Template for production-ready scripts with comprehensive error handling:

```bash
#!/bin/bash
# robust-vra-script-template.sh

# Exit on any error
set -e

# Configuration
SCRIPT_NAME=$(basename "$0")
LOG_FILE="/tmp/${SCRIPT_NAME%.*}-$(date +%Y%m%d-%H%M%S).log"
VERBOSE=${VERBOSE:-false}
DRY_RUN=${DRY_RUN:-false}

# Error handling
error_exit() {
    echo "ERROR: $1" >&2
    echo "Check log file: $LOG_FILE" >&2
    exit "${2:-1}"
}

log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
    
    if [[ "$level" == "ERROR" ]]; then
        echo "$message" >&2
    fi
}

verbose_log() {
    if [[ "$VERBOSE" == "true" ]]; then
        log "DEBUG" "$@"
    fi
}

# Function to check prerequisites
check_prerequisites() {
    log "INFO" "Checking prerequisites..."
    
    # Check if CLI is available
    if ! command -v vmware-vra >/dev/null 2>&1; then
        error_exit "vmware-vra CLI not found in PATH"
    fi
    
    # Check authentication
    if ! vmware-vra auth status | grep -q "Authenticated"; then
        error_exit "Not authenticated. Run 'vmware-vra auth login' first"
    fi
    
    # Check required environment variables
    if [[ -z "${PROJECT_ID:-}" ]]; then
        error_exit "PROJECT_ID environment variable is required"
    fi
    
    # Test basic connectivity
    if ! vmware-vra catalog list --first-page-only >/dev/null 2>&1; then
        error_exit "Cannot connect to vRA API. Check authentication and connectivity"
    fi
    
    log "INFO" "Prerequisites check passed"
}

# Function to safely execute vRA commands
safe_vra_command() {
    local description="$1"
    shift
    
    log "INFO" "Executing: $description"
    verbose_log "$@"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "INFO" "[DRY RUN] Would execute: $*"
        return 0
    fi
    
    local output
    local exit_code
    
    # Execute command and capture output
    if output=$("$@" 2>&1); then
        exit_code=0
        verbose_log "Command output: $output"
    else
        exit_code=$?
        log "ERROR" "Command failed (exit code: $exit_code): $*"
        log "ERROR" "Output: $output"
        return $exit_code
    fi
    
    # Return output via stdout for chaining
    echo "$output"
    return $exit_code
}

# Function to wait for deployment with timeout
wait_for_deployment() {
    local deployment_id="$1"
    local timeout_seconds="${2:-1800}"  # 30 minutes default
    local check_interval="${3:-30}"     # 30 seconds default
    
    log "INFO" "Waiting for deployment $deployment_id to complete (timeout: ${timeout_seconds}s)"
    
    local elapsed=0
    local status
    
    while [[ $elapsed -lt $timeout_seconds ]]; do
        if status=$(safe_vra_command "Check deployment status" \
            vmware-vra deployment show "$deployment_id" --format json | jq -r '.status'); then
            
            case "$status" in
                "CREATE_SUCCESSFUL"|"UPDATE_SUCCESSFUL")
                    log "INFO" "Deployment completed successfully: $status"
                    return 0
                    ;;
                "CREATE_FAILED"|"UPDATE_FAILED"|"FAILED")
                    log "ERROR" "Deployment failed: $status"
                    # Get failure details
                    safe_vra_command "Get deployment details" \
                        vmware-vra deployment show "$deployment_id" | head -20
                    return 1
                    ;;
                "CREATE_INPROGRESS"|"UPDATE_INPROGRESS"|"INPROGRESS")
                    verbose_log "Deployment in progress: $status (${elapsed}s elapsed)"
                    ;;
                *)
                    verbose_log "Unknown deployment status: $status"
                    ;;
            esac
        else
            log "WARN" "Failed to check deployment status, retrying..."
        fi
        
        sleep "$check_interval"
        elapsed=$((elapsed + check_interval))
    done
    
    log "ERROR" "Deployment timed out after ${timeout_seconds}s"
    return 1
}

# Main function
main() {
    log "INFO" "Starting $SCRIPT_NAME"
    log "INFO" "Log file: $LOG_FILE"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "INFO" "DRY RUN MODE - No actual changes will be made"
    fi
    
    # Check prerequisites
    check_prerequisites
    
    # Your main logic here
    log "INFO" "Main script logic would go here"
    
    # Example: Create a deployment
    local deployment_id
    if deployment_id=$(safe_vra_command "Request catalog item" \
        vmware-vra catalog request "$CATALOG_ITEM_ID" \
        --project "$PROJECT_ID" \
        --name "example-deployment-$(date +%s)" \
        --inputs '{"cpu": 2, "memory": "4GB"}' \
        --format json | jq -r '.deploymentId'); then
        
        log "INFO" "Deployment created: $deployment_id"
        
        # Wait for completion
        if wait_for_deployment "$deployment_id"; then
            log "INFO" "Script completed successfully"
        else
            error_exit "Deployment failed to complete"
        fi
    else
        error_exit "Failed to create deployment"
    fi
}

# Cleanup function
cleanup() {
    log "INFO" "Performing cleanup..."
    # Add cleanup logic here
}

# Set up signal handlers
trap cleanup EXIT
trap 'error_exit "Script interrupted by user" 130' INT TERM

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --dry-run|-n)
            DRY_RUN=true
            shift
            ;;
        --help|-h)
            cat << EOF
Usage: $SCRIPT_NAME [OPTIONS]

Options:
  --verbose, -v     Enable verbose logging
  --dry-run, -n     Show what would be done without making changes
  --help, -h        Show this help message

Environment Variables:
  PROJECT_ID        Required: vRA project ID
  CATALOG_ITEM_ID   Required: Catalog item to deploy
  VERBOSE           Set to 'true' to enable verbose logging
  DRY_RUN           Set to 'true' to enable dry run mode

Example:
  PROJECT_ID=dev-123 CATALOG_ITEM_ID=blueprint-vm $SCRIPT_NAME --verbose
EOF
            exit 0
            ;;
        *)
            error_exit "Unknown option: $1"
            ;;
    esac
done

# Validate required variables
if [[ -z "${PROJECT_ID:-}" ]]; then
    error_exit "PROJECT_ID environment variable is required"
fi

if [[ -z "${CATALOG_ITEM_ID:-}" ]]; then
    error_exit "CATALOG_ITEM_ID environment variable is required"
fi

# Run main function
main "$@"

log "INFO" "$SCRIPT_NAME completed successfully"
```

These examples demonstrate practical, real-world usage patterns for the VMware vRA CLI tool, showing how to build robust automation solutions for common infrastructure management tasks.
