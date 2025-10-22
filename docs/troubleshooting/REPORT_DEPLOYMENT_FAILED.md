# Report - Generate Monthly Detailed Usage Per Region - Troubleshooting

## 🔍 Issue Summary

**Catalog Item:** Report - Generate monthly detailed usage per region  
**Catalog ID:** `40c3a0a6-926a-306b-ab32-e5b5a5042a3e`  
**Problem:** All deployments are failing with `CREATE_FAILED` status

## 📊 Observed Failures

Recent failed deployments:
- `report-gene123` - CREATE_FAILED
- `report-generate2` - CREATE_FAILED
- `report-generate` - CREATE_FAILED
- `report-generate-monthly-detailed-usage-per-region-576032` - CREATE_FAILED

## 🔎 Root Cause Analysis

### 1. **Workflow Resource State: TAINTED**
The vRO workflow resource shows state `TAINTED` instead of `SUCCESSFUL`, indicating the workflow execution failed.

### 2. **Missing Required Input: email**
The schema includes an `email` field but deployments are not providing it:

**Schema Properties:**
```json
{
  "email": {
    "type": "string",
    "title": "email"
  },
  "month": {
    "type": "string",
    "title": "month"
  },
  "regionId": {
    "type": "string",
    "title": "regionId"
  },
  "tenantId": {
    "type": "string",
    "title": "tenantId"
  },
  "isInternal": {
    "type": "boolean",
    "title": "isInternal"
  }
}
```

**Actual Inputs Sent:**
```json
{
  "month": "2025-10",
  "regionId": "KPCFR-MOP",
  "tenantId": "Fabryk"
}
```

**Missing:** `email`, `isInternal`

## ✅ Solutions

### Solution 1: Add Missing Email Field

The workflow likely needs an email address to send the generated report. Add the email field when deploying:

#### Via Web UI:
1. Open the catalog item deployment form
2. Fill in all fields including **email**
3. Fill in **isInternal** (true/false)
4. Deploy

#### Via CLI:
```bash
vra catalog request 40c3a0a6-926a-306b-ab32-e5b5a5042a3e \
  --input email="your.email@company.com" \
  --input month="2025-10" \
  --input regionId="KPCFR-MOP" \
  --input tenantId="Fabryk" \
  --input isInternal=false \
  --name "report-monthly-oct-2025"
```

#### Via API:
```bash
curl -X POST "http://localhost:3000/catalog/40c3a0a6-926a-306b-ab32-e5b5a5042a3e/request" \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": "40c3a0a6-926a-306b-ab32-e5b5a5042a3e",
    "project_id": "5dbd84b1-d715-4c6d-b530-4db83f68708b",
    "name": "report-monthly-oct-2025",
    "reason": "Generate monthly report",
    "inputs": {
      "email": "your.email@company.com",
      "month": "2025-10",
      "regionId": "KPCFR-MOP",
      "tenantId": "Fabryk",
      "isInternal": false
    }
  }'
```

### Solution 2: Fix Schema to Mark Email as Required

If email is mandatory for the workflow, update the schema to mark it as required:

```json
{
  "schema": {
    "type": "object",
    "properties": { ... },
    "required": ["email", "month", "regionId", "tenantId"]
  }
}
```

This would be done in vRA/vRO workflow definition.

### Solution 3: Check vRO Workflow Logs

The workflow itself might be failing due to other reasons. Check vRO workflow execution logs:

1. Open vRO UI
2. Navigate to Workflow Runs
3. Find execution ID: `26d6834c-9d80-4751-b3fb-55e3b1896efd`
4. Check logs for detailed error messages

Common vRO workflow failures:
- Missing permissions to send email
- Invalid email server configuration
- Missing data in specified region
- Date format issues with month parameter

## 🔧 Verification Steps

### 1. Check Deployment Status
```bash
curl "http://localhost:3000/deployments/DEPLOYMENT_ID" | jq '.deployment.status'
```

### 2. Check Resource State
```bash
curl "http://localhost:3000/deployments/DEPLOYMENT_ID/resources" | jq '.resources[] | {name, type, state}'
```

### 3. Expected Success States
- Deployment status: `CREATE_SUCCESSFUL`
- Workflow resource state: `SUCCESSFUL` or `ACTIVE`

## 📋 Checklist for Future Deployments

Before deploying this catalog item:
- [ ] Email address provided and valid
- [ ] Month format correct (YYYY-MM)
- [ ] RegionId exists and is valid
- [ ] TenantId exists and is valid
- [ ] isInternal flag set (true/false)
- [ ] Email server accessible from vRO
- [ ] User has permissions to generate reports

## 🎯 Quick Test

Try a minimal deployment with all required fields:

```bash
vra catalog request 40c3a0a6-926a-306b-ab32-e5b5a5042a3e \
  --input email="test@example.com" \
  --input month="$(date +%Y-%m)" \
  --input regionId="KPCFR-MOP" \
  --input tenantId="Fabryk" \
  --input isInternal=false \
  --name "report-test-$(date +%s)"
```

Monitor the deployment:
```bash
vra deployment get DEPLOYMENT_ID --watch
```

## 📞 Support

If the issue persists after adding all required fields:
1. Check vRO workflow logs for detailed errors
2. Verify email server configuration in vRO
3. Confirm user permissions for report generation
4. Check that the region and tenant have data for the specified month

## 🔗 Related Documentation

- vRO Workflow Troubleshooting
- Email Configuration in vRO
- vRA Deployment Status Guide
- Report Generation Best Practices
