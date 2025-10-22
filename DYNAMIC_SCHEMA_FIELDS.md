# Dynamic Schema Fields - Implementation Complete ✅

## 📋 Overview

The catalog deployment form now supports **dynamic URL fetching** for schema properties that have `$data` fields. This allows dropdown values to be fetched dynamically from APIs based on user input.

## 🎯 What Was Implemented

### 1. **Schema Property Support**
Added support for two dynamic schema properties:
- **`$data`** - URL to fetch enum/dropdown values dynamically
- **`$dynamicDefault`** - URL to fetch default value dynamically

### 2. **Variable Substitution**
The system automatically substitutes variables in URLs:
```typescript
// URL template with variables
"$data": "/data/vro-actions/api/getList?regionId={{regionId}}&projectId={{projectId}}"

// After substitution (when regionId="MOP" and projectId="abc123")
"/data/vro-actions/api/getList?regionId=MOP&projectId=abc123"
```

### 3. **Dependency Resolution**
- Fields are aware of their dependencies
- Waits for dependent fields to have values before fetching
- Automatically refetches when dependency values change

### 4. **Loading States**
- Shows loading spinner while fetching values
- Disables field during loading
- Displays "No options available" when fetch returns empty
- Shows "(Waiting for dependent fields)" when dependencies not resolved

## 🔧 Technical Implementation

### File Modified
`frontend/src/components/catalog/SchemaForm.tsx`

### Key Changes

#### 1. **Added State Management**
```typescript
const [dynamicEnums, setDynamicEnums] = useState<Record<string, string[]>>({})
const [loadingFields, setLoadingFields] = useState<Set<string>>(new Set())
```

#### 2. **Variable Substitution Function**
```typescript
const substituteVariables = (template: string, values: Record<string, any>): string => {
  return template.replace(/\{\{(\w+)\}\}/g, (_, varName) => {
    return values[varName] !== undefined ? String(values[varName]) : ''
  })
}
```

#### 3. **Dynamic Fetch Function**
```typescript
const fetchDynamicEnum = async (fieldName: string, url: string) => {
  // Substitute variables
  const resolvedUrl = substituteVariables(url, formData)
  
  // Check if all variables resolved
  if (resolvedUrl.includes('{{')) return
  
  // Fetch from API
  const response = await apiClient.get(resolvedUrl)
  
  // Extract values from response
  let values: string[] = []
  if (Array.isArray(response.data)) {
    values = response.data
  } else if (response.data.values) {
    values = response.data.values
  } else if (response.data.data) {
    values = response.data.data
  }
  
  // Update state
  setDynamicEnums(prev => ({ ...prev, [fieldName]: values }))
}
```

#### 4. **Auto-Fetch on Dependencies Change**
```typescript
useEffect(() => {
  formFields.forEach(field => {
    if (field.$data) {
      fetchDynamicEnum(field.name, field.$data)
    }
  })
}, [formData, formFields])
```

## 📊 Example Schema

### Before (Static Enum)
```json
{
  "regionId": {
    "type": "string",
    "title": "Region",
    "enum": ["MOP", "PAR", "LON"]
  }
}
```

### After (Dynamic Enum)
```json
{
  "regionId": {
    "type": "string",
    "title": "Region",
    "enum": ["MOP"],
    "default": ""
  },
  "ruleName": {
    "type": "string",
    "title": "Rule Name",
    "$data": "/data/vro-actions/fr.kyndryl.library/getKPCListOfIds?regionId={{regionId}}&type=asgRule&projectId={{projectId}}"
  }
}
```

## 🔄 How It Works

### Flow Diagram
```
1. User opens deployment form
   ↓
2. Schema parsed, fields with $data detected
   ↓
3. Initial fields without dependencies rendered
   ↓
4. User fills in "regionId" = "MOP"
   ↓
5. System detects change in formData
   ↓
6. Substitutes {{regionId}} → "MOP" in dependent field URLs
   ↓
7. Checks if all variables resolved (no {{}} left)
   ↓
8. Makes API call to fetch values
   ↓
9. Shows loading spinner on dependent field
   ↓
10. Receives response: ["rule-1", "rule-2", "rule-3"]
    ↓
11. Populates dropdown with fetched values
    ↓
12. User can now select from dynamic list
```

## 🎨 UI Features

### Visual Indicators
- **Loading Spinner** - Shown in field while fetching
- **Disabled State** - Field disabled during fetch
- **Empty State** - "No options available" when fetch returns empty
- **Helper Text** - "(Waiting for dependent fields)" when dependencies not met

