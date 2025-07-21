# VMware vRA CLI Troubleshooting Guide

This guide helps you diagnose and resolve common issues when using the VMware vRA CLI tool.

## General Troubleshooting Steps

### Enable Verbose Mode

Always start troubleshooting with verbose mode to see detailed HTTP request/response information:

```bash
vmware-vra --verbose [command]
```

**Example:**
```bash
vmware-vra --verbose auth login
vmware-vra --verbose catalog list
vmware-vra --verbose deployment export-all
```

### Check CLI Version and Environment

```bash
# Check CLI version
vmware-vra --version

# Check current configuration
vmware-vra config show

# Check authentication status
vmware-vra auth status
```

### Verify Network Connectivity

```bash
# Test basic connectivity to vRA server
curl -k https://your-vra-server.com/health

# Test with authentication (replace with your actual token)
curl -k -H "Authorization: Bearer your-token" https://your-vra-server.com/catalog/api/items
```

## Authentication Issues

### Issue: "No valid authentication token found"

**Symptoms:**
```
❌ No valid authentication token found. Please run 'vra auth login' first.
```

**Solutions:**

1. **Re-authenticate:**
   ```bash
   vmware-vra auth login --username your-username --url https://vra.example.com
   ```

2. **Check stored tokens:**
   ```bash
   vmware-vra auth status
   ```

3. **Clear and re-authenticate:**
   ```bash
   vmware-vra auth logout
   vmware-vra auth login
   ```

### Issue: "Authentication failed: 401 Unauthorized"

**Symptoms:**
```
❌ Authentication failed: 401 Unauthorized
```

**Possible Causes and Solutions:**

1. **Invalid credentials:**
   - Verify username and password
   - Check if account is locked or disabled

2. **Wrong domain (for multiple identity sources):**
   ```bash
   vmware-vra auth login --username admin --domain vsphere.local
   ```

3. **Wrong tenant:**
   ```bash
   vmware-vra auth login --tenant correct-tenant.local
   ```

4. **Wrong vRA URL:**
   ```bash
   vmware-vra auth login --url https://correct-vra.example.com
   ```

### Issue: "SSL Certificate Verification Failed"

**Symptoms:**
```
SSL: CERTIFICATE_VERIFY_FAILED
requests.exceptions.SSLError: HTTPSConnectionPool
```

**Solutions:**

1. **Disable SSL verification (NOT recommended for production):**
   ```bash
   vmware-vra config set verify_ssl false
   ```

2. **Add certificate to system trust store (recommended):**
   - Download the vRA certificate
   - Add to your system's certificate store
   - Restart CLI

3. **Use proper certificate setup:**
   - Ensure vRA has valid SSL certificate
   - Verify certificate chain is complete

### Issue: "Token expired" errors during operations

**Symptoms:**
```
403 Forbidden - Token expired
```

**Solutions:**

1. **Refresh token manually:**
   ```bash
   vmware-vra auth refresh
   ```

2. **Re-authenticate if refresh fails:**
   ```bash
   vmware-vra auth login
   ```

3. **Check token expiration:**
   ```bash
   vmware-vra auth status
   ```

## Permission and Authorization Issues

### Issue: "403 Forbidden" on specific operations

**Symptoms:**
```
Failed to list deployments: 403 Forbidden
Failed to request catalog item: 403 Forbidden
```

**Required Roles by Operation:**

| Operation | Minimum Required Role |
|-----------|----------------------|
| List catalog items | Service Catalog User |
| Request catalog items | Service Catalog User + Project access |
| List all deployments | Service Catalog User |
| List project deployments | Project Member |
| Delete deployments | Project Administrator |
| Export all deployments | Service Catalog User (system-wide) or Project Administrator (project-specific) |
| Tag management | Depends on resource - see below |

**Tag Management Permissions:**
- **List tags**: Service Catalog User
- **Create/Delete tags**: Organization Administrator
- **Assign/Remove tags**: Resource owner or Project Administrator

**Solutions:**

1. **Check your roles in vRA:**
   - Log into vRA web interface
   - Check assigned roles in user profile
   - Contact administrator for role assignment

