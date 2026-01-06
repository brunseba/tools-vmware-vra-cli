# REST API Integration Examples

This guide provides practical examples and patterns for integrating the VMware vRA REST API into your applications.

## Basic Examples

### Python with requests

```python
import requests
import json

class VRAClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.authenticated = False
    
    def authenticate(self, username, password, url, tenant=None):
        """Authenticate with vRA"""
        payload = {
            "username": username,
            "password": password,
            "url": url
        }
        if tenant:
            payload["tenant"] = tenant
            
        response = self.session.post(f"{self.base_url}/auth/login", json=payload)
        response.raise_for_status()
        
        result = response.json()
        self.authenticated = result.get("success", False)
        return result
    
    def list_catalog_items(self, project_id=None, page_size=100):
        """List available catalog items"""
        params = {"page_size": page_size}
        if project_id:
            params["project_id"] = project_id
            
        response = self.session.get(f"{self.base_url}/catalog/items", params=params)
        response.raise_for_status()
        return response.json()
    
    def request_deployment(self, catalog_item_id, project_id, name, description=None, inputs=None):
        """Request a new deployment"""
        payload = {
            "catalog_item_id": catalog_item_id,
            "project_id": project_id,
            "name": name
        }
        if description:
            payload["description"] = description
        if inputs:
            payload["inputs"] = inputs
            
        response = self.session.post(
            f"{self.base_url}/catalog/items/{catalog_item_id}/request",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_deployment_status(self, deployment_id):
        """Get deployment status"""
        response = self.session.get(f"{self.base_url}/deployments/{deployment_id}")
        response.raise_for_status()
        return response.json()
    
    def generate_activity_report(self, days_back=30, group_by="week"):
        """Generate activity timeline report"""
        params = {"days_back": days_back, "group_by": group_by}
        response = self.session.get(f"{self.base_url}/reports/activity-timeline", params=params)
        response.raise_for_status()
        return response.json()

# Usage example
def main():
    client = VRAClient()
    
    # Authenticate
    auth_result = client.authenticate(
        username="admin@corp.local",
        password="password",
        url="https://vra.company.com",
        tenant="corp.local"
    )
    
    if auth_result["success"]:
        print("✅ Authentication successful")
        
        # List catalog items
        items = client.list_catalog_items(project_id="dev-project")
        print(f"Found {len(items['items'])} catalog items")
        
        # Request deployment
        if items['items']:
            deployment = client.request_deployment(
                catalog_item_id=items['items'][0]['id'],
                project_id="dev-project",
                name="api-test-vm",
                description="VM created via REST API"
            )
            print(f"Deployment requested: {deployment['deployment_id']}")
            
        # Generate report
        report = client.generate_activity_report(days_back=7)
        print(f"Activity report: {report['timeline_data']['summary']['total_deployments']} deployments")

if __name__ == "__main__":
    main()
```

### JavaScript/Node.js with axios