### User Experience
- **Automatic** - No manual refresh needed
- **Real-time** - Updates as dependencies change
- **Responsive** - Shows loading states appropriately
- **Informative** - Clear feedback on field status

## 🧪 Testing

### Test Scenario 1: Simple Dependency
```json
{
  "region": {
    "type": "string",
    "enum": ["US", "EU"]
  },
  "datacenter": {
    "type": "string",
    "$data": "/api/datacenters?region={{region}}"
  }
}
```

**Steps:**
1. Select region "US"
2. Datacenter field automatically fetches from `/api/datacenters?region=US`
3. Dropdown populates with US datacenters
4. Change region to "EU"
5. Datacenter field refetches from `/api/datacenters?region=EU`
6. Dropdown updates with EU datacenters

### Test Scenario 2: Chained Dependencies
```json
{
  "project": { "type": "string", "enum": ["proj1"] },
  "region": {
    "type": "string",
    "$data": "/api/regions?project={{project}}"
  },
  "subnet": {
    "type": "string",
    "$data": "/api/subnets?project={{project}}&region={{region}}"
  }
}
```

**Steps:**
1. Select project "proj1"
2. Region field fetches and populates
3. Subnet field shows "(Waiting for dependent fields)"
4. Select region "us-east"
5. Subnet field fetches with both project and region
6. Dropdown populates with matching subnets

## 📝 Response Format Support

The implementation supports multiple response formats:

### Format 1: Direct Array
```json
["option1", "option2", "option3"]
```

### Format 2: Nested in 'values'
```json
{
  "values": ["option1", "option2", "option3"]
}
```

### Format 3: Nested in 'data'
```json
{
  "data": ["option1", "option2", "option3"]
}
```

## ⚠️ Error Handling

### Cases Handled
1. **Network Errors** - Logged to console, field remains empty
2. **Invalid Response** - Logged to console, field shows "No options available"
3. **Unresolved Variables** - Fetch skipped, field shows helper text
4. **Empty Results** - Field shows "No options available"

### Console Logging
- Skipped fetches due to unresolved variables
- Failed fetch attempts with error details
- Helps with debugging in development

## 🚀 Benefits

### For Users
✅ **Dynamic Content** - Dropdowns populated with real-time data
✅ **Contextual Options** - Values filtered based on other selections
✅ **Better UX** - Clear feedback on field status
✅ **Reduced Errors** - Only valid options shown

### For Developers
✅ **Flexible Schemas** - Support complex dependency chains
✅ **Easy Integration** - Works with existing vRA APIs
✅ **Type Safe** - Full TypeScript support
✅ **Maintainable** - Clean separation of concerns

## 🎯 Use Cases

### 1. **Region/Datacenter Selection**
Select region → Datacenters filtered by region

### 2. **Network Configuration**
Select project → VPCs filtered by project
Select VPC → Subnets filtered by VPC

### 3. **Firewall Rules**
Select source ASG → Destination ASGs filtered by compatibility
Select protocol → Ports filtered by protocol

### 4. **VM Deployment**
Select datacenter → Available templates in that datacenter
Select template → Compatible sizes for that template

## 📚 Schema Property Reference

### `$data` Property
```json
{
  "fieldName": {
    "type": "string",
    "title": "Field Title",
    "$data": "/api/endpoint?param1={{field1}}&param2={{field2}}"
  }
}
```

**Purpose:** Fetch dropdown values dynamically

**Requirements:**
- Must be a valid URL (absolute or relative)
- Can include `{{variableName}}` placeholders
- API must return array of strings or object with 'values'/'data' array

### `$dynamicDefault` Property
```json
{
  "fieldName": {
    "type": "string",
    "title": "Field Title",
    "$dynamicDefault": "/api/default?id={{otherId}}"
  }
}
```

**Purpose:** Fetch default value dynamically (future enhancement)

**Status:** Parsed but not yet fully implemented for default values

## 🎉 Summary

Dynamic schema field fetching is now **fully functional** in the catalog deployment form, enabling:

- ✅ Real-time dropdown value fetching
- ✅ Variable substitution in URLs
- ✅ Dependency chain resolution
- ✅ Loading states and user feedback
- ✅ Multiple response format support
- ✅ Error handling and console logging

Users can now deploy catalog items with complex, interdependent form fields that fetch their values dynamically from backend APIs! 🚀