2. **Use project-specific operations:**
   ```bash
   # Instead of system-wide list
   vmware-vra deployment list --project your-project-id
   
   # Instead of full export
   vmware-vra deployment export-all --project your-project-id
   ```

3. **Request appropriate permissions:**
   - Contact your vRA administrator
   - Request minimum required roles for your use case

## Network and Connectivity Issues

### Issue: Connection timeouts

**Symptoms:**
```
requests.exceptions.ConnectTimeout
Connection timed out after 30 seconds
```

**Solutions:**

1. **Increase timeout:**
   ```bash
   vmware-vra config set timeout 120
   ```

2. **Check network connectivity:**
   ```bash
   ping your-vra-server.com
   telnet your-vra-server.com 443
   ```

3. **Check proxy settings:**
   ```bash
   # Set proxy if required
   export HTTP_PROXY=http://proxy.company.com:8080
   export HTTPS_PROXY=http://proxy.company.com:8080
   ```

### Issue: DNS resolution failures

**Symptoms:**
```
requests.exceptions.ConnectionError: [Errno -2] Name or service not known
```

**Solutions:**

1. **Verify DNS resolution:**
   ```bash
   nslookup your-vra-server.com
   ```

2. **Use IP address instead:**
   ```bash
   vmware-vra config set api_url https://192.168.1.100
   ```

3. **Check /etc/hosts file:**
   ```bash
   # Add entry if needed
   echo "192.168.1.100 vra.company.com" >> /etc/hosts
   ```

## Export-Specific Issues

### Issue: Export command hangs or times out

**Symptoms:**
```
# Command appears to hang indefinitely
vmware-vra deployment export-all
# No output for extended period
```

**Solutions:**

1. **Use project filtering to reduce scope:**
   ```bash
   vmware-vra deployment export-all --project specific-project-id
   ```

2. **Disable resource details (faster):**
   ```bash
   vmware-vra deployment export-all --no-unsynced
   ```

3. **Increase timeout:**
   ```bash
   vmware-vra config set timeout 300
   ```

4. **Check system resources:**
   ```bash
   # Check available memory and disk space
   df -h
   free -h
   ```

### Issue: "No space left on device" during export

**Symptoms:**
```
IOError: [Errno 28] No space left on device
```

**Solutions:**

1. **Check available space:**
   ```bash
   df -h
   ```

2. **Use external storage:**
   ```bash
   vmware-vra deployment export-all --output-dir /mnt/external-storage/exports
   ```

3. **Clean up existing exports:**
   ```bash
   # Compress old exports
   find ./exports -name "*.json" -mtime +7 -exec gzip {} \;
   
   # Remove very old exports
   find ./exports -name "*.gz" -mtime +30 -delete
   ```

4. **Export in smaller chunks:**
   ```bash
   # Export each project separately
   for project in project1 project2 project3; do
     vmware-vra deployment export-all --project "$project" --output-dir "./exports/$project"
   done
   ```

### Issue: Export creates empty or incomplete files

**Symptoms:**
- Export completes but files are empty
- Missing expected deployments in export

**Solutions:**

1. **Verify permissions:**
   ```bash
   # Check if you have permission to see all deployments
   vmware-vra deployment list --first-page-only
   ```

2. **Check export summary:**
   ```bash
   # Look at the export summary for clues
   cat ./exports/export_summary.json | jq '.statistics'
   ```

3. **Enable verbose mode:**
   ```bash
   vmware-vra --verbose deployment export-all --output-dir ./debug-export
   ```

4. **Validate export files:**
   ```bash
   # Check if JSON files are valid
   for file in ./exports/*.json; do
     echo "Validating: $file"
     python -m json.tool "$file" > /dev/null && echo "✓ Valid" || echo "✗ Invalid"
   done
   ```

## Configuration Issues

### Issue: "Config file not found" or configuration not persisting

**Symptoms:**
```
Configuration changes don't persist between sessions
Config file errors
```

**Solutions:**

1. **Check config file location:**
   ```bash
   vmware-vra config show
   # Look for config file path at bottom
   ```

2. **Create config directory manually:**
   ```bash
   mkdir -p ~/.config/vmware-vra-cli
   ```