```javascript
const axios = require('axios');

class VRAClient {
    constructor(baseURL = 'http://localhost:8000') {
        this.client = axios.create({
            baseURL: baseURL,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        // Add response interceptor for error handling
        this.client.interceptors.response.use(
            response => response,
            error => {
                console.error('API Error:', error.response?.data || error.message);
                throw error;
            }
        );
    }
    
    async authenticate(username, password, url, tenant = null) {
        try {
            const payload = { username, password, url };
            if (tenant) payload.tenant = tenant;
            
            const response = await this.client.post('/auth/login', payload);
            return response.data;
        } catch (error) {
            throw new Error(`Authentication failed: ${error.message}`);
        }
    }
    
    async listCatalogItems(projectId = null, pageSize = 100) {
        try {
            const params = { page_size: pageSize };
            if (projectId) params.project_id = projectId;
            
            const response = await this.client.get('/catalog/items', { params });
            return response.data;
        } catch (error) {
            throw new Error(`Failed to list catalog items: ${error.message}`);
        }
    }
    
    async requestDeployment(catalogItemId, projectId, name, description = null, inputs = null) {
        try {
            const payload = {
                catalog_item_id: catalogItemId,
                project_id: projectId,
                name: name
            };
            if (description) payload.description = description;
            if (inputs) payload.inputs = inputs;
            
            const response = await this.client.post(
                `/catalog/items/${catalogItemId}/request`,
                payload
            );
            return response.data;
        } catch (error) {
            throw new Error(`Failed to request deployment: ${error.message}`);
        }
    }
    
    async getDeploymentStatus(deploymentId) {
        try {
            const response = await this.client.get(`/deployments/${deploymentId}`);
            return response.data;
        } catch (error) {
            throw new Error(`Failed to get deployment status: ${error.message}`);
        }
    }
    
    async generateActivityReport(daysBack = 30, groupBy = 'week') {
        try {
            const params = { days_back: daysBack, group_by: groupBy };
            const response = await this.client.get('/reports/activity-timeline', { params });
            return response.data;
        } catch (error) {
            throw new Error(`Failed to generate report: ${error.message}`);
        }
    }
}

// Usage example
async function main() {
    const client = new VRAClient();
    
    try {
        // Authenticate
        const authResult = await client.authenticate(
            'admin@corp.local',
            'password',
            'https://vra.company.com',
            'corp.local'
        );
        
        if (authResult.success) {
            console.log('✅ Authentication successful');
            
            // List catalog items
            const items = await client.listCatalogItems('dev-project');
            console.log(`Found ${items.items.length} catalog items`);
            
            // Request deployment if items exist
            if (items.items.length > 0) {
                const deployment = await client.requestDeployment(
                    items.items[0].id,
                    'dev-project',
                    'js-api-test-vm',
                    'VM created via JavaScript REST API'
                );
                console.log(`Deployment requested: ${deployment.deployment_id}`);
                
                // Monitor deployment status
                const status = await client.getDeploymentStatus(deployment.deployment_id);
                console.log(`Deployment status: ${status.deployment.status}`);
            }
            
            // Generate activity report
            const report = await client.generateActivityReport(7, 'day');
            console.log(`Activity report: ${report.timeline_data.summary.total_deployments} deployments`);
        }
    } catch (error) {
        console.error('Error:', error.message);
    }
}

// Run example
main().catch(console.error);
```

### Go with net/http

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io/ioutil"
    "net/http"
    "time"
)

type VRAClient struct {
    BaseURL    string
    HTTPClient *http.Client
}

type AuthRequest struct {
    Username string `json:"username"`
    Password string `json:"password"`
    URL      string `json:"url"`
    Tenant   string `json:"tenant,omitempty"`
}

type AuthResponse struct {
    Success     bool   `json:"success"`
    Message     string `json:"message"`
    TokenStored bool   `json:"token_stored"`
    ExpiresAt   string `json:"expires_at"`
}

type CatalogItemsResponse struct {
    Success    bool          `json:"success"`
    Items      []CatalogItem `json:"items"`
    TotalCount int           `json:"total_count"`
}

type CatalogItem struct {
    ID          string `json:"id"`
    Name        string `json:"name"`
    Type        string `json:"type"`
    Status      string `json:"status"`
    Version     string `json:"version"`
    Description string `json:"description"`
}

type DeploymentRequest struct {
    CatalogItemID string                 `json:"catalog_item_id"`
    ProjectID     string                 `json:"project_id"`
    Name          string                 `json:"name"`
    Description   string                 `json:"description,omitempty"`
    Inputs        map[string]interface{} `json:"inputs,omitempty"`
}

type DeploymentResponse struct {
    Success      bool   `json:"success"`
    Message      string `json:"message"`
    DeploymentID string `json:"deployment_id"`
    Status       string `json:"status"`
}

func NewVRAClient(baseURL string) *VRAClient {
    return &VRAClient{
        BaseURL: baseURL,
        HTTPClient: &http.Client{
            Timeout: 30 * time.Second,
        },
    }
}

func (c *VRAClient) doRequest(method, endpoint string, body interface{}) (*http.Response, error) {
    var reqBody []byte
    var err error
    
    if body != nil {
        reqBody, err = json.Marshal(body)
        if err != nil {
            return nil, fmt.Errorf("failed to marshal request body: %w", err)
        }
    }
    
    req, err := http.NewRequest(method, c.BaseURL+endpoint, bytes.NewBuffer(reqBody))
    if err != nil {
        return nil, fmt.Errorf("failed to create request: %w", err)
    }
    
    req.Header.Set("Content-Type", "application/json")
    
    resp, err := c.HTTPClient.Do(req)
    if err != nil {
        return nil, fmt.Errorf("request failed: %w", err)
    }
    
    return resp, nil
}

