# VMware vRA CLI - Quick Start

## ✅ Status: Production Mode Active

The application is configured to connect to your **real VMware vRA instance**.

**Mock data has been removed** - All data comes from your live vRA environment.

## 🚀 Access the Application

| Component | URL | Status |
|-----------|-----|--------|
| **Frontend UI** | http://localhost:5173 | ✅ Running |
| **Backend API** | http://localhost:3000 | ✅ Running |
| **Redis Cache** | localhost:6379 | ✅ Running |

## 🔐 Login

1. Open http://localhost:5173 in your browser
2. Enter your vRA credentials:
   - **URL**: Your vRA server (e.g., `https://vra.company.com`)
   - **Username**: Your vRA username (e.g., `admin@vsphere.local`)
   - **Password**: Your vRA password
   - **Tenant**: Your tenant (e.g., `vsphere.local`)
   - **Domain**: Your domain (optional)

## 📊 What You'll See

### Dashboard
- Real-time deployment statistics
- Active resources count
- Success rate metrics
- Recent activity feed

### Catalog
- All catalog items from your vRA service catalog
- Search and filter capabilities
- Deploy new services

### Deployments
- All your active and historical deployments
- Filter by project, status
- View deployment details and resources
- Manage deployment lifecycle

### Reports
- Analytics and metrics
- Resource usage reports
- Activity timelines

## ⚙️ Configuration

**Production Mode**: `VRA_DEV_MODE=false` ✅

To verify:
```bash
docker-compose exec backend env | grep VRA_DEV_MODE
# Output: VRA_DEV_MODE=false
```

## 🔄 Management Commands

```bash
# View logs
docker-compose logs backend -f
docker-compose logs frontend -f

# Restart services
docker-compose restart backend
docker-compose restart frontend

# Stop all services
docker-compose down

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

## 🆘 Troubleshooting

### Can't Login?
- Verify vRA server URL is correct and accessible
- Check your username/password
- Ensure tenant and domain are correct
- Check backend logs: `docker-compose logs backend --tail=50`

### No Data Showing?
- Verify you're successfully authenticated
- Check that you have deployments in your vRA instance
- Verify network connectivity to vRA server
- Check for errors in console: Browser DevTools → Console

### Application Not Loading?
```bash
# Check all containers are running
docker-compose ps

# Restart if needed
docker-compose restart

# Check logs for errors
docker-compose logs --tail=100
```

## 📖 Documentation

- **Production Setup**: See `PRODUCTION_SETUP.md` for detailed configuration
- **API Reference**: See `DEMO_SETUP.md` for API endpoint examples
- **Architecture**: See `/docs` folder for technical documentation

## 🎯 Next Steps

1. ✅ Login with your vRA credentials
2. ✅ Browse your catalog items
3. ✅ View your deployments
4. ✅ Deploy a new service from catalog
5. ✅ Monitor deployment status
6. ✅ Review analytics and reports

---

**Note**: This application connects to your **live vRA environment**. All actions (deployments, deletions, etc.) will affect your real vRA resources.