3. **Set configuration manually:**
   ```bash
   vmware-vra config set api_url https://vra.example.com
   vmware-vra config set tenant company.local
   ```

4. **Check file permissions:**
   ```bash
   ls -la ~/.config/vmware-vra-cli/config.json
   # Should be readable/writable by user
   ```

### Issue: Environment variables not being recognized

**Symptoms:**
- Environment variables don't override config
- Settings revert to defaults

**Solutions:**

1. **Verify environment variable names:**
   ```bash
   # Correct variable names:
   export VRA_URL="https://vra.example.com"
   export VRA_TENANT="company.local"
   export VRA_DOMAIN="vsphere.local"
   export VRA_VERIFY_SSL="true"
   export VRA_TIMEOUT="60"
   ```

2. **Check variable values:**
   ```bash
   env | grep VRA_
   ```

3. **Test with explicit values:**
   ```bash
   VRA_URL="https://test.example.com" vmware-vra config show
   ```

## Data and JSON Issues

### Issue: "JSON decode error" when parsing responses

**Symptoms:**
```
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

**Solutions:**

1. **Check vRA server status:**
   ```bash
   curl -k https://vra.example.com/health
   ```

2. **Verify API endpoints:**
   ```bash
   # Test with curl
   curl -k -H "Authorization: Bearer your-token" \
     "https://vra.example.com/catalog/api/items" | jq .
   ```

3. **Check for HTML error pages:**
   ```bash
   # Enable verbose mode to see raw responses
   vmware-vra --verbose catalog list
   ```

4. **Verify vRA version compatibility:**
   - Check if your vRA version is supported
   - Some API endpoints may differ between versions

### Issue: Unicode or character encoding errors

**Symptoms:**
```
UnicodeDecodeError: 'utf-8' codec can't decode byte
```

**Solutions:**

1. **Check system locale:**
   ```bash
   locale
   # Ensure UTF-8 locale is set
   ```

2. **Set UTF-8 environment:**
   ```bash
   export LANG=en_US.UTF-8
   export LC_ALL=en_US.UTF-8
   ```

3. **Check deployment/catalog item names:**
   - Some special characters may cause issues
   - Contact administrator to fix problematic names

## Performance Issues

### Issue: Slow CLI operations

**Symptoms:**
- Commands take much longer than expected
- Large environments cause timeouts

**Solutions:**

1. **Use pagination options:**
   ```bash
   # Fetch only first page for quick results
   vmware-vra catalog list --first-page-only
   vmware-vra deployment list --first-page-only
   ```

2. **Increase page sizes:**
   ```bash
   # Get more items per request
   vmware-vra catalog list --page-size 2000
   ```

3. **Filter by project:**
   ```bash
   # Reduce scope of operations
   vmware-vra deployment list --project your-project-id
   ```

4. **Avoid resource details when not needed:**
   ```bash
   # Faster export without resource details
   vmware-vra deployment export-all --no-unsynced
   ```

## Platform-Specific Issues

### Windows Issues

**Issue: SSL errors on Windows**

**Solution:**
```cmd
# Update certificate store
certlm.msc
# Import vRA certificate manually
```

**Issue: Path issues with PowerShell**

**Solution:**
```powershell
# Use forward slashes or escape backslashes
vmware-vra deployment export-all --output-dir "./exports"
# or
vmware-vra deployment export-all --output-dir "C:\\backup\\exports"
```

### macOS Issues

**Issue: SSL certificate verification on macOS**

**Solution:**
```bash
# Add certificate to keychain
security add-trusted-cert -d -r trustRoot -k ~/Library/Keychains/login.keychain certificate.crt
```

### Linux Issues

**Issue: Missing dependencies**

**Solution:**
```bash
# Install required packages (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install python3-pip curl jq

# Install required packages (RHEL/CentOS)
sudo yum install python3-pip curl jq
```

## Debugging Tools and Techniques

### HTTP Traffic Analysis

Use tools to analyze HTTP traffic:

```bash
# Using mitmproxy (requires setup)
mitmdump -s script.py

# Using tcpdump (requires root)
sudo tcpdump -i any port 443