func (c *VRAClient) Authenticate(username, password, url, tenant string) (*AuthResponse, error) {
    authReq := AuthRequest{
        Username: username,
        Password: password,
        URL:      url,
        Tenant:   tenant,
    }
    
    resp, err := c.doRequest("POST", "/auth/login", authReq)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    
    if resp.StatusCode != http.StatusOK {
        return nil, fmt.Errorf("authentication failed with status: %d", resp.StatusCode)
    }
    
    var authResp AuthResponse
    if err := json.NewDecoder(resp.Body).Decode(&authResp); err != nil {
        return nil, fmt.Errorf("failed to decode auth response: %w", err)
    }
    
    return &authResp, nil
}

func (c *VRAClient) ListCatalogItems(projectID string, pageSize int) (*CatalogItemsResponse, error) {
    endpoint := fmt.Sprintf("/catalog/items?page_size=%d", pageSize)
    if projectID != "" {
        endpoint += "&project_id=" + projectID
    }
    
    resp, err := c.doRequest("GET", endpoint, nil)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    
    if resp.StatusCode != http.StatusOK {
        return nil, fmt.Errorf("list catalog items failed with status: %d", resp.StatusCode)
    }
    
    var itemsResp CatalogItemsResponse
    if err := json.NewDecoder(resp.Body).Decode(&itemsResp); err != nil {
        return nil, fmt.Errorf("failed to decode catalog items response: %w", err)
    }
    
    return &itemsResp, nil
}

func (c *VRAClient) RequestDeployment(catalogItemID, projectID, name, description string, inputs map[string]interface{}) (*DeploymentResponse, error) {
    deployReq := DeploymentRequest{
        CatalogItemID: catalogItemID,
        ProjectID:     projectID,
        Name:          name,
        Description:   description,
        Inputs:        inputs,
    }
    
    endpoint := fmt.Sprintf("/catalog/items/%s/request", catalogItemID)
    resp, err := c.doRequest("POST", endpoint, deployReq)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    
    if resp.StatusCode != http.StatusOK {
        return nil, fmt.Errorf("deployment request failed with status: %d", resp.StatusCode)
    }
    
    var deployResp DeploymentResponse
    if err := json.NewDecoder(resp.Body).Decode(&deployResp); err != nil {
        return nil, fmt.Errorf("failed to decode deployment response: %w", err)
    }
    
    return &deployResp, nil
}

func main() {
    client := NewVRAClient("http://localhost:8000")
    
    // Authenticate
    authResp, err := client.Authenticate(
        "admin@corp.local",
        "password",
        "https://vra.company.com",
        "corp.local",
    )
    if err != nil {
        fmt.Printf("Authentication failed: %v\n", err)
        return
    }
    
    if authResp.Success {
        fmt.Println("✅ Authentication successful")
        
        // List catalog items
        items, err := client.ListCatalogItems("dev-project", 10)
        if err != nil {
            fmt.Printf("Failed to list catalog items: %v\n", err)
            return
        }
        
        fmt.Printf("Found %d catalog items\n", len(items.Items))
        
        // Request deployment if items exist
        if len(items.Items) > 0 {
            deployment, err := client.RequestDeployment(
                items.Items[0].ID,
                "dev-project",
                "go-api-test-vm",
                "VM created via Go REST API",
                nil,
            )
            if err != nil {
                fmt.Printf("Failed to request deployment: %v\n", err)
                return
            }
            
            fmt.Printf("Deployment requested: %s\n", deployment.DeploymentID)
        }
    }
}
```

## Web Framework Examples

### Flask Web Application

```python
from flask import Flask, request, jsonify, render_template
import requests
import os

app = Flask(__name__)

class VRAService:
    def __init__(self):
        self.base_url = os.getenv('VRA_API_URL', 'http://localhost:8000')
        self.session = requests.Session()
    
    def authenticate(self, username, password, vra_url, tenant=None):
        payload = {
            'username': username,
            'password': password,
            'url': vra_url
        }
        if tenant:
            payload['tenant'] = tenant
            
        response = self.session.post(f'{self.base_url}/auth/login', json=payload)
        return response.json()
    
    def list_catalog_items(self, project_id=None):
        params = {}
        if project_id:
            params['project_id'] = project_id
            
        response = self.session.get(f'{self.base_url}/catalog/items', params=params)
        return response.json()
    
    def request_deployment(self, catalog_item_id, project_id, name, description=None):
        payload = {
            'catalog_item_id': catalog_item_id,
            'project_id': project_id,
            'name': name
        }
        if description:
            payload['description'] = description
            
        response = self.session.post(
            f'{self.base_url}/catalog/items/{catalog_item_id}/request',
            json=payload
        )
        return response.json()

vra_service = VRAService()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    result = vra_service.authenticate(
        data['username'],
        data['password'],
        data['vra_url'],
        data.get('tenant')
    )
    return jsonify(result)

@app.route('/api/catalog/items')
def catalog_items():
    project_id = request.args.get('project_id')
    result = vra_service.list_catalog_items(project_id)
    return jsonify(result)

@app.route('/api/deployments', methods=['POST'])
def create_deployment():
    data = request.get_json()
    result = vra_service.request_deployment(
        data['catalog_item_id'],
        data['project_id'],
        data['name'],
        data.get('description')
    )
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
```

### FastAPI Web Application

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import requests
import os

app = FastAPI(title="vRA Web Interface")

class AuthRequest(BaseModel):
    username: str
    password: str
    vra_url: str
    tenant: Optional[str] = None

class DeploymentRequest(BaseModel):
    catalog_item_id: str
    project_id: str
    name: str
    description: Optional[str] = None

class VRAService:
    def __init__(self):
        self.base_url = os.getenv('VRA_API_URL', 'http://localhost:8000')
        self.session = requests.Session()
    
    async def authenticate(self, auth_req: AuthRequest):
        payload = auth_req.dict(exclude_none=True)
        response = self.session.post(f'{self.base_url}/auth/login', json=payload)
        response.raise_for_status()
        return response.json()
    
    async def list_catalog_items(self, project_id: Optional[str] = None):
        params = {}
        if project_id:
            params['project_id'] = project_id
            
        response = self.session.get(f'{self.base_url}/catalog/items', params=params)
        response.raise_for_status()
        return response.json()
    
    async def request_deployment(self, deploy_req: DeploymentRequest):
        payload = deploy_req.dict()
        response = self.session.post(
            f'{self.base_url}/catalog/items/{deploy_req.catalog_item_id}/request',
            json=payload
        )
        response.raise_for_status()
        return response.json()

# Dependency injection
def get_vra_service():
    return VRAService()

@app.post("/auth/login")
async def login(auth_req: AuthRequest, vra_service: VRAService = Depends(get_vra_service)):
    try:
        result = await vra_service.authenticate(auth_req)
        return result
    except requests.HTTPError as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

@app.get("/catalog/items")
async def list_catalog_items(
    project_id: Optional[str] = None,
    vra_service: VRAService = Depends(get_vra_service)
):
    try:
        result = await vra_service.list_catalog_items(project_id)
        return result
    except requests.HTTPError as e:
        raise HTTPException(status_code=400, detail="Failed to list catalog items")

@app.post("/deployments")
async def create_deployment(
    deploy_req: DeploymentRequest,
    vra_service: VRAService = Depends(get_vra_service)
):
    try:
        result = await vra_service.request_deployment(deploy_req)
        return result
    except requests.HTTPError as e:
        raise HTTPException(status_code=400, detail="Failed to create deployment")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "vRA Web Interface"}
```

### Express.js Web Application

