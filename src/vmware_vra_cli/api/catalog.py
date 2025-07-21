"""Service Catalog API client for VMware vRA."""

import requests
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
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
    item_schema: Optional[Dict[str, Any]] = Field(None, alias='schema')
    projectIds: Optional[List[str]] = None
    createdAt: Optional[str] = None
    createdBy: Optional[str] = None
    lastUpdatedAt: Optional[str] = None
    lastUpdatedBy: Optional[str] = None
    bulkRequestLimit: Optional[int] = None
    formId: Optional[str] = None
    externalId: Optional[str] = None


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
    
    def __init__(self, base_url: str, token: str, verify_ssl: bool = True, verbose: bool = False):
        """Initialize the catalog client.
        
        Args:
            base_url: Base URL of the vRA instance
            token: Authentication token
            verify_ssl: Whether to verify SSL certificates
            verbose: Whether to print HTTP request/response details
        """
        self.base_url = base_url.rstrip('/')
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.session.verify = verify_ssl
    
    def _log_http_request(self, method: str, url: str, params: Optional[Dict] = None, data: Optional[Dict] = None):
        """Log HTTP request details if verbose mode is enabled."""
        if not self.verbose:
            return
            
        print(f"\n[HTTP REQUEST]")
        print(f"Method: {method.upper()}")
        print(f"URL: {url}")
        
        if params:
            print(f"Parameters: {params}")
            
        if data:
            print(f"Request Body: {json.dumps(data, indent=2)}")
            
    def _log_http_response(self, response: requests.Response):
        """Log HTTP response details if verbose mode is enabled."""
        if not self.verbose:
            return
            
        print(f"\n[HTTP RESPONSE]")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"Response Body: {json.dumps(response_json, indent=2)}")
        except (ValueError, requests.exceptions.JSONDecodeError):
            print(f"Response Body (text): {response.text}")
        
        print()
    
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
                
            self._log_http_request('GET', url, params=params)
            response = self.session.get(url, params=params)
            self._log_http_response(response)
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
        self._log_http_request('GET', url)
        response = self.session.get(url)
        self._log_http_response(response)
        response.raise_for_status()
        
        return CatalogItem(**response.json())
    
    def get_catalog_item_schema(self, item_id: str) -> Dict[str, Any]:
        """Get the request schema for a catalog item.
        
        This method first tries to get the schema from the catalog item response itself,
        as many catalog items include their schema directly. If no schema is found,
        it falls back to trying dedicated schema endpoints.
        
        Args:
            item_id: ID of the catalog item
            
        Returns:
            Schema definition for the catalog item
        """
        # First, get the catalog item details which often include the schema
        try:
            item = self.get_catalog_item(item_id)
            item_dict = item.dict()
            
            # Check if schema is included in the catalog item response
            # Access the schema directly from the item object
            if item.item_schema:
                return item.item_schema
                
        except Exception as e:
            # If getting catalog item fails, continue with fallback methods
            pass
        
        # Fallback: try the standard catalog schema endpoint
        url = f"{self.base_url}/catalog/api/items/{item_id}/schema"
        self._log_http_request('GET', url)
        response = self.session.get(url)
        self._log_http_response(response)
        
        if response.status_code == 200:
            response.raise_for_status()
            return response.json()
        
        # If schema endpoint returns 404, try type-specific endpoints
        if response.status_code == 404:
            try:
                item = self.get_catalog_item(item_id)
                item_type = item.type.id
                
                if item_type == "com.vmw.vro.workflow":
                    # For workflows, try the workflow schema endpoint
                    workflow_url = f"{self.base_url}/vco/api/workflows/{item_id}"
                    self._log_http_request('GET', workflow_url)
                    workflow_response = self.session.get(workflow_url)
                    self._log_http_response(workflow_response)
                    
                    if workflow_response.status_code == 200:
                        return workflow_response.json()
                    else:
                        # If workflow endpoint also fails, return a helpful message
                        return {
                            "error": "Schema not available",
                            "message": f"Schema not found in catalog item response and workflow endpoint returned {workflow_response.status_code} for item {item_id}",
                            "item_type": item_type,
                            "suggestion": "Workflows may not expose their schema through the catalog API. Try using the workflow-specific commands."
                        }
                elif item_type == "com.vmw.blueprint":
                    # For blueprints, the schema should be available but might be at a different endpoint
                    return {
                        "error": "Schema not available", 
                        "message": f"Schema not found in catalog item response and schema endpoint returned 404 for blueprint item {item_id}",
                        "item_type": item_type,
                        "suggestion": "This blueprint may not have a publicly accessible schema or may require different permissions."
                    }
                else:
                    return {
                        "error": "Schema not available",
                        "message": f"Schema not found in catalog item response and schema endpoint returned 404 for item {item_id} of type {item_type}",
                        "item_type": item_type
                    }
            except Exception as e:
                return {
                    "error": "Schema not available",
                    "message": f"Failed to retrieve schema for item {item_id}: {str(e)}"
                }
        
        # For other HTTP errors, raise them
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
            
        self._log_http_request('POST', url, data=payload)
        response = self.session.post(url, json=payload)
        self._log_http_response(response)
        response.raise_for_status()
        
        return response.json()
    
    def list_deployments(self, project_id: Optional[str] = None, 
                        status: Optional[str] = None, page_size: int = 100, fetch_all: bool = True) -> List[Dict[str, Any]]:
        """List deployments.
        
        Args:
            project_id: Optional project ID to filter deployments
            status: Optional status to filter deployments
            page_size: Number of items per page (default: 100, max: 2000)
            fetch_all: Whether to fetch all pages or just the first page (default: True)
            
        Returns:
            List of deployments
        """
        url = f"{self.base_url}/deployment/api/deployments"
        all_deployments = []
        page = 0
        
        while True:
            params = {
                'page': page,
                'size': min(page_size, 2000)
            }
            
            if project_id:
                params['projects'] = project_id
            if status:
                params['status'] = status
                
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            deployments = data.get('content', [])
            all_deployments.extend(deployments)
            
            # Check if this is the last page or if we only want the first page
            if not fetch_all or data.get('last', True) or len(deployments) == 0:
                break
                
            page += 1
        
        return all_deployments
    
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
    
    def list_workflows(self, page_size: int = 100, fetch_all: bool = True) -> List[Dict[str, Any]]:
        """List available workflows.
        
        Args:
            page_size: Number of items per page (default: 100, max: 2000)
            fetch_all: Whether to fetch all pages or just the first page (default: True)
        
        Returns:
            List of workflows
        """
        url = f"{self.base_url}/vco/api/workflows"
        all_workflows = []
        page = 0
        
        while True:
            # vCO/vRO API might use different pagination parameters
            params = {
                'maxResult': min(page_size, 2000),
                'startIndex': page * page_size
            }
                
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            workflows = data.get('link', [])
            all_workflows.extend(workflows)
            
            # Check if this is the last page or if we only want the first page
            # vRO API might not have 'last' indicator, so check if we got fewer items than requested
            if not fetch_all or len(workflows) < page_size or len(workflows) == 0:
                break
                
            page += 1
        
        return all_workflows
    
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
    
    def list_tags(self, search: Optional[str] = None, page_size: int = 100, fetch_all: bool = True) -> List[Tag]:
        """List available tags.
        
        Args:
            search: Optional search term to filter tags
            page_size: Number of items per page (default: 100, max: 2000)
            fetch_all: Whether to fetch all pages or just the first page (default: True)
            
        Returns:
            List of tags
        """
        url = f"{self.base_url}/vco/api/tags"
        all_tags = []
        page = 0
        
        while True:
            params = {
                '$skip': page * page_size,
                '$top': min(page_size, 2000)
            }
            
            if search:
                params['$filter'] = f"substringof('{search}', key) or substringof('{search}', value)"
                
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            items = data.get('value', [])
            
            for item in items:
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
                all_tags.append(Tag(**tag_data))
            
            # Check if this is the last page or if we only want the first page
            if not fetch_all or len(items) < page_size or len(items) == 0:
                break
                
            page += 1
            
        return all_tags
    
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
            
        self._log_http_request('POST', url, data=payload)
        response = self.session.post(url, json=payload)
        self._log_http_response(response)
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
        self._log_http_request('DELETE', url)
        response = self.session.delete(url)
        self._log_http_response(response)
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