# Using curl to test specific endpoints
curl -k -H "Authorization: Bearer token" \
  "https://vra.example.com/catalog/api/items" -v
```

### Log Analysis

Enable comprehensive logging:

```bash
# Create log directory
mkdir -p ~/.cache/vmware-vra-cli/logs

# Enable debug logging (if supported by CLI)
export VRA_DEBUG=true
vmware-vra --verbose catalog list 2>&1 | tee debug.log
```

### JSON Response Analysis

Analyze responses for debugging:

```bash
# Pretty print JSON responses
vmware-vra --format json catalog list | jq .

# Filter specific fields
vmware-vra --format json deployment list | jq '.[].status' | sort | uniq -c

# Find problematic entries
vmware-vra --format json catalog list | jq '.[] | select(.name | contains("special-chars"))'
```

## Getting Help

### CLI Help

```bash
# Global help
vmware-vra --help

# Command-specific help
vmware-vra deployment --help
vmware-vra deployment export-all --help

# Show all available commands
vmware-vra --help | grep -A 100 "Commands:"
```

### Collecting Diagnostic Information

When reporting issues, collect this information:

```bash
#!/bin/bash
# diagnostic-info.sh

echo "=== VMware vRA CLI Diagnostic Information ==="
echo "Date: $(date)"
echo "CLI Version: $(vmware-vra --version)"
echo "Platform: $(uname -a)"
echo "Python Version: $(python --version 2>&1)"

echo -e "\n=== Configuration ==="
vmware-vra config show

echo -e "\n=== Authentication Status ==="
vmware-vra auth status

echo -e "\n=== Network Connectivity ==="
ping -c 3 your-vra-server.com 2>/dev/null || echo "Ping failed"

echo -e "\n=== Environment Variables ==="
env | grep VRA_ || echo "No VRA_ environment variables set"

echo -e "\n=== Recent Errors (if log file exists) ==="
if [ -f debug.log ]; then
    tail -20 debug.log
else
    echo "No debug.log file found"
fi
```

### Common Error Patterns

| Error Pattern | Likely Cause | Quick Fix |
|---------------|--------------|-----------|
| `SSL: CERTIFICATE_VERIFY_FAILED` | SSL certificate issues | Set `verify_ssl false` temporarily |
| `401 Unauthorized` | Authentication expired | Run `vmware-vra auth refresh` |
| `403 Forbidden` | Insufficient permissions | Check user roles in vRA |
| `Connection timeout` | Network issues | Increase timeout or check connectivity |
| `JSON decode error` | Server returning HTML/error page | Check vRA server status |
| `No space left on device` | Disk full | Clean up or use different output directory |
| `Command not found` | CLI not installed properly | Reinstall CLI |

## Prevention Tips

### Regular Maintenance

```bash
#!/bin/bash
# vra-cli-maintenance.sh

# Test authentication
vmware-vra auth status

# Test basic connectivity
vmware-vra catalog list --first-page-only >/dev/null && echo "✓ API accessible" || echo "✗ API issues"

# Check disk space for exports
df -h . | grep -v "Avail" | awk '{if($5 > 80) print "⚠ Disk space low: "$5" used"}'

# Clean old exports
find ./exports -name "*.json" -mtime +7 -exec echo "Old export file: {}" \;
```

### Configuration Validation

```bash
#!/bin/bash
# validate-config.sh

echo "Validating vRA CLI configuration..."

# Check required config
CONFIG_ITEMS=("api_url" "tenant")
for item in "${CONFIG_ITEMS[@]}"; do
    VALUE=$(vmware-vra config show --format json 2>/dev/null | jq -r ".$item")
    if [ "$VALUE" = "null" ] || [ -z "$VALUE" ]; then
        echo "⚠ Missing required config: $item"
    else
        echo "✓ $item configured"
    fi
done

# Test authentication
if vmware-vra auth status | grep -q "Authenticated"; then
    echo "✓ Authentication valid"
else
    echo "⚠ Authentication required"
fi

echo "Configuration validation complete."
```

This comprehensive troubleshooting guide should help resolve most issues encountered when using the VMware vRA CLI tool.