```javascript
const express = require('express');
const axios = require('axios');
const cors = require('cors');

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// VRA Service
class VRAService {
    constructor() {
        this.baseURL = process.env.VRA_API_URL || 'http://localhost:8000';
        this.client = axios.create({
            baseURL: this.baseURL,
            timeout: 30000
        });
    }
    
    async authenticate(username, password, vraUrl, tenant = null) {
        const payload = { username, password, url: vraUrl };
        if (tenant) payload.tenant = tenant;
        
        const response = await this.client.post('/auth/login', payload);
        return response.data;
    }
    
    async listCatalogItems(projectId = null) {
        const params = {};
        if (projectId) params.project_id = projectId;
        
        const response = await this.client.get('/catalog/items', { params });
        return response.data;
    }
    
    async requestDeployment(catalogItemId, projectId, name, description = null) {
        const payload = {
            catalog_item_id: catalogItemId,
            project_id: projectId,
            name: name
        };
        if (description) payload.description = description;
        
        const response = await this.client.post(
            `/catalog/items/${catalogItemId}/request`,
            payload
        );
        return response.data;
    }
    
    async getDeploymentStatus(deploymentId) {
        const response = await this.client.get(`/deployments/${deploymentId}`);
        return response.data;
    }
}

const vraService = new VRAService();

// Routes
app.post('/api/auth/login', async (req, res) => {
    try {
        const { username, password, vraUrl, tenant } = req.body;
        const result = await vraService.authenticate(username, password, vraUrl, tenant);
        res.json(result);
    } catch (error) {
        res.status(401).json({ error: 'Authentication failed', details: error.message });
    }
});

app.get('/api/catalog/items', async (req, res) => {
    try {
        const { project_id } = req.query;
        const result = await vraService.listCatalogItems(project_id);
        res.json(result);
    } catch (error) {
        res.status(400).json({ error: 'Failed to list catalog items', details: error.message });
    }
});

app.post('/api/deployments', async (req, res) => {
    try {
        const { catalog_item_id, project_id, name, description } = req.body;
        const result = await vraService.requestDeployment(catalog_item_id, project_id, name, description);
        res.json(result);
    } catch (error) {
        res.status(400).json({ error: 'Failed to create deployment', details: error.message });
    }
});

app.get('/api/deployments/:id', async (req, res) => {
    try {
        const { id } = req.params;
        const result = await vraService.getDeploymentStatus(id);
        res.json(result);
    } catch (error) {
        res.status(404).json({ error: 'Deployment not found', details: error.message });
    }
});

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'healthy', service: 'vRA Web Interface' });
});

// Error handling middleware
app.use((error, req, res, next) => {
    console.error('Unhandled error:', error);
    res.status(500).json({ error: 'Internal server error' });
});

app.listen(port, () => {
    console.log(`vRA Web Interface running on port ${port}`);
});

module.exports = app;
```

## Frontend Examples

### React Component

