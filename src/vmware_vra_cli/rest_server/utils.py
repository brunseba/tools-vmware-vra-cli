"""Utility functions for MCP server."""

import os
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from vmware_vra_cli.api.catalog import CatalogClient
from vmware_vra_cli.auth import TokenManager
from vmware_vra_cli.config import get_config


class MockCatalogClient:
    """Mock catalog client for development mode."""
    
    def __init__(self, base_url=None, token=None, verify_ssl=True, verbose=False):
        self.base_url = base_url
        self.token = token
        self.verify_ssl = verify_ssl
        self.verbose = verbose
        
    def list_deployments(self, project_id=None, fetch_all=True, status=None, page_size=100):
        """Mock deployments data with recent dates."""
        now = datetime.utcnow()
        
        mock_deployments = [
            {
                "id": "demo-deployment-1",
                "name": "Demo Web App",
                "projectId": "project-demo-1",
                "projectName": "Demo Project 1",
                "organizationId": "demo-org",
                "status": "CREATE_SUCCESSFUL",
                "blueprintId": "demo-blueprint-1",
                "blueprintName": "Web Application",
                "createdAt": (now - timedelta(days=5)).isoformat() + "Z",
                "updatedAt": (now - timedelta(days=5, minutes=-15)).isoformat() + "Z",
                "createdBy": "demo@example.com",
                "ownedBy": "demo@example.com",
                "resourceCount": 3
            },
            {
                "id": "demo-deployment-2",
                "name": "Demo Database",
                "projectId": "project-demo-2",
                "projectName": "Demo Project 2",
                "organizationId": "demo-org",
                "status": "CREATE_SUCCESSFUL",
                "blueprintId": "demo-blueprint-2",
                "blueprintName": "Database Server",
                "createdAt": (now - timedelta(days=10)).isoformat() + "Z",
                "updatedAt": (now - timedelta(days=10, minutes=-15)).isoformat() + "Z",
                "createdBy": "admin@example.com",
                "ownedBy": "admin@example.com",
                "resourceCount": 2
            },
            {
                "id": "demo-deployment-3",
                "name": "Demo API Gateway", 
                "projectId": "project-demo-1",
                "projectName": "Demo Project 1",
                "organizationId": "demo-org",
                "status": "UPDATE_SUCCESSFUL",
                "blueprintId": "demo-blueprint-3",
                "blueprintName": "API Gateway",
                "createdAt": (now - timedelta(days=2)).isoformat() + "Z",
                "updatedAt": (now - timedelta(days=2, hours=-2)).isoformat() + "Z",
                "createdBy": "demo@example.com",
                "ownedBy": "demo@example.com",
                "resourceCount": 1
            },
            {
                "id": "demo-deployment-4",
                "name": "Demo Failed Deploy",
                "projectId": "project-demo-2",
                "projectName": "Demo Project 2",
                "organizationId": "demo-org",
                "status": "CREATE_FAILED",
                "blueprintId": "demo-blueprint-4",
                "blueprintName": "Test Application",
                "createdAt": (now - timedelta(days=1)).isoformat() + "Z",
                "updatedAt": (now - timedelta(days=1, minutes=-5)).isoformat() + "Z",
                "createdBy": "test@example.com",
                "ownedBy": "test@example.com",
                "resourceCount": 0
            }
        ]
        
        # Filter by project_id if provided
        filtered_deployments = mock_deployments
        if project_id:
            filtered_deployments = [d for d in filtered_deployments if d["projectId"] == project_id]
        
        # Filter by status if provided
        if status:
            filtered_deployments = [d for d in filtered_deployments if d["status"] == status]
        
        # Apply page_size limit
        if not fetch_all and page_size:
            filtered_deployments = filtered_deployments[:page_size]
            
        return filtered_deployments
    
    def list_catalog_items(self, project_id=None):
        """Mock catalog items data."""
        mock_catalog_items = [
            {
                "id": "catalog-item-1",
                "name": "Ubuntu Virtual Machine",
                "description": "Deploy a standard Ubuntu 20.04 virtual machine",
                "type": "Cloud Template",
                "projectId": project_id or "project-demo-1",
                "iconId": "ubuntu-icon",
                "status": "RELEASED",
                "createdAt": "2024-01-10T08:00:00Z",
                "updatedAt": "2024-01-15T12:00:00Z",
                "requestCount": 25
            },
            {
                "id": "catalog-item-2", 
                "name": "Windows Server 2019",
                "description": "Deploy a Windows Server 2019 instance",
                "type": "Cloud Template",
                "projectId": project_id or "project-demo-2",
                "iconId": "windows-icon",
                "status": "RELEASED",
                "createdAt": "2024-01-12T10:30:00Z",
                "updatedAt": "2024-01-18T15:45:00Z",
                "requestCount": 18
            },
            {
                "id": "catalog-item-3",
                "name": "Docker Container Host",
                "description": "Deploy a Docker-ready host with container runtime",
                "type": "Cloud Template",
                "projectId": project_id or "project-demo-1",
                "iconId": "docker-icon",
                "status": "RELEASED",
                "createdAt": "2024-01-14T16:20:00Z",
                "updatedAt": "2024-01-19T09:10:00Z", 
                "requestCount": 12
            }
        ]
        
        return mock_catalog_items
    
    def get_catalog_item(self, item_id):
        """Mock get catalog item by ID."""
        catalog_items = self.list_catalog_items()
        for item in catalog_items:
            if item["id"] == item_id:
                # Create a mock object that supports dict() method
                class MockCatalogItem:
                    def __init__(self, data):
                        self._data = data
                        for k, v in data.items():
                            setattr(self, k, v)
                    
                    def dict(self):
                        return self._data
                
                return MockCatalogItem(item)
        return None
    
    def get_catalog_item_schema(self, item_id):
        """Mock get catalog item schema."""
        return {
            "type": "object",
            "properties": {
                "deploymentName": {
                    "type": "string",
                    "title": "Deployment Name",
                    "description": "Name for this deployment",
                    "default": f"demo-{item_id[:8]}"
                },
                "instanceSize": {
                    "type": "string",
                    "title": "Instance Size",
                    "enum": ["small", "medium", "large"],
                    "default": "medium"
                },
                "environment": {
                    "type": "string",
                    "title": "Environment",
                    "enum": ["development", "testing", "production"],
                    "default": "development"
                }
            },
            "required": ["deploymentName"]
        }
    
    def request_catalog_item(self, item_id, inputs_dict, project_id, reason=None):
        """Mock request catalog item."""
        deployment_id = f"deployment-{item_id[:8]}-{hash(str(inputs_dict)) % 1000:03d}"
        return {
            "deploymentId": deployment_id,
            "requestId": f"request-{deployment_id}",
            "message": "Mock deployment created successfully"
        }
    
    def get_deployment(self, deployment_id):
        """Mock get deployment by ID."""
        deployments = self.list_deployments()
        for deployment in deployments:
            if deployment["id"] == deployment_id:
                return deployment
        return None
    
    def delete_deployment(self, deployment_id):
        """Mock delete deployment."""
        return {"message": f"Deployment {deployment_id} deletion initiated", "requestId": "mock-request-123"}
    
    def get_deployment_resources(self, deployment_id):
        """Mock get deployment resources."""
        return [
            {
                "id": f"resource-{deployment_id}-1",
                "name": "web-server",
                "type": "Virtual Machine",
                "status": "RUNNING",
                "properties": {
                    "cpus": 2,
                    "memory": 4096,
                    "disk": 40,
                    "os": "Ubuntu 20.04"
                }
            },
            {
                "id": f"resource-{deployment_id}-2",
                "name": "load-balancer",
                "type": "Load Balancer",
                "status": "ACTIVE",
                "properties": {
                    "algorithm": "round-robin",
                    "protocol": "HTTP",
                    "port": 80
                }
            }
        ]
    
    def get_activity_timeline(self, project_id=None, days_back=30, include_statuses=None, group_by="day"):
        """Mock activity timeline data with recent dates."""
        now = datetime.utcnow()
        return {
            "activities": [
                {
                    "timestamp": (now - timedelta(days=2, hours=-2)).isoformat() + "Z",
                    "type": "deployment",
                    "action": "Created",
                    "resource": "Demo API Gateway",
                    "user": "demo@example.com",
                    "status": "UPDATE_SUCCESSFUL"
                },
                {
                    "timestamp": (now - timedelta(days=5)).isoformat() + "Z",
                    "type": "deployment",
                    "action": "Created",
                    "resource": "Demo Web App",
                    "user": "demo@example.com",
                    "status": "CREATE_SUCCESSFUL"
                },
                {
                    "timestamp": (now - timedelta(days=10)).isoformat() + "Z",
                    "type": "deployment",
                    "action": "Created",
                    "resource": "Demo Database",
                    "user": "admin@example.com",
                    "status": "CREATE_SUCCESSFUL"
                },
                {
                    "timestamp": (now - timedelta(days=1)).isoformat() + "Z",
                    "type": "failure",
                    "action": "Failed",
                    "resource": "Demo Failed Deploy",
                    "user": "test@example.com",
                    "status": "CREATE_FAILED"
                }
            ],
            "summary": {
                "total_activities": 4,
                "date_range": f"{days_back} days"
            }
        }
    
    def get_catalog_usage_stats(self, project_id=None, fetch_resource_counts=False):
        """Mock catalog usage statistics."""
        return [
            {
                "catalog_item": type('Item', (), {
                    "id": "catalog-item-1",
                    "name": "Ubuntu Virtual Machine",
                    "type": type('Type', (), {"name": "Cloud Template"})()
                })(),
                "deployment_count": 15,
                "resource_count": 30,
                "success_count": 14,
                "failed_count": 1,
                "in_progress_count": 0,
                "success_rate": 93.3,
                "status_counts": {
                    "CREATE_SUCCESSFUL": 14,
                    "CREATE_FAILED": 1
                }
            }
        ]
    
    def get_resources_usage_report(self, project_id=None, include_detailed_resources=True):
        """Mock resources usage report."""
        return {
            "deployments": [
                {
                    "deployment_id": "demo-deployment-1",
                    "name": "Demo Web App",
                    "resources": [
                        {"type": "Virtual Machine", "count": 2, "status": "RUNNING"},
                        {"type": "Load Balancer", "count": 1, "status": "ACTIVE"}
                    ]
                }
            ],
            "summary": {
                "total_deployments": 3,
                "total_resources": 6,
                "resource_types": {
                    "Virtual Machine": 4,
                    "Load Balancer": 2
                }
            }
        }
    
    def get_unsynced_deployments(self, project_id=None, fetch_resource_counts=False):
        """Mock unsynced deployments report."""
        return {
            "unsynced_deployments": [],
            "summary": {
                "total_deployments": 3,
                "unsynced_deployments": 0,
                "unsynced_percentage": 0.0,
                "sync_health": "Good"
            },
            "reasons": {}
        }

