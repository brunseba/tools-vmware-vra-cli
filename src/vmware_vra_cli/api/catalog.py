"""Service Catalog API client for VMware vRA."""

import requests
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import json


class CatalogItemType(BaseModel):
    """Represents the type information of a catalog item."""
    id: str
    link: Optional[str] = None
    name: str


class CatalogItem(BaseModel):
    """Represents a catalog item in vRA."""
    id: str
    name: str
    description: Optional[str] = None
    type: CatalogItemType
    status: Optional[str] = None
    version: Optional[str] = None
    icon: Optional[str] = None
    iconId: Optional[str] = None
    form: Optional[Dict[str, Any]] = None
    projectIds: Optional[List[str]] = None
    createdAt: Optional[str] = None
    createdBy: Optional[str] = None
    lastUpdatedAt: Optional[str] = None
    lastUpdatedBy: Optional[str] = None
    bulkRequestLimit: Optional[int] = None


class WorkflowRun(BaseModel):
    """Represents a workflow execution."""
    id: str
    name: str
    state: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    input_parameters: Optional[Dict[str, Any]] = None
    output_parameters: Optional[Dict[str, Any]] = None


class Tag(BaseModel):
    """Represents a tag in vRA."""
    id: str
    key: str
    value: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class CatalogClient:
    """Client for interacting with vRA Service Catalog APIs."""
    
    def __init__(self, base_url: str, token: str, verify_ssl: bool = True):
        """Initialize the catalog client.
        
        Args:
            base_url: Base URL of the vRA instance
            token: Authentication token
            verify_ssl: Whether to verify SSL certificates
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.session.verify = verify_ssl
    
    def list_catalog_items(self, project_id: Optional[str] = None, page_size: int = 100, fetch_all: bool = True) -> List[CatalogItem]:
        """List available catalog items.
        
        Args:
            project_id: Optional project ID to filter items
            page_size: Number of items per page (default: 100, max: 2000)
            fetch_all: Whether to fetch all pages or just the first page (default: True)
            
        Returns:
            List of catalog items
        """
        url = f"{self.base_url}/catalog/api/items"
        all_items = []
        page = 0
        
        while True:
            params = {
                'page': page,
                'size': min(page_size, 2000)  # vRA typically has a max page size limit
            }
            if project_id:
                params['projectId'] = project_id
                
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            items = [CatalogItem(**item) for item in data.get('content', [])]
            all_items.extend(items)
            
            # Check if this is the last page or if we only want the first page
            if not fetch_all or data.get('last', True) or len(items) == 0:
                break
                
            page += 1
        
        return all_items
    
    def get_catalog_item(self, item_id: str) -> CatalogItem:
        """Get details of a specific catalog item.
        
        Args:
            item_id: ID of the catalog item
            
        Returns:
            Catalog item details
        """
        url = f"{self.base_url}/catalog/api/items/{item_id}"
        response = self.session.get(url)
        response.raise_for_status()
        
        return CatalogItem(**response.json())
    
    def get_catalog_item_schema(self, item_id: str) -> Dict[str, Any]:
        """Get the request schema for a catalog item.
        
        Args:
            item_id: ID of the catalog item
            
        Returns:
            Schema definition for the catalog item
        """
        url = f"{self.base_url}/catalog/api/items/{item_id}/schema"
        response = self.session.get(url)
        response.raise_for_status()
        
        return response.json()
    
    def request_catalog_item(self, item_id: str, inputs: Dict[str, Any], 
                           project_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """Request a catalog item.
        
        Args:
            item_id: ID of the catalog item
            inputs: Input parameters for the request
            project_id: Project ID for the request
            reason: Optional reason for the request
            
        Returns:
            Request details including deployment ID
        """
        url = f"{self.base_url}/catalog/api/items/{item_id}/request"
        
        payload = {
            "deploymentName": inputs.get('deploymentName', f"deployment-{item_id}"),
            "projectId": project_id,
            "inputs": inputs
        }
        
        if reason:
            payload["reason"] = reason
            
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def list_deployments(self, project_id: Optional[str] = None, 
                        status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List deployments.
        
        Args:
            project_id: Optional project ID to filter deployments
            status: Optional status to filter deployments
            
        Returns:
            List of deployments
        """
        url = f"{self.base_url}/deployment/api/deployments"
        params = {}
        
        if project_id:
            params['projects'] = project_id
        if status:
            params['status'] = status
            
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        return response.json().get('content', [])
    
    def get_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """Get deployment details.
        
        Args:
            deployment_id: ID of the deployment
            
        Returns:
            Deployment details
        """
        url = f"{self.base_url}/deployment/api/deployments/{deployment_id}"
        response = self.session.get(url)
        response.raise_for_status()
        
        return response.json()
    
    def delete_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """Delete a deployment.
        
        Args:
            deployment_id: ID of the deployment to delete
            
        Returns:
            Operation result
        """
        url = f"{self.base_url}/deployment/api/deployments/{deployment_id}"
        response = self.session.delete(url)
        response.raise_for_status()
        
        return response.json()
    
    def get_deployment_resources(self, deployment_id: str) -> List[Dict[str, Any]]:
        """Get resources of a deployment.
        
        Args:
            deployment_id: ID of the deployment
            
        Returns:
            List of deployment resources
        """
        url = f"{self.base_url}/deployment/api/deployments/{deployment_id}/resources"
        response = self.session.get(url)
        response.raise_for_status()
        
        return response.json().get('content', [])
    
    def run_workflow(self, workflow_id: str, inputs: Dict[str, Any]) -> WorkflowRun:
        """Execute a workflow.
        
        Args:
            workflow_id: ID of the workflow to run
            inputs: Input parameters for the workflow
            
        Returns:
            Workflow run details
        """
        url = f"{self.base_url}/vco/api/workflows/{workflow_id}/executions"
        
        payload = {
            "parameters": [
                {"name": key, "value": {"string": {"value": str(value)}}}
                for key, value in inputs.items()
            ]
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        execution_data = response.json()
        return WorkflowRun(
            id=execution_data['id'],
            name=execution_data.get('name', ''),
            state=execution_data['state'],
            start_date=execution_data.get('start-date'),
            end_date=execution_data.get('end-date'),
            input_parameters=inputs
        )
    
    def get_workflow_run(self, workflow_id: str, execution_id: str) -> WorkflowRun:
        """Get workflow run details.
        
        Args:
            workflow_id: ID of the workflow
            execution_id: ID of the execution
            
        Returns:
            Workflow run details
        """
        url = f"{self.base_url}/vco/api/workflows/{workflow_id}/executions/{execution_id}"
        response = self.session.get(url)
        response.raise_for_status()
        
        data = response.json()
        return WorkflowRun(
            id=data['id'],
            name=data.get('name', ''),
            state=data['state'],
            start_date=data.get('start-date'),
            end_date=data.get('end-date')
        )
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List available workflows.
        
        Returns:
            List of workflows
        """
        url = f"{self.base_url}/vco/api/workflows"
        response = self.session.get(url)
        response.raise_for_status()
        
        return response.json().get('link', [])
    
    def get_workflow_schema(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow input/output schema.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            Workflow schema
        """
        url = f"{self.base_url}/vco/api/workflows/{workflow_id}"
        response = self.session.get(url)
        response.raise_for_status()
        
        return response.json()
    
    def cancel_workflow_run(self, workflow_id: str, execution_id: str) -> bool:
        """Cancel a running workflow.
        
        Args:
            workflow_id: ID of the workflow
            execution_id: ID of the execution to cancel
            
        Returns:
            True if cancellation was successful
        """
        url = f"{self.base_url}/vco/api/workflows/{workflow_id}/executions/{execution_id}/state"
        
        payload = {"value": "canceled"}
        
        response = self.session.put(url, json=payload)
        response.raise_for_status()
        
        return response.status_code == 200
    
    # Tag Management Methods
    
    def list_tags(self, search: Optional[str] = None) -> List[Tag]:
        """List available tags.
        
        Args:
            search: Optional search term to filter tags
            
        Returns:
            List of tags
        """
        url = f"{self.base_url}/vco/api/tags"
        params = {}
        
        if search:
            params['$filter'] = f"substringof('{search}', key) or substringof('{search}', value)"
            
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        tags = []
        
        for item in data.get('value', []):
            tag_data = {
                'id': item.get('id', ''),
                'key': item.get('key', ''),
                'value': item.get('value'),
                'description': item.get('description'),
                'created_at': item.get('createdAt'),
                'updated_at': item.get('updatedAt'),
                'created_by': item.get('createdBy'),
                'updated_by': item.get('updatedBy')
            }
            tags.append(Tag(**tag_data))
            
        return tags
    
    def get_tag(self, tag_id: str) -> Tag:
        """Get details of a specific tag.
        
        Args:
            tag_id: ID of the tag
            
        Returns:
            Tag details
        """
        url = f"{self.base_url}/vco/api/tags/{tag_id}"
        response = self.session.get(url)
        response.raise_for_status()
        
        data = response.json()
        tag_data = {
            'id': data.get('id', ''),
            'key': data.get('key', ''),
            'value': data.get('value'),
            'description': data.get('description'),
            'created_at': data.get('createdAt'),
            'updated_at': data.get('updatedAt'),
            'created_by': data.get('createdBy'),
            'updated_by': data.get('updatedBy')
        }
        
        return Tag(**tag_data)
    
    def create_tag(self, key: str, value: Optional[str] = None, 
                  description: Optional[str] = None) -> Tag:
        """Create a new tag.
        
        Args:
            key: Tag key (required)
            value: Tag value (optional)
            description: Tag description (optional)
            
        Returns:
            Created tag details
        """
        url = f"{self.base_url}/vco/api/tags"
        
        payload = {
            "key": key
        }
        
        if value is not None:
            payload["value"] = value
        if description is not None:
            payload["description"] = description
            
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        tag_data = {
            'id': data.get('id', ''),
            'key': data.get('key', ''),
            'value': data.get('value'),
            'description': data.get('description'),
            'created_at': data.get('createdAt'),
            'updated_at': data.get('updatedAt'),
            'created_by': data.get('createdBy'),
            'updated_by': data.get('updatedBy')
        }
        
        return Tag(**tag_data)
    
    def update_tag(self, tag_id: str, key: Optional[str] = None, 
                  value: Optional[str] = None, description: Optional[str] = None) -> Tag:
        """Update an existing tag.
        
        Args:
            tag_id: ID of the tag to update
            key: New tag key (optional)
            value: New tag value (optional)
            description: New tag description (optional)
            
        Returns:
            Updated tag details
        """
        url = f"{self.base_url}/vco/api/tags/{tag_id}"
        
        # Get current tag to preserve existing values
        current_tag = self.get_tag(tag_id)
        
        payload = {
            "key": key if key is not None else current_tag.key,
            "value": value if value is not None else current_tag.value,
            "description": description if description is not None else current_tag.description
        }
        
        response = self.session.put(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        tag_data = {
            'id': data.get('id', ''),
            'key': data.get('key', ''),
            'value': data.get('value'),
            'description': data.get('description'),
            'created_at': data.get('createdAt'),
            'updated_at': data.get('updatedAt'),
            'created_by': data.get('createdBy'),
            'updated_by': data.get('updatedBy')
        }
        
        return Tag(**tag_data)
    
    def delete_tag(self, tag_id: str) -> bool:
        """Delete a tag.
        
        Args:
            tag_id: ID of the tag to delete
            
        Returns:
            True if deletion was successful
        """
        url = f"{self.base_url}/vco/api/tags/{tag_id}"
        response = self.session.delete(url)
        response.raise_for_status()
        
        return response.status_code == 204
    
    def assign_tag_to_resource(self, resource_id: str, tag_id: str, 
                              resource_type: str = "deployment") -> bool:
        """Assign a tag to a resource.
        
        Args:
            resource_id: ID of the resource
            tag_id: ID of the tag to assign
            resource_type: Type of resource (e.g., 'deployment', 'catalog-item')
            
        Returns:
            True if assignment was successful
        """
        if resource_type == "deployment":
            url = f"{self.base_url}/deployment/api/deployments/{resource_id}/tags"
        elif resource_type == "catalog-item":
            url = f"{self.base_url}/catalog/api/items/{resource_id}/tags"
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")
            
        payload = {"tagId": tag_id}
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        return response.status_code in [200, 201]
    
    def remove_tag_from_resource(self, resource_id: str, tag_id: str, 
                                resource_type: str = "deployment") -> bool:
        """Remove a tag from a resource.
        
        Args:
            resource_id: ID of the resource
            tag_id: ID of the tag to remove
            resource_type: Type of resource (e.g., 'deployment', 'catalog-item')
            
        Returns:
            True if removal was successful
        """
        if resource_type == "deployment":
            url = f"{self.base_url}/deployment/api/deployments/{resource_id}/tags/{tag_id}"
        elif resource_type == "catalog-item":
            url = f"{self.base_url}/catalog/api/items/{resource_id}/tags/{tag_id}"
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")
            
        response = self.session.delete(url)
        response.raise_for_status()
        
        return response.status_code == 204
    
    def get_resource_tags(self, resource_id: str, 
                         resource_type: str = "deployment") -> List[Tag]:
        """Get tags assigned to a resource.
        
        Args:
            resource_id: ID of the resource
            resource_type: Type of resource (e.g., 'deployment', 'catalog-item')
            
        Returns:
            List of tags assigned to the resource
        """
        if resource_type == "deployment":
            url = f"{self.base_url}/deployment/api/deployments/{resource_id}/tags"
        elif resource_type == "catalog-item":
            url = f"{self.base_url}/catalog/api/items/{resource_id}/tags"
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")
            
        response = self.session.get(url)
        response.raise_for_status()
        
        data = response.json()
        tags = []
        
        for item in data.get('content', []):
            tag_data = {
                'id': item.get('id', ''),
                'key': item.get('key', ''),
                'value': item.get('value'),
                'description': item.get('description'),
                'created_at': item.get('createdAt'),
                'updated_at': item.get('updatedAt'),
                'created_by': item.get('createdBy'),
                'updated_by': item.get('updatedBy')
            }
            tags.append(Tag(**tag_data))
            
        return tags