```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const VRADashboard = () => {
    const [auth, setAuth] = useState(null);
    const [catalogItems, setCatalogItems] = useState([]);
    const [deployments, setDeployments] = useState([]);
    const [loading, setLoading] = useState(false);

    const api = axios.create({
        baseURL: process.env.REACT_APP_VRA_API_URL || 'http://localhost:8000'
    });

    const authenticate = async (credentials) => {
        try {
            setLoading(true);
            const response = await api.post('/auth/login', credentials);
            setAuth(response.data);
            return response.data;
        } catch (error) {
            console.error('Authentication failed:', error);
            throw error;
        } finally {
            setLoading(false);
        }
    };

    const loadCatalogItems = async (projectId = null) => {
        try {
            setLoading(true);
            const params = projectId ? { project_id: projectId } : {};
            const response = await api.get('/catalog/items', { params });
            setCatalogItems(response.data.items);
        } catch (error) {
            console.error('Failed to load catalog items:', error);
        } finally {
            setLoading(false);
        }
    };

    const loadDeployments = async (projectId = null) => {
        try {
            setLoading(true);
            const params = projectId ? { project_id: projectId } : {};
            const response = await api.get('/deployments', { params });
            setDeployments(response.data.deployments);
        } catch (error) {
            console.error('Failed to load deployments:', error);
        } finally {
            setLoading(false);
        }
    };

    const requestDeployment = async (catalogItemId, projectId, name) => {
        try {
            setLoading(true);
            const response = await api.post(`/catalog/items/${catalogItemId}/request`, {
                catalog_item_id: catalogItemId,
                project_id: projectId,
                name: name,
                description: `Deployment created from React dashboard`
            });
            
            // Reload deployments to show the new one
            await loadDeployments(projectId);
            return response.data;
        } catch (error) {
            console.error('Failed to request deployment:', error);
            throw error;
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (auth?.success) {
            loadCatalogItems();
            loadDeployments();
        }
    }, [auth]);

    if (!auth?.success) {
        return <LoginForm onLogin={authenticate} loading={loading} />;
    }

    return (
        <div className="vra-dashboard">
            <header>
                <h1>vRA Management Dashboard</h1>
                <button onClick={() => setAuth(null)}>Logout</button>
            </header>
            
            <div className="dashboard-content">
                <section>
                    <h2>Catalog Items</h2>
                    <div className="catalog-items">
                        {catalogItems.map(item => (
                            <CatalogItemCard
                                key={item.id}
                                item={item}
                                onDeploy={(name) => requestDeployment(item.id, 'default-project', name)}
                                loading={loading}
                            />
                        ))}
                    </div>
                </section>
                
                <section>
                    <h2>Recent Deployments</h2>
                    <div className="deployments">
                        {deployments.map(deployment => (
                            <DeploymentCard key={deployment.id} deployment={deployment} />
                        ))}
                    </div>
                </section>
            </div>
        </div>
    );
};

const LoginForm = ({ onLogin, loading }) => {
    const [credentials, setCredentials] = useState({
        username: '',
        password: '',
        vra_url: '',
        tenant: ''
    });

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await onLogin(credentials);
        } catch (error) {
            alert('Authentication failed');
        }
    };

    return (
        <form onSubmit={handleSubmit} className="login-form">
            <h2>Login to vRA</h2>
            <input
                type="text"
                placeholder="Username"
                value={credentials.username}
                onChange={(e) => setCredentials({...credentials, username: e.target.value})}
                required
            />
            <input
                type="password"
                placeholder="Password"
                value={credentials.password}
                onChange={(e) => setCredentials({...credentials, password: e.target.value})}
                required
            />
            <input
                type="url"
                placeholder="vRA URL"
                value={credentials.vra_url}
                onChange={(e) => setCredentials({...credentials, vra_url: e.target.value})}
                required
            />
            <input
                type="text"
                placeholder="Tenant (optional)"
                value={credentials.tenant}
                onChange={(e) => setCredentials({...credentials, tenant: e.target.value})}
            />
            <button type="submit" disabled={loading}>
                {loading ? 'Authenticating...' : 'Login'}
            </button>
        </form>
    );
};

const CatalogItemCard = ({ item, onDeploy, loading }) => {
    const [deploymentName, setDeploymentName] = useState('');

    const handleDeploy = () => {
        if (deploymentName.trim()) {
            onDeploy(deploymentName);
            setDeploymentName('');
        }
    };

    return (
        <div className="catalog-item-card">
            <h3>{item.name}</h3>
            <p>{item.description}</p>
            <div className="deploy-section">
                <input
                    type="text"
                    placeholder="Deployment name"
                    value={deploymentName}
                    onChange={(e) => setDeploymentName(e.target.value)}
                />
                <button onClick={handleDeploy} disabled={!deploymentName.trim() || loading}>
                    Deploy
                </button>
            </div>
        </div>
    );
};

const DeploymentCard = ({ deployment }) => {
    const getStatusColor = (status) => {
        switch (status) {
            case 'CREATE_SUCCESSFUL': return 'green';
            case 'CREATE_FAILED': return 'red';
            case 'CREATE_INPROGRESS': return 'orange';
            default: return 'gray';
        }
    };

    return (
        <div className="deployment-card">
            <h3>{deployment.name}</h3>
            <p>Status: <span style={{color: getStatusColor(deployment.status)}}>{deployment.status}</span></p>
            <p>Created: {new Date(deployment.created_at).toLocaleString()}</p>
            <p>Project: {deployment.project_name}</p>
        </div>
    );
};

export default VRADashboard;
```

### Vue.js Component