def get_catalog_client(verbose: bool = False) -> CatalogClient:
    """Get configured catalog client with automatic token refresh.
    
    Args:
        verbose: Whether to enable verbose HTTP logging
        
    Returns:
        CatalogClient instance
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Check if we're in development mode
        is_dev_mode = os.getenv("VRA_DEV_MODE", "false").lower() == "true"
        
        if is_dev_mode:
            # Return mock client in dev mode
            return MockCatalogClient(verbose=verbose)
        
        # Production mode - use real catalog client
        config = get_config()
        token = TokenManager.get_access_token()
        
        # Try to refresh token if access token is not available or expired
        if not token:
            token = TokenManager.refresh_access_token(
                config["api_url"], 
                config["verify_ssl"]
            )
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No valid authentication token found. Please authenticate first."
            )
        
        return CatalogClient(
            base_url=config["api_url"],
            token=token,
            verify_ssl=config["verify_ssl"],
            verbose=verbose
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating catalog client: {str(e)}"
        )


def handle_client_error(operation: str, error: Exception) -> HTTPException:
    """Handle client errors and convert to appropriate HTTP exceptions.
    
    Args:
        operation: Description of the operation that failed
        error: The original exception
        
    Returns:
        HTTPException with appropriate status code and message
    """
    if "401" in str(error) or "unauthorized" in str(error).lower():
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed during {operation}: {str(error)}"
        )
    elif "403" in str(error) or "forbidden" in str(error).lower():
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access forbidden during {operation}: {str(error)}"
        )
    elif "404" in str(error) or "not found" in str(error).lower():
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource not found during {operation}: {str(error)}"
        )
    elif "400" in str(error) or "bad request" in str(error).lower():
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bad request during {operation}: {str(error)}"
        )
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error during {operation}: {str(error)}"
        )
