# VMware vRA CLI - Production Setup Guide

## 🎯 Overview

This application is now configured to connect to your **live VMware vRA instance**. All mock data has been removed, and the application will fetch real data from your vRA environment.

## 🔧 Configuration

### Environment Variables

The application is configured via `docker-compose.yml`:

```yaml
environment:
  - VRA_DEV_MODE=false           # Production mode (connects to real vRA)
  - VRA_API_URL=${VRA_API_URL}   # Your vRA server URL
  - LOG_LEVEL=${LOG_LEVEL:-info} # Logging level
```

### SSL Configuration

If your vRA instance uses self-signed certificates, you may need to configure SSL verification in the application settings or disable SSL verification (not recommended for production).

## 🚀 Quick Start

### 1. Start the Application

```bash
cd /Users/brun_s/sandbox/tools-vmware-vra-cli
docker-compose up -d
```

### 2. Access the Web Interface

Open your browser and navigate to:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:3000

### 3. Login with vRA Credentials

Use your actual VMware vRA credentials:

| Field | Example | Description |
|-------|---------|-------------|
| **URL** | `https://vra.company.com` | Your vRA server URL |
| **Username** | `admin@vsphere.local` | Your vRA username |
| **Password** | `********` | Your vRA password |
| **Tenant** | `vsphere.local` | Your vRA tenant |
| **Domain** | `vsphere.local` | Authentication domain (optional) |

## 📊 Available Features

### Dashboard
- **Real-time Statistics**: Total deployments, active resources, success rates
- **Recent Activity**: Live activity feed from vRA
- **Resource Usage**: CPU, memory, and storage metrics
- **User Analytics**: User activity and deployment trends

### Catalog Browser
- **Browse Catalog Items**: All catalog items from your vRA service catalog
- **Search & Filter**: Find catalog items by name, description, or type
- **Request Deployment**: Deploy catalog items with custom configurations
- **Schema Viewer**: View input schemas for catalog items

### Deployments Manager
- **List Deployments**: View all deployments from your vRA environment
- **Filter & Search**: Filter by status, project, or search by name
- **Deployment Details**: View detailed information about each deployment
- **Resource Management**: View and manage deployment resources
- **Deployment Actions**: Start, stop, or delete deployments

### Reports & Analytics
- **Activity Timeline**: Historical view of deployment activities
- **Catalog Usage**: Usage statistics for catalog items
- **Resource Reports**: Detailed resource usage reports
- **Success Metrics**: Deployment success rates and trends

### Settings
- **Default Project**: Configure your default project for filtering
- **Auto-refresh**: Enable automatic data refresh
- **Page Size**: Configure pagination settings
- **Theme**: Light/dark mode preferences

## 🔐 Authentication Flow

### 1. Initial Login
The application uses two-step authentication with vRA:

1. **Step 1**: Authenticate with CSP Gateway to get refresh token
   - Endpoint: `/csp/gateway/am/api/login?access_token`
   
2. **Step 2**: Exchange refresh token for IaaS access token
   - Endpoint: `/iaas/api/login`

### 2. Token Management
- **Access tokens** are stored securely in the system keyring
- **Refresh tokens** are used for automatic token renewal
- **Token refresh** happens automatically when access token expires

### 3. Session Persistence
- Authentication state is persisted in the frontend
- Tokens are securely stored on the backend
- Auto-logout on token expiration

## 🧪 Testing the API

### Authentication

```bash
# Login with vRA credentials
curl -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin@vsphere.local",
    "password": "your-password",
    "url": "https://vra.yourcompany.com",
    "tenant": "vsphere.local",
    "domain": "vsphere.local"
  }'

# Check authentication status
curl http://localhost:3000/auth/status

# Logout
curl -X POST http://localhost:3000/auth/logout
```

### Projects

```bash
# List all projects
curl http://localhost:3000/projects

# Get specific project
curl http://localhost:3000/projects/{project-id}
```

### Deployments

```bash
# List all deployments
curl http://localhost:3000/deployments

# Filter by project
curl "http://localhost:3000/deployments?project_id={project-id}"

# Filter by status
curl "http://localhost:3000/deployments?status=CREATE_SUCCESSFUL"

# Get deployment details
curl http://localhost:3000/deployments/{deployment-id}

# Get deployment resources
curl http://localhost:3000/deployments/{deployment-id}/resources

# Delete deployment
curl -X DELETE "http://localhost:3000/deployments/{deployment-id}?confirm=true"
```

### Catalog

```bash
# List catalog items
curl http://localhost:3000/catalog/items

# Filter by project
curl "http://localhost:3000/catalog/items?project_id={project-id}"

# Get catalog item details
curl http://localhost:3000/catalog/items/{item-id}

# Get catalog item schema
curl http://localhost:3000/catalog/items/{item-id}/schema

# Request catalog item
curl -X POST http://localhost:3000/catalog/items/{item-id}/request \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Deployment",
    "project_id": "project-id",
    "inputs": {
      "instanceSize": "medium",
      "environment": "production"
    }
  }'
```

### Analytics

```bash
# Get analytics statistics
curl "http://localhost:3000/analytics/stats?time_range=30d"

# Get activity timeline
curl "http://localhost:3000/analytics/timeline?limit=50"

# Get chart data
curl "http://localhost:3000/analytics/charts?time_range=7d"

# Get resource usage
curl http://localhost:3000/analytics/usage
```

## 🔍 Troubleshooting

### Connection Issues

**Problem**: Cannot connect to vRA server
```bash
# Check vRA server reachability
curl -k https://vra.yourcompany.com/health

# Check backend logs
docker-compose logs backend --tail=50

# Verify environment variables
docker-compose exec backend env | grep VRA
```

**Solution**: 
- Verify vRA server URL is correct
- Check network connectivity
- Ensure firewall allows connections
- Verify SSL certificates

### Authentication Failures

**Problem**: 401 Unauthorized errors
```bash
# Check authentication status
curl http://localhost:3000/auth/status

# View authentication logs
docker-compose logs backend | grep -i auth
```

**Solution**:
- Verify credentials are correct
- Check tenant and domain settings
- Ensure user has proper vRA permissions
- Re-authenticate if tokens expired

### Empty Data

**Problem**: Dashboard or pages show no data

**Solution**:
- Verify you're authenticated
- Check that you have deployments in vRA
- Verify project permissions
- Check backend logs for errors

### SSL Certificate Errors

**Problem**: SSL verification failures

**Solution**:
1. Use valid SSL certificates (recommended)
2. Import self-signed certificates into the system
3. Configure `verify_ssl: false` in config (not recommended for production)

## 📈 Performance Optimization

### Caching
- API responses are cached using Redis
- Cache duration configurable per endpoint
- Manual cache invalidation available

### Pagination
- All list endpoints support pagination
- Default page size: 100 items
- Configurable via query parameters

### Auto-refresh
- Configurable auto-refresh intervals
- Disabled by default for performance
- Can be enabled per page in settings

## 🔒 Security Best Practices

1. **Use HTTPS** in production environments
2. **Rotate credentials** regularly
3. **Limit API access** to authorized networks
4. **Enable audit logging** for compliance
5. **Use strong passwords** for vRA accounts
6. **Keep tokens secure** - never commit to git
7. **Regular updates** - keep dependencies updated

## 📝 Next Steps

1. **Configure Projects**: Set up your default project in settings
2. **Browse Catalog**: Explore available catalog items
3. **Deploy Services**: Request deployments from the catalog
4. **Monitor Deployments**: Track deployment status and resources
5. **Analyze Usage**: Review analytics and reports

## 🆘 Support

For issues or questions:
- Check logs: `docker-compose logs backend`
- Review documentation in `/docs`
- Check VMware vRA documentation
- Verify API connectivity with curl tests

## 🎉 Success Checklist

- ✅ Application running (docker-compose ps shows healthy containers)
- ✅ Can access frontend at http://localhost:5173
- ✅ Can access backend at http://localhost:3000
- ✅ Authentication successful with vRA credentials
- ✅ Projects are listed from vRA
- ✅ Deployments are visible
- ✅ Catalog items are loaded
- ✅ Dashboard shows real-time statistics
- ✅ Can request new deployments from catalog