```vue
<template>
  <div class="vra-dashboard">
    <div v-if="!authenticated" class="login-section">
      <LoginForm @login="handleLogin" :loading="loading" />
    </div>
    
    <div v-else class="dashboard-content">
      <header>
        <h1>vRA Management Dashboard</h1>
        <button @click="logout" class="logout-btn">Logout</button>
      </header>
      
      <div class="main-content">
        <section class="catalog-section">
          <h2>Catalog Items</h2>
          <div class="catalog-grid">
            <CatalogItemCard
              v-for="item in catalogItems"
              :key="item.id"
              :item="item"
              @deploy="handleDeploy"
              :loading="loading"
            />
          </div>
        </section>
        
        <section class="deployments-section">
          <h2>Recent Deployments</h2>
          <div class="deployments-list">
            <DeploymentCard
              v-for="deployment in deployments"
              :key="deployment.id"
              :deployment="deployment"
            />
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import LoginForm from './LoginForm.vue';
import CatalogItemCard from './CatalogItemCard.vue';
import DeploymentCard from './DeploymentCard.vue';

export default {
  name: 'VRADashboard',
  components: {
    LoginForm,
    CatalogItemCard,
    DeploymentCard
  },
  data() {
    return {
      authenticated: false,
      loading: false,
      catalogItems: [],
      deployments: [],
      api: null
    };
  },
  created() {
    this.api = axios.create({
      baseURL: process.env.VUE_APP_VRA_API_URL || 'http://localhost:8000'
    });
  },
  methods: {
    async handleLogin(credentials) {
      try {
        this.loading = true;
        const response = await this.api.post('/auth/login', credentials);
        
        if (response.data.success) {
          this.authenticated = true;
          await this.loadData();
        }
      } catch (error) {
        console.error('Authentication failed:', error);
        this.$emit('error', 'Authentication failed');
      } finally {
        this.loading = false;
      }
    },
    
    async loadData() {
      try {
        this.loading = true;
        const [catalogResponse, deploymentsResponse] = await Promise.all([
          this.api.get('/catalog/items'),
          this.api.get('/deployments')
        ]);
        
        this.catalogItems = catalogResponse.data.items;
        this.deployments = deploymentsResponse.data.deployments;
      } catch (error) {
        console.error('Failed to load data:', error);
      } finally {
        this.loading = false;
      }
    },
    
    async handleDeploy(catalogItemId, name) {
      try {
        this.loading = true;
        await this.api.post(`/catalog/items/${catalogItemId}/request`, {
          catalog_item_id: catalogItemId,
          project_id: 'default-project',
          name: name,
          description: 'Deployment created from Vue dashboard'
        });
        
        // Reload deployments
        await this.loadData();
        this.$emit('success', 'Deployment requested successfully');
      } catch (error) {
        console.error('Failed to deploy:', error);
        this.$emit('error', 'Deployment failed');
      } finally {
        this.loading = false;
      }
    },
    
    logout() {
      this.authenticated = false;
      this.catalogItems = [];
      this.deployments = [];
    }
  }
};
</script>

<style scoped>
.vra-dashboard {
  padding: 20px;
}

.dashboard-content {
  max-width: 1200px;
  margin: 0 auto;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.catalog-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.deployments-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 15px;
}

.logout-btn {
  background: #dc3545;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
}

.logout-btn:hover {
  background: #c82333;
}
</style>
```

## CI/CD Integration Examples

### GitHub Actions Workflow

