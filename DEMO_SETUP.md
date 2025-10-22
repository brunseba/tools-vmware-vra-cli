# VMware vRA CLI - Demo Setup Guide

## 🎯 Testing the Application

This guide shows how to test the VMware vRA CLI application with mock data for development and demonstration purposes.

## 🔐 vRA Credentials

The application is configured to connect to your real VMware vRA instance. Use your actual vRA credentials to authenticate.

**Note**: The application no longer uses mock/demo data. All data comes from your live vRA environment.

## 🚀 Quick Start

### 1. Start the Application
```bash
cd /Users/brun_s/sandbox/tools-vmware-vra-cli
docker-compose up -d
```

### 2. Access the Frontend
Open http://localhost:5173 in your browser

### 3. Login with Your vRA Credentials
- **URL**: Your vRA server URL (e.g., `https://vra.yourcompany.com`)
- **Username**: Your vRA username
- **Password**: Your vRA password
- **Tenant**: Your vRA tenant (e.g., `vsphere.local`)
- **Domain**: Your authentication domain (if applicable)

## 🧪 API Testing

### Authentication
```bash
# Login with your vRA credentials
curl -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your-vra-username",
    "password": "your-vra-password",
    "url": "https://vra.yourcompany.com",
    "tenant": "vsphere.local",
    "domain": "your-domain"
  }'

# Check authentication status
curl http://localhost:3000/auth/status
```

### Data Endpoints
```bash
# List projects
curl http://localhost:3000/projects

# List deployments
curl http://localhost:3000/deployments

# Get specific deployment
curl http://localhost:3000/deployments/demo-deployment-1

# Get deployment resources
curl http://localhost:3000/deployments/demo-deployment-1/resources

# Logout
curl -X POST http://localhost:3000/auth/logout
```

## 📊 Live Data

The application now displays live data from your vRA environment:

### Projects
All projects from your vRA instance will be displayed

### Deployments
All active and historical deployments from your vRA environment

### Catalog Items
All catalog items available in your vRA service catalog

## 🔧 Production Configuration

The application is configured for production use with your real vRA instance:

```yaml
# docker-compose.yml
environment:
  - VRA_DEV_MODE=false  # Production mode - connects to real vRA
```

### Production Mode Features

| Feature | Status |
|---------|--------|
| Authentication | Real vRA server |
| Data Source | Live vRA API |
| Network Calls | Real HTTP calls to vRA |
| SSL Verification | Configured per vRA setup |
| Projects | Live from vRA |
| Deployments | Live from vRA |
| Catalog Items | Live from vRA |
| Analytics | Real-time metrics |

## 🎭 Frontend Testing

### Login Flow
1. Navigate to http://localhost:5173
2. You'll be redirected to `/login` if not authenticated
3. Enter demo credentials and click "Sign In"
4. You'll be redirected to the dashboard with live data

### Available Pages
- **Dashboard** (`/dashboard`) - Overview and statistics
- **Catalog** (`/catalog`) - Browse available catalog items
- **Deployments** (`/deployments`) - View and manage deployments
- **Reports** (`/reports`) - Analytics and reporting
- **Settings** (`/settings`) - Application settings

## 🔍 Troubleshooting

### Backend Not Starting
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

### Authentication Issues
```bash
# Verify development mode is enabled
docker-compose exec backend env | grep VRA_DEV_MODE

# Should output: VRA_DEV_MODE=true
```

### Frontend Not Loading
```bash
# Check frontend status
docker-compose logs frontend

# Verify port access
curl -I http://localhost:5173
```

## 📝 Production Setup

To use with a real vRA server:

1. Set `VRA_DEV_MODE=false` in docker-compose.yml
2. Provide real vRA server URL and credentials
3. Ensure network connectivity to vRA server
4. Configure SSL certificates if required

```bash
# Example production login
curl -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your-vra-username",
    "password": "your-vra-password", 
    "url": "https://your-vra-server.domain.com",
    "tenant": "your-tenant",
    "domain": "your-domain"
  }'
```

## 🎉 What's Working

✅ **Authentication System**
- Demo login/logout flow
- Token management
- Session persistence

✅ **Core API Endpoints**
- Projects listing and details
- Deployments CRUD operations
- Resource management
- Status monitoring

✅ **Frontend Application**
- React-based UI with Material-UI
- Authentication guards
- Responsive design
- Real-time data updates

✅ **Development Tools**
- Docker containerization
- Hot reload for development
- Comprehensive logging
- Mock data system

## 🔗 Next Steps

1. **Customize Mock Data**: Edit `/src/vmware_vra_cli/rest_server/utils.py` to add your own test data
2. **Extend API**: Add more endpoints in `/src/vmware_vra_cli/rest_server/routers/`
3. **Frontend Enhancement**: Modify React components in `/frontend/src/`
4. **Production Deploy**: Configure with real vRA credentials and deploy