# Authentication Debugging Guide

## ✅ Verbose Logging Now Enabled

I've added comprehensive logging to help diagnose the authentication issue.

## 🔍 Step-by-Step Debugging

### Method 1: Automated Test Script (Recommended)

```bash
# Run the test script
./test_auth_webui.sh

# This will:
# 1. Check backend status
# 2. Show development mode setting
# 3. Monitor logs in real-time
# 4. Show all authentication-related messages
```

**What to do:**
1. Run the script: `./test_auth_webui.sh`
2. Open http://localhost:5173 in your browser
3. Try to login with your vRA credentials
4. Watch the terminal for detailed log messages
5. Press Ctrl+C when done

### Method 2: Manual Debugging

#### Step 1: Check Backend Logs

```bash
# View logs in real-time
docker-compose logs -f backend | grep -i "auth\|login\|401"
```

#### Step 2: Open Browser Console

1. Open http://localhost:5173
2. Open Browser DevTools (F12 or Cmd+Option+I)
3. Go to the **Console** tab
4. Try to login
5. Look for messages starting with "Auth Service:"

You should see:
```
Auth Service: Attempting login with: {username: "...", url: "...", ...}
Auth Service: Login response received: 200
```

Or if failed:
```
Auth Service: Login failed: 401 {...}
```

#### Step 3: Check Network Tab

1. In Browser DevTools, go to **Network** tab
2. Try to login
3. Look for the request to `/auth/login` or `/api/auth/login`
4. Click on it to see:
   - **Headers**: Request headers
   - **Payload**: What data was sent
   - **Response**: Server response

### What to Look For

#### In Backend Logs

You should see messages like:
```
INFO: Authentication attempt - URL: https://..., User: ..., Tenant: ..., Domain: ...
INFO: Development mode: false
INFO: Production mode - attempting real vRA authentication
INFO: Config loaded - verify_ssl: True
INFO: Creating VRAAuthenticator with URL: https://...
INFO: Calling authenticator.authenticate()
```

If successful:
```
INFO: Authentication successful - tokens received
```

If failed:
```
ERROR: Authentication failed - RequestException: ...
ERROR: Exception type: ...
ERROR: Traceback: ...
```

#### In Browser Console

Frontend sending:
```
Auth Service: Attempting login with: {
  username: "admin@vsphere.local",
  url: "https://vra.company.com",
  tenant: "vsphere.local",
  domain: "vsphere.local",
  passwordProvided: true
}
```

Backend response:
```
Auth Service: Login response received: 200
```

Or error:
```
Auth Service: Login failed: 401 {detail: "Authentication failed: ..."}
```

## 🐛 Common Issues & Solutions

### Issue 1: URL Mismatch

**Symptoms**: Backend logs show wrong URL
```
INFO: Creating VRAAuthenticator with URL: https://
```

**Cause**: Frontend sending incomplete URL

**Solution**: 
- Make sure URL in login form is complete (e.g., `https://vra.company.com`)
- Don't leave it as just `https://`

### Issue 2: Missing Credentials

**Symptoms**: 
```
ERROR: Authentication failed - RequestException: 401 Unauthorized
```

**Cause**: Wrong username/password or wrong format

**Solution**:
- Verify credentials work with CLI
- Check username format (usually `user@domain`)
- Try same credentials on vRA web UI first

### Issue 3: Connection Failed

**Symptoms**:
```
ERROR: Connection refused
ERROR: Name or service not known
```

**Cause**: Cannot reach vRA server

**Solution**:
- Verify vRA URL is accessible
- Test: `curl -k https://your-vra-server.com/health`
- Check network/firewall settings

### Issue 4: SSL Certificate Error

**Symptoms**:
```
ERROR: SSL certificate verify failed
```

**Cause**: Self-signed or untrusted certificate

**Solution**:
- Check verify_ssl setting in config
- May need to import certificate
- For testing: disable SSL verification (not recommended for production)

## 🧪 Test with CLI First

Verify your credentials work with the CLI:

```bash
# Test authentication with CLI
uv run vra login \
  --url https://your-vra-server.com \
  --username admin@vsphere.local \
  --password your-password

# List deployments to verify
uv run vra list deployments
```

If CLI works but web UI doesn't, it's a web UI specific issue.

## 📋 Information to Collect

When reporting the issue, please provide:

1. **Backend logs** during login attempt:
   ```bash
   docker-compose logs backend --tail=50 > backend_logs.txt
   ```

2. **Browser console** output:
   - Screenshot or copy/paste of console messages

3. **Network request details**:
   - From Browser DevTools → Network → /auth/login request
   - Request payload
   - Response status and body

4. **Configuration**:
   ```bash
   docker-compose exec backend env | grep VRA
   ```

5. **CLI test result**:
   - Does `vra login` work with same credentials?

## 🎯 Quick Diagnosis

Run all checks:

```bash
# 1. Check containers
docker-compose ps

# 2. Check dev mode
docker-compose exec backend env | grep VRA_DEV_MODE

# 3. Test backend health
curl http://localhost:3000/health

# 4. Test frontend
curl -I http://localhost:5173

# 5. Watch logs
./test_auth_webui.sh
```

Then try to login and observe the output.

## 📞 Next Steps

After running the debug steps:

1. **If you see the issue in logs**: Share the specific error message
2. **If CLI works but web UI doesn't**: We have a web UI specific issue
3. **If nothing appears in logs**: Request might not be reaching backend
4. **If SSL errors**: Certificate issue needs to be addressed

Run `./test_auth_webui.sh` and share the output for more specific guidance!