```yaml
name: vRA Deployment Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  VRA_API_URL: ${{ secrets.VRA_API_URL }}
  VRA_USERNAME: ${{ secrets.VRA_USERNAME }}
  VRA_PASSWORD: ${{ secrets.VRA_PASSWORD }}
  VRA_URL: ${{ secrets.VRA_URL }}
  VRA_TENANT: ${{ secrets.VRA_TENANT }}

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install requests python-dotenv
    
    - name: Deploy to staging
      run: |
        python .github/scripts/deploy_staging.py
        
  test-deployment:
    needs: deploy-staging
    runs-on: ubuntu-latest
    
    steps:
    - name: Test deployment
      run: |
        python .github/scripts/test_deployment.py
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    
    environment {
        VRA_API_URL = credentials('vra-api-url')
        VRA_CREDENTIALS = credentials('vra-credentials')
        VRA_URL = credentials('vra-url')
        VRA_TENANT = credentials('vra-tenant')
    }
    
    stages {
        stage('Authenticate') {
            steps {
                script {
                    sh '''
                        curl -X POST ${VRA_API_URL}/auth/login \
                          -H "Content-Type: application/json" \
                          -d "{
                            \"username\": \"${VRA_CREDENTIALS_USR}\",
                            \"password\": \"${VRA_CREDENTIALS_PSW}\",
                            \"url\": \"${VRA_URL}\",
                            \"tenant\": \"${VRA_TENANT}\"
                          }"
                    '''
                }
            }
        }
        
        stage('Deploy Infrastructure') {
            steps {
                script {
                    def deploymentResponse = sh(
                        script: '''
                            curl -X POST ${VRA_API_URL}/catalog/items/app-template/request \
                              -H "Content-Type: application/json" \
                              -d "{
                                \"catalog_item_id\": \"app-template\",
                                \"project_id\": \"staging-project\",
                                \"name\": \"app-staging-${BUILD_NUMBER}\",
                                \"description\": \"Staging deployment for build ${BUILD_NUMBER}\"
                              }"
                        ''',
                        returnStdout: true
                    ).trim()
                    
                    def deployment = readJSON text: deploymentResponse
                    env.DEPLOYMENT_ID = deployment.deployment_id
                }
            }
        }
        
        stage('Wait for Deployment') {
            steps {
                script {
                    timeout(time: 30, unit: 'MINUTES') {
                        waitUntil {
                            script {
                                def status = sh(
                                    script: "curl -s ${VRA_API_URL}/deployments/${DEPLOYMENT_ID}",
                                    returnStdout: true
                                ).trim()
                                def deployment = readJSON text: status
                                return deployment.deployment.status == 'CREATE_SUCCESSFUL'
                            }
                        }
                    }
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                sh 'python tests/integration_tests.py'
            }
        }
    }
    
    post {
        always {
            script {
                if (env.DEPLOYMENT_ID) {
                    sh "curl -X DELETE ${VRA_API_URL}/deployments/${DEPLOYMENT_ID}"
                }
            }
        }
    }
}
```

## Error Handling Patterns

### Retry Logic

```python
import time
import requests
from functools import wraps

def retry_on_failure(max_retries=3, delay=1, backoff=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    retries += 1
                    if retries >= max_retries:
                        raise e
                    
                    wait_time = delay * (backoff ** (retries - 1))
                    print(f"Retry {retries}/{max_retries} after {wait_time}s...")
                    time.sleep(wait_time)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

class VRAClientWithRetry:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
    
    @retry_on_failure(max_retries=3, delay=2)
    def authenticate(self, username, password, url, tenant=None):
        payload = {
            "username": username,
            "password": password,
            "url": url
        }
        if tenant:
            payload["tenant"] = tenant
            
        response = self.session.post(f"{self.base_url}/auth/login", json=payload)
        response.raise_for_status()
        return response.json()
    
    @retry_on_failure(max_retries=2, delay=1)
    def list_catalog_items(self, project_id=None):
        params = {}
        if project_id:
            params["project_id"] = project_id
            
        response = self.session.get(f"{self.base_url}/catalog/items", params=params)
        response.raise_for_status()
        return response.json()
```

### Circuit Breaker Pattern

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open" 
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
            
            raise e

class ResilientVRAClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.circuit_breaker = CircuitBreaker()
    
    def authenticate(self, username, password, url, tenant=None):
        def _authenticate():
            payload = {
                "username": username,
                "password": password,
                "url": url
            }
            if tenant:
                payload["tenant"] = tenant
                
            response = self.session.post(f"{self.base_url}/auth/login", json=payload)
            response.raise_for_status()
            return response.json()
        
        return self.circuit_breaker.call(_authenticate)
```

These examples demonstrate various integration patterns and best practices for using the VMware vRA REST API in different environments and frameworks. Choose the patterns that best fit your specific use case and requirements.

---

For more information:
- [Authentication Configuration](authentication.md)
- [OpenAPI Documentation](openapi.md)
- [REST API Setup](setup.md)
- [Complete API Reference](../rest-api-comprehensive.md)