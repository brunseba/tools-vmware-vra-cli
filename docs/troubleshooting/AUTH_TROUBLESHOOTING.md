# Authentication Troubleshooting Guide

## ⚠️ Current Issue: 401 Unauthorized

The application is returning **401 Unauthorized** errors because it's now in **production mode** and attempting to authenticate with a real VMware vRA server.

## 🔍 What's Happening

1. **Production Mode Active**: `VRA_DEV_MODE=false`
2. **Mock Auth Disabled**: Demo credentials (demo/demo123) no longer work
3. **Real vRA Required**: The app is trying to connect to an actual vRA server
4. **Authentication Failing**: vRA server is rejecting the login attempts

## ✅ Solution: Use Real vRA Credentials

You need to provide **actual VMware vRA credentials** from your vRA instance.

### Required Information

| Field | What You Need | Example |
|-------|---------------|---------|
| **URL** | Your vRA server address | `https://vra-prod.company.com` |
| **Username** | Your vRA username | `admin@vsphere.local` or `john.doe@company.com` |
| **Password** | Your vRA password | `YourActualPassword123!` |
| **Tenant** | Your vRA tenant | `vsphere.local` |
| **Domain** | Authentication domain | `vsphere.local` or leave empty |

### How to Find Your vRA Details

1. **vRA Server URL**:
   - Ask your vRA administrator
   - Check your company's vRA documentation
   - Look at existing vRA bookmarks/links
   - Example: `https://vra.company.com` or `https://automation.company.com`

2. **Username**:
   - Usually in format: `username@domain`
   - Example: `admin@vsphere.local`
   - Or your corporate email: `john.doe@company.com`

3. **Tenant**:
   - Common values: `vsphere.local`, `company.local`
   - Ask your vRA administrator if unsure
   - May be same as your authentication domain

4. **Domain** (optional):
   - Authentication domain for your organization
   - Often same as tenant
   - Can be left empty if not required

## 🚀 Testing Authentication

### Step 1: Verify vRA Server is Accessible

```bash
# Check if vRA server is reachable
curl -k https://YOUR-VRA-SERVER.com/health

# Or check basic connectivity
ping YOUR-VRA-SERVER.com
```

### Step 2: Test Login via API

```bash
# Replace with YOUR actual credentials
curl -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "YOUR-USERNAME@vsphere.local",
    "password": "YOUR-ACTUAL-PASSWORD",
    "url": "https://YOUR-VRA-SERVER.com",
    "tenant": "vsphere.local",
    "domain": "vsphere.local"
  }'
```

**Successful response**:
```json
{
  "success": true,
  "message": "Authentication successful",
  "token_stored": true,
  "config_saved": true
}
```

**Failed response** (wrong credentials):
```json
{
  "detail": "Authentication failed: 401 Client Error: Unauthorized"
}
```

### Step 3: Login via Web UI

1. Open http://localhost:5173
2. Enter your **real vRA credentials**
3. Click "Show Advanced Options" if you need to specify tenant/domain
4. Click "Sign In"

## 🔄 Alternative: Enable Demo Mode (Temporary)

If you don't have vRA credentials right now and want to test the UI with mock data:

### Enable Development Mode

```bash
# Edit docker-compose.yml
# Change this line:
- VRA_DEV_MODE=false

# To this:
- VRA_DEV_MODE=true

# Restart backend
docker-compose restart backend
```

### Use Demo Credentials

With dev mode enabled, you can use:
- **Username**: `demo`
- **Password**: `demo123`
- **URL**: `https://demo.vra.example.com`
- **Tenant**: `demo-tenant`
- **Domain**: `demo.local`

## 🐛 Common Authentication Errors

### Error: "Connection refused" or "Failed to connect"

**Cause**: vRA server is not reachable

**Solution**:
- Verify vRA server URL is correct
- Check network connectivity
- Ensure firewall allows outbound connections
- Verify vRA server is online

### Error: "SSL certificate verify failed"

**Cause**: Self-signed or untrusted SSL certificate

**Solution**:
- Use a valid SSL certificate (recommended)
- Or configure SSL verification settings

### Error: "401 Unauthorized"

**Cause**: Invalid credentials or wrong authentication details

**Solution**:
- Double-check username and password
- Verify tenant name is correct
- Try authenticating via vRA web UI directly first
- Ensure your account is not locked
- Check if you have proper vRA permissions

### Error: "403 Forbidden"

**Cause**: User doesn't have required permissions

**Solution**:
- Contact vRA administrator
- Verify your account has access to vRA IaaS API
- Check user role assignments in vRA

## 📋 Verification Checklist

Before attempting login:
- [ ] I have access to a VMware vRA instance
- [ ] I know my vRA server URL
- [ ] I have a valid vRA username
- [ ] I have my vRA password
- [ ] I know my tenant name (or can ask admin)
- [ ] vRA server is accessible from my network
- [ ] My vRA account is active and not locked
- [ ] I have permissions to access vRA API

## 🆘 Still Having Issues?

### Check Backend Logs

```bash
# View real-time logs
docker-compose logs backend -f

# Search for authentication errors
docker-compose logs backend | grep -i "auth\|401\|error"
```

### Check Frontend Browser Console

1. Open http://localhost:5173
2. Open browser Developer Tools (F12)
3. Go to Console tab
4. Attempt to login
5. Look for error messages

### Verify Configuration

```bash
# Check development mode status
docker-compose exec backend env | grep VRA_DEV_MODE

# Should show:
# VRA_DEV_MODE=false (for production with real vRA)
# VRA_DEV_MODE=true (for demo mode with mock data)
```

## 📞 Contact Your vRA Administrator

If you need help with:
- vRA server URL
- Your username format
- Tenant information
- Authentication domain
- API access permissions
- Account activation

Contact your organization's VMware vRA administrator or infrastructure team.

## 🎯 Quick Resolution

**Option 1: Use Real vRA** (Production)
1. Get your vRA credentials from your admin
2. Login at http://localhost:5173 with real credentials
3. All data will come from your live vRA environment

**Option 2: Use Demo Mode** (Testing)
1. Set `VRA_DEV_MODE=true` in docker-compose.yml
2. Restart backend: `docker-compose restart backend`
3. Login with demo credentials (demo/demo123)
4. UI will show mock data for testing

Choose the option that fits your current needs!
