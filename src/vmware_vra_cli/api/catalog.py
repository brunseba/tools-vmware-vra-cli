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
    
    def get_catalog_usage_stats(self, project_id: Optional[str] = None, 
                              fetch_resource_counts: bool = False) -> List[Dict[str, Any]]:
        """Get comprehensive usage statistics for catalog items.
        
        This method provides detailed analytics including deployment counts,
        resource counts, and success rates for each catalog item.
        
        Args:
            project_id: Optional project ID to filter items and deployments
            fetch_resource_counts: Whether to fetch actual resource counts (slower but accurate)
            
        Returns:
            List of usage statistics for each catalog item
        """
        # Get all catalog items and deployments
        catalog_items = self.list_catalog_items(project_id=project_id)
        deployments = self.list_deployments(project_id=project_id)
        
        usage_stats = []
        
        for item in catalog_items:
            # Find deployments for this catalog item
            # Match by catalogItemId, blueprintId, or catalogItemName
            item_deployments = [
                d for d in deployments 
                if (d.get('catalogItemId') == item.id or 
                    d.get('blueprintId') == item.id or
                    d.get('catalogItemName') == item.name or
                    # Also check if the deployment name contains the catalog item name
                    (item.name.lower() in d.get('name', '').lower()))
            ]
            
            # Count deployment statuses
            status_counts = {}
            total_resources = 0
            
            for deployment in item_deployments:
                status = deployment.get('status', 'UNKNOWN')
                status_counts[status] = status_counts.get(status, 0) + 1
                
                if fetch_resource_counts:
                    # Fetch actual resource count for this deployment (expensive operation)
                    try:
                        resources = self.get_deployment_resources(deployment.get('id'))
                        total_resources += len(resources)
                    except Exception:
                        # If we can't get resources, estimate conservatively
                        total_resources += 1
                else:
                    # Use simple estimation for better performance
                    if 'resourceCount' in deployment:
                        total_resources += deployment.get('resourceCount', 1)
                    else:
                        # Conservative estimate: at least 1 resource per deployment
                        total_resources += 1
            
            deployment_count = len(item_deployments)
            
            # Calculate success metrics
            success_statuses = ['CREATE_SUCCESSFUL', 'UPDATE_SUCCESSFUL', 'SUCCESSFUL']
            failed_statuses = ['CREATE_FAILED', 'UPDATE_FAILED', 'FAILED']
            progress_statuses = ['CREATE_INPROGRESS', 'UPDATE_INPROGRESS', 'INPROGRESS']
            
            success_count = sum(status_counts.get(status, 0) for status in success_statuses)
            failed_count = sum(status_counts.get(status, 0) for status in failed_statuses)
            in_progress_count = sum(status_counts.get(status, 0) for status in progress_statuses)
            
            success_rate = (success_count / deployment_count * 100) if deployment_count > 0 else 0
            
            stats = {
                'catalog_item': item,
                'deployment_count': deployment_count,
                'resource_count': total_resources,
                'success_count': success_count,
                'failed_count': failed_count,
                'in_progress_count': in_progress_count,
                'success_rate': success_rate,
                'status_counts': status_counts,
                'recent_deployments': sorted(
                    item_deployments, 
                    key=lambda x: x.get('createdAt', ''), 
                    reverse=True
                )[:5]  # Keep last 5 deployments for reference
            }
            
            usage_stats.append(stats)
        
        return usage_stats
    
    def get_unsynced_deployments(self, project_id: Optional[str] = None, 
                               fetch_resource_counts: bool = False) -> Dict[str, Any]:
        """Get deployments that don't match to any catalog items.
        
        This method identifies deployments that cannot be linked back to catalog items,
        which may indicate issues with deployment tracking, deleted catalog items,
        or deployments created outside the service catalog.
        
        Args:
            project_id: Optional project ID to filter deployments
            fetch_resource_counts: Whether to fetch actual resource counts (slower but accurate)
            
        Returns:
            Dictionary containing unsynced deployment details and statistics
        """
        from datetime import datetime
        
        # Get all catalog items and deployments
        catalog_items = self.list_catalog_items(project_id=project_id)
        all_deployments = self.list_deployments(project_id=project_id)
        
        # Create a set of all deployments that are linked to catalog items
        linked_deployment_ids = set()
        
        # Track which deployments are linked to which catalog items
        deployment_to_catalog_map = {}
        
        for item in catalog_items:
            # Find deployments for this catalog item using the same matching logic
            item_deployments = [
                d for d in all_deployments 
                if (d.get('catalogItemId') == item.id or 
                    d.get('blueprintId') == item.id or
                    d.get('catalogItemName') == item.name or
                    # Also check if the deployment name contains the catalog item name
                    (item.name.lower() in d.get('name', '').lower()))
            ]
            
            for deployment in item_deployments:
                deployment_id = deployment.get('id')
                if deployment_id:
                    linked_deployment_ids.add(deployment_id)
                    deployment_to_catalog_map[deployment_id] = item
        
        # Find unsynced deployments
        unsynced_deployments = []
        for deployment in all_deployments:
            deployment_id = deployment.get('id')
            if deployment_id and deployment_id not in linked_deployment_ids:
                # Analyze why this deployment is unsynced
                analysis = self._analyze_unsynced_deployment(deployment, catalog_items)
                
                # Get resource count if requested
                resource_count = 0
                if fetch_resource_counts:
                    try:
                        resources = self.get_deployment_resources(deployment_id)
                        resource_count = len(resources)
                    except Exception:
                        resource_count = 1  # Conservative estimate
                else:
                    resource_count = deployment.get('resourceCount', 1)
                
                unsynced_deployment = {
                    'deployment': deployment,
                    'resource_count': resource_count,
                    'analysis': analysis
                }
                unsynced_deployments.append(unsynced_deployment)
        
        # Calculate statistics
        total_deployments = len(all_deployments)
        linked_deployments = len(linked_deployment_ids)
        unsynced_count = len(unsynced_deployments)
        unsynced_percentage = (unsynced_count / max(total_deployments, 1)) * 100
        
        # Group by analysis reasons
        reason_groups = {}
        for unsync in unsynced_deployments:
            reason = unsync['analysis']['primary_reason']
            if reason not in reason_groups:
                reason_groups[reason] = []
            reason_groups[reason].append(unsync)
        
        # Status breakdown of unsynced deployments
        status_counts = {}
        total_unsynced_resources = 0
        
        for unsync in unsynced_deployments:
            deployment = unsync['deployment']
            status = deployment.get('status', 'UNKNOWN')
            status_counts[status] = status_counts.get(status, 0) + 1
            total_unsynced_resources += unsync['resource_count']
        
        # Age analysis
        now = datetime.now()
        age_groups = {'<24h': 0, '1-7d': 0, '1-4w': 0, '>1m': 0}
        
        for unsync in unsynced_deployments:
            created_at_str = unsync['deployment'].get('createdAt', '')
            if created_at_str:
                try:
                    # Parse timestamp
                    import re
                    clean_timestamp = re.sub(r'\+\d{2}:\d{2}$|Z$', '', created_at_str)
                    if '.' in clean_timestamp:
                        clean_timestamp = clean_timestamp.split('.')[0]
                    
                    created_at = datetime.fromisoformat(clean_timestamp)
                    age_delta = now - created_at
                    age_days = age_delta.days
                    
                    if age_days < 1:
                        age_groups['<24h'] += 1
                    elif age_days <= 7:
                        age_groups['1-7d'] += 1
                    elif age_days <= 28:
                        age_groups['1-4w'] += 1
                    else:
                        age_groups['>1m'] += 1
                        
                except Exception:
                    pass  # Skip deployments with unparseable timestamps
        
        return {
            'summary': {
                'total_deployments': total_deployments,
                'linked_deployments': linked_deployments,
                'unsynced_deployments': unsynced_count,
                'unsynced_percentage': round(unsynced_percentage, 1),
                'total_unsynced_resources': total_unsynced_resources,
                'catalog_items_count': len(catalog_items)
            },
            'unsynced_deployments': unsynced_deployments,
            'reason_groups': {reason: len(group) for reason, group in reason_groups.items()},
            'status_breakdown': status_counts,
            'age_breakdown': age_groups,
            'detailed_reason_groups': reason_groups
        }
    
    def _analyze_unsynced_deployment(self, deployment: Dict[str, Any], 
                                   catalog_items: List[CatalogItem]) -> Dict[str, Any]:
        """Analyze why a deployment is not synced to any catalog item.
        
        Args:
            deployment: The unsynced deployment
            catalog_items: List of all available catalog items
            
        Returns:
            Dictionary containing analysis of why the deployment is unsynced
        """
        analysis = {
            'primary_reason': 'unknown',
            'details': [],
            'suggestions': [],
            'potential_matches': []
        }
        
        deployment_name = deployment.get('name', '').lower()
        catalog_item_id = deployment.get('catalogItemId')
        catalog_item_name = deployment.get('catalogItemName')
        blueprint_id = deployment.get('blueprintId')
        
        # Check for missing catalog item references
        if not catalog_item_id and not catalog_item_name and not blueprint_id:
            analysis['primary_reason'] = 'missing_catalog_references'
            analysis['details'].append('Deployment has no catalogItemId, catalogItemName, or blueprintId')
            analysis['suggestions'].append('This deployment may have been created outside the service catalog')
        
        # Check if referenced catalog item exists
        elif catalog_item_id:
            matching_item = next((item for item in catalog_items if item.id == catalog_item_id), None)
            if not matching_item:
                analysis['primary_reason'] = 'catalog_item_deleted'
                analysis['details'].append(f'Referenced catalog item ID {catalog_item_id} no longer exists')
                analysis['suggestions'].append('The catalog item may have been deleted after deployment creation')
            else:
                analysis['primary_reason'] = 'matching_logic_issue'
                analysis['details'].append('Catalog item exists but matching logic failed')
                analysis['suggestions'].append('There may be an issue with the catalog item matching algorithm')
        
        elif blueprint_id:
            matching_item = next((item for item in catalog_items if item.id == blueprint_id), None)
            if not matching_item:
                analysis['primary_reason'] = 'blueprint_deleted'
                analysis['details'].append(f'Referenced blueprint ID {blueprint_id} no longer exists')
                analysis['suggestions'].append('The blueprint may have been deleted or moved')
            else:
                analysis['primary_reason'] = 'matching_logic_issue'
                analysis['details'].append('Blueprint exists but matching logic failed')
                analysis['suggestions'].append('There may be an issue with the blueprint matching algorithm')
        
        elif catalog_item_name:
            matching_items = [item for item in catalog_items if item.name == catalog_item_name]
            if not matching_items:
                analysis['primary_reason'] = 'catalog_name_mismatch'
                analysis['details'].append(f'No catalog item found with name "{catalog_item_name}"')
                analysis['suggestions'].append('The catalog item may have been renamed or deleted')
                
                # Look for similar names
                similar_items = [item for item in catalog_items 
                               if catalog_item_name.lower() in item.name.lower() or 
                                  item.name.lower() in catalog_item_name.lower()]
                if similar_items:
                    analysis['potential_matches'] = [{
                        'id': item.id,
                        'name': item.name,
                        'similarity_reason': 'name_substring_match'
                    } for item in similar_items[:3]]  # Limit to top 3
        
        # Look for potential matches based on deployment name
        if not analysis['potential_matches'] and deployment_name:
            name_matches = []
            for item in catalog_items:
                item_name_lower = item.name.lower()
                # Check various name matching strategies
                if (deployment_name in item_name_lower or 
                    item_name_lower in deployment_name or
                    # Check for common prefixes/suffixes
                    any(word in item_name_lower for word in deployment_name.split() if len(word) > 3)):
                    
                    name_matches.append({
                        'id': item.id,
                        'name': item.name,
                        'similarity_reason': 'deployment_name_similarity'
                    })
            
            if name_matches:
                analysis['potential_matches'] = name_matches[:3]  # Limit to top 3
                if analysis['primary_reason'] == 'unknown':
                    analysis['primary_reason'] = 'weak_name_association'
                    analysis['details'].append('Deployment name suggests possible catalog item association')
                    analysis['suggestions'].append('Review potential matches to identify the correct catalog item')
        
        # If still unknown, provide general analysis
        if analysis['primary_reason'] == 'unknown':
            if deployment.get('status') in ['FAILED', 'CREATE_FAILED', 'UPDATE_FAILED']:
                analysis['primary_reason'] = 'failed_deployment'
                analysis['details'].append('Deployment failed - may not have been properly linked')
                analysis['suggestions'].append('Failed deployments sometimes lose catalog associations')
            else:
                analysis['primary_reason'] = 'external_creation'
                analysis['details'].append('Deployment appears to have been created outside service catalog')
                analysis['suggestions'].append('This may be a direct vRA deployment or imported from another system')
        
        return analysis
    
    def export_deployments_by_catalog_item(self, project_id: Optional[str] = None, 
                                          output_dir: str = "./exports",
                                          include_resources: bool = False,
                                          include_unsynced: bool = True) -> Dict[str, Any]:
        """Export all deployments grouped by catalog item ID to separate JSON files.
        
        This method fetches all deployments and groups them by their associated catalog item ID,
        then exports each group to a separate JSON file. This is useful for backup, analysis,
        or migration purposes.
        
        Args:
            project_id: Optional project ID to filter deployments
            output_dir: Directory to save the exported JSON files (default: ./exports)
            include_resources: Whether to include resource details for each deployment
            include_unsynced: Whether to include deployments not linked to catalog items
            
        Returns:
            Dictionary containing export summary and statistics
        """
        import os
        from collections import defaultdict
        from datetime import datetime
        
        # Get all deployments and catalog items
        all_deployments = self.list_deployments(project_id=project_id)
        catalog_items = self.list_catalog_items(project_id=project_id)
        
        # Create catalog item lookup for enrichment
        catalog_item_lookup = {item.id: item for item in catalog_items}
        
        # Group deployments by catalog item ID
        deployments_by_catalog_item = defaultdict(list)
        unsynced_deployments = []
        
        # Process each deployment
        for deployment in all_deployments:
            deployment_data = dict(deployment)  # Make a copy
            
            # Try to determine catalog item ID using the same logic as other methods
            catalog_item_id = None
            
            # Check various fields for catalog item reference
            if deployment.get('catalogItemId'):
                catalog_item_id = deployment.get('catalogItemId')
            elif deployment.get('blueprintId'):
                catalog_item_id = deployment.get('blueprintId')
            elif deployment.get('catalogItemName'):
                # Try to find catalog item by name
                catalog_item_name = deployment.get('catalogItemName')
                matching_item = next((item for item in catalog_items if item.name == catalog_item_name), None)
                if matching_item:
                    catalog_item_id = matching_item.id
            else:
                # Try name-based matching as fallback
                deployment_name = deployment.get('name', '').lower()
                if deployment_name:
                    for item in catalog_items:
                        if item.name.lower() in deployment_name or deployment_name in item.name.lower():
                            catalog_item_id = item.id
                            break
            
            # Include resource details if requested
            if include_resources:
                try:
                    deployment_id = deployment.get('id')
                    if deployment_id:
                        resources = self.get_deployment_resources(deployment_id)
                        deployment_data['resources'] = resources
                        deployment_data['resource_count'] = len(resources)
                except Exception as e:
                    if self.verbose:
                        print(f"Warning: Could not fetch resources for deployment {deployment_id}: {e}")
                    deployment_data['resources'] = []
                    deployment_data['resource_count'] = 0
            
            # Add catalog item information if available
            if catalog_item_id and catalog_item_id in catalog_item_lookup:
                catalog_item = catalog_item_lookup[catalog_item_id]
                deployment_data['_catalog_item_info'] = {
                    'id': catalog_item.id,
                    'name': catalog_item.name,
                    'type': catalog_item.type.name,
                    'status': catalog_item.status,
                    'version': catalog_item.version,
                    'description': catalog_item.description
                }
                deployments_by_catalog_item[catalog_item_id].append(deployment_data)
            else:
                # Unsynced deployment
                deployment_data['_unsynced_reason'] = self._determine_unsynced_reason(deployment, catalog_items)
                if include_unsynced:
                    unsynced_deployments.append(deployment_data)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Export metadata
        export_timestamp = datetime.now().isoformat()
        total_deployments = len(all_deployments)
        synced_deployments = sum(len(deps) for deps in deployments_by_catalog_item.values())
        
        export_summary = {
            'export_timestamp': export_timestamp,
            'export_parameters': {
                'project_id': project_id,
                'include_resources': include_resources,
                'include_unsynced': include_unsynced
            },
            'statistics': {
                'total_deployments': total_deployments,
                'synced_deployments': synced_deployments,
                'unsynced_deployments': len(unsynced_deployments),
                'catalog_items_with_deployments': len(deployments_by_catalog_item),
                'total_catalog_items': len(catalog_items)
            },
            'exported_files': []
        }
        
        files_created = 0
        
        # Export deployments by catalog item
        for catalog_item_id, deployments in deployments_by_catalog_item.items():
            # Get catalog item info for filename
            catalog_item = catalog_item_lookup.get(catalog_item_id)
            if catalog_item:
                # Create safe filename
                safe_name = "".join(c for c in catalog_item.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_name = safe_name.replace(' ', '_')
                filename = f"{safe_name}_{catalog_item_id}.json"
            else:
                filename = f"unknown_catalog_item_{catalog_item_id}.json"
            
            filepath = os.path.join(output_dir, filename)
            
            # Prepare export data
            export_data = {
                'catalog_item_id': catalog_item_id,
                'catalog_item_info': catalog_item.dict() if catalog_item else None,
                'export_timestamp': export_timestamp,
                'deployment_count': len(deployments),
                'deployments': deployments
            }
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            export_summary['exported_files'].append({
                'filename': filename,
                'filepath': filepath,
                'catalog_item_id': catalog_item_id,
                'catalog_item_name': catalog_item.name if catalog_item else 'Unknown',
                'deployment_count': len(deployments)
            })
            
            files_created += 1
        
        # Export unsynced deployments if requested and present
        if include_unsynced and unsynced_deployments:
            unsynced_filename = "unsynced_deployments.json"
            unsynced_filepath = os.path.join(output_dir, unsynced_filename)
            
            unsynced_export_data = {
                'export_timestamp': export_timestamp,
                'description': 'Deployments that could not be linked to any catalog item',
                'deployment_count': len(unsynced_deployments),
                'deployments': unsynced_deployments
            }
            
            with open(unsynced_filepath, 'w', encoding='utf-8') as f:
                json.dump(unsynced_export_data, f, indent=2, ensure_ascii=False)
            
            export_summary['exported_files'].append({
                'filename': unsynced_filename,
                'filepath': unsynced_filepath,
                'catalog_item_id': None,
                'catalog_item_name': 'Unsynced Deployments',
                'deployment_count': len(unsynced_deployments)
            })
            
            files_created += 1
        
        # Save export summary
        summary_filename = "export_summary.json"
        summary_filepath = os.path.join(output_dir, summary_filename)
        
        with open(summary_filepath, 'w', encoding='utf-8') as f:
            json.dump(export_summary, f, indent=2, ensure_ascii=False)
        
        files_created += 1
        
        export_summary['files_created'] = files_created
        
        return export_summary
    
    def export_catalog_schemas(self, project_id: Optional[str] = None,
                             output_dir: str = "./schema_exports",
                             format_type: str = "json") -> Dict[str, Any]:
        """Export all catalog item schemas to separate files.
        
        This method fetches all catalog items and exports their schemas to individual files
        in the specified output directory. This is useful for backup, documentation,
        or development purposes.
        
        Args:
            project_id: Optional project ID to filter catalog items
            output_dir: Directory to save the exported schema files (default: ./schema_exports)
            format_type: Output format ('json' or 'yaml', default: 'json')
            
        Returns:
            Dictionary containing export summary and statistics
        """
        import os
        import yaml
        from datetime import datetime
        
        # Get all catalog items
        catalog_items = self.list_catalog_items(project_id=project_id)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Export metadata
        export_timestamp = datetime.now().isoformat()
        
        export_summary = {
            'export_timestamp': export_timestamp,
            'export_parameters': {
                'project_id': project_id,
                'output_dir': output_dir,
                'format_type': format_type
            },
            'statistics': {
                'total_catalog_items': len(catalog_items),
                'successful_exports': 0,
                'failed_exports': 0,
                'items_without_schema': 0
            },
            'exported_files': [],
            'failed_items': [],
            'items_without_schema': []
        }
        
        files_created = 0
        
        # Export schema for each catalog item
        for item in catalog_items:
            try:
                # Create safe filename based on item name and ID
                safe_name = "".join(c for c in item.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_name = safe_name.replace(' ', '_')
                
                file_extension = 'yaml' if format_type == 'yaml' else 'json'
                filename = f"{safe_name}_{item.id}_schema.{file_extension}"
                filepath = os.path.join(output_dir, filename)
                
                # Get the schema for this catalog item
                try:
                    schema = self.get_catalog_item_schema(item.id)
                    
                    if not schema or (isinstance(schema, dict) and len(schema) == 0):
                        # No schema available for this item
                        export_summary['items_without_schema'].append({
                            'id': item.id,
                            'name': item.name,
                            'type': item.type.name,
                            'reason': 'Schema is empty or unavailable'
                        })
                        export_summary['statistics']['items_without_schema'] += 1
                        continue
                    
                    # Prepare export data with metadata
                    export_data = {
                        'catalog_item_info': {
                            'id': item.id,
                            'name': item.name,
                            'type': item.type.name,
                            'status': item.status,
                            'version': item.version,
                            'description': item.description
                        },
                        'export_timestamp': export_timestamp,
                        'schema': schema
                    }
                    
                    # Write to file
                    with open(filepath, 'w', encoding='utf-8') as f:
                        if format_type == 'yaml':
                            yaml.dump(export_data, f, default_flow_style=False, indent=2)
                        else:
                            json.dump(export_data, f, indent=2, ensure_ascii=False)
                    
                    export_summary['exported_files'].append({
                        'filename': filename,
                        'filepath': filepath,
                        'catalog_item_id': item.id,
                        'catalog_item_name': item.name,
                        'catalog_item_type': item.type.name,
                        'schema_size': len(json.dumps(schema)) if schema else 0
                    })
                    
                    export_summary['statistics']['successful_exports'] += 1
                    files_created += 1
                    
                except Exception as schema_error:
                    # Failed to get schema for this item
                    export_summary['failed_items'].append({
                        'id': item.id,
                        'name': item.name,
                        'type': item.type.name,
                        'error': str(schema_error)
                    })
                    export_summary['statistics']['failed_exports'] += 1
                    
                    if self.verbose:
                        print(f"Warning: Could not export schema for {item.name} ({item.id}): {schema_error}")
                    
            except Exception as item_error:
                # Failed to process this item entirely
                export_summary['failed_items'].append({
                    'id': item.id,
                    'name': item.name,
                    'type': item.type.name if hasattr(item, 'type') else 'Unknown',
                    'error': f"Item processing error: {str(item_error)}"
                })
                export_summary['statistics']['failed_exports'] += 1
                
                if self.verbose:
                    print(f"Warning: Could not process catalog item {item.id}: {item_error}")
        
        # Save export summary
        summary_filename = f"schema_export_summary.{format_type}"
        summary_filepath = os.path.join(output_dir, summary_filename)
        
        with open(summary_filepath, 'w', encoding='utf-8') as f:
            if format_type == 'yaml':
                yaml.dump(export_summary, f, default_flow_style=False, indent=2)
            else:
                json.dump(export_summary, f, indent=2, ensure_ascii=False)
        
        files_created += 1
        export_summary['files_created'] = files_created
        
        return export_summary
    
    def _determine_unsynced_reason(self, deployment: Dict[str, Any], 
                                 catalog_items: List[CatalogItem]) -> str:
        """Determine why a deployment is unsynced (simplified version for export)."""
        if not deployment.get('catalogItemId') and not deployment.get('catalogItemName') and not deployment.get('blueprintId'):
            return 'missing_catalog_references'
        elif deployment.get('catalogItemId'):
            return 'catalog_item_deleted'
        elif deployment.get('blueprintId'):
            return 'blueprint_deleted'
        elif deployment.get('catalogItemName'):
            return 'catalog_name_mismatch'
        else:
            return 'unknown'
    
    def get_activity_timeline(self, project_id: Optional[str] = None,
                            days_back: int = 30,
                            include_statuses: Optional[List[str]] = None,
                            group_by: str = 'day') -> Dict[str, Any]:
        """Get deployment activity timeline for analytics.
        
        This method provides a timeline view of deployment activity, showing
        patterns of usage over time including creation, updates, and failures.
        
        Args:
            project_id: Optional project ID to filter deployments
            days_back: Number of days to look back for activity (default: 30)
            include_statuses: List of deployment statuses to include (default: all)
            group_by: How to group results ('day', 'week', 'month', 'year')
            
        Returns:
            Dictionary containing timeline data with dates, activity counts, and trends
        """
        from datetime import datetime, timedelta
        from collections import defaultdict
        import re
        
        # Get deployments
        deployments = self.list_deployments(project_id=project_id)
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Parse deployment timestamps and organize by time period
        period_activity = defaultdict(lambda: {
            'total_deployments': 0,
            'successful_deployments': 0,
            'failed_deployments': 0,
            'in_progress_deployments': 0,
            'catalog_items': set(),
            'projects': set(),
            'deployments': []
        })
        
        # Track catalog item activity
        catalog_item_timeline = defaultdict(lambda: defaultdict(int))
        hourly_activity = defaultdict(int)
        status_timeline = defaultdict(lambda: defaultdict(int))
        
        total_deployments = 0
        successful_deployments = 0
        failed_deployments = 0
        in_progress_deployments = 0
        
        success_statuses = ['CREATE_SUCCESSFUL', 'UPDATE_SUCCESSFUL', 'SUCCESSFUL']
        failed_statuses = ['CREATE_FAILED', 'UPDATE_FAILED', 'FAILED']
        progress_statuses = ['CREATE_INPROGRESS', 'UPDATE_INPROGRESS', 'INPROGRESS']
        
        if include_statuses is None:
            include_statuses = success_statuses + failed_statuses + progress_statuses + ['DELETED', 'ABORTED']
        
        for deployment in deployments:
            # Parse creation timestamp
            created_at_str = deployment.get('createdAt', '')
            if not created_at_str:
                continue
                
            try:
                # Handle ISO format with timezone
                # Remove timezone info for simpler parsing
                clean_timestamp = re.sub(r'\+\d{2}:\d{2}$|Z$', '', created_at_str)
                if '.' in clean_timestamp:
                    # Handle microseconds
                    clean_timestamp = clean_timestamp.split('.')[0]
                
                created_at = datetime.fromisoformat(clean_timestamp)
                
                # Skip deployments outside our date range
                if created_at < start_date or created_at > end_date:
                    continue
                    
                status = deployment.get('status', 'UNKNOWN')
                if status not in include_statuses:
                    continue
                    
                # Generate period key based on group_by parameter
                if group_by == 'day':
                    period_key = created_at.strftime('%Y-%m-%d')
                elif group_by == 'week':
                    # ISO week: YYYY-W##
                    year, week, _ = created_at.isocalendar()
                    period_key = f"{year}-W{week:02d}"
                elif group_by == 'month':
                    period_key = created_at.strftime('%Y-%m')
                elif group_by == 'year':
                    period_key = created_at.strftime('%Y')
                else:
                    period_key = created_at.strftime('%Y-%m-%d')  # fallback to daily
                
                hour_key = created_at.strftime('%H')
                
                # Period activity
                period_activity[period_key]['total_deployments'] += 1
                period_activity[period_key]['deployments'].append({
                    'id': deployment.get('id'),
                    'name': deployment.get('name'),
                    'status': status,
                    'catalog_item': deployment.get('catalogItemName', 'Unknown'),
                    'time': created_at.strftime('%H:%M:%S'),
                    'date': created_at.strftime('%Y-%m-%d')
                })
                
                # Track catalog items and projects
                if deployment.get('catalogItemName'):
                    period_activity[period_key]['catalog_items'].add(deployment.get('catalogItemName'))
                if deployment.get('projectId'):
                    period_activity[period_key]['projects'].add(deployment.get('projectId'))
                
                # Status-based counting
                if status in success_statuses:
                    period_activity[period_key]['successful_deployments'] += 1
                    successful_deployments += 1
                elif status in failed_statuses:
                    period_activity[period_key]['failed_deployments'] += 1
                    failed_deployments += 1
                elif status in progress_statuses:
                    period_activity[period_key]['in_progress_deployments'] += 1
                    in_progress_deployments += 1
                
                # Catalog item timeline
                catalog_item_name = deployment.get('catalogItemName', 'Unknown')
                catalog_item_timeline[catalog_item_name][period_key] += 1
                
                # Hourly distribution
                hourly_activity[hour_key] += 1
                
                # Status timeline
                status_timeline[status][period_key] += 1
                
                total_deployments += 1
                
            except Exception as e:
                # Skip deployments with invalid timestamps
                if self.verbose:
                    print(f"Warning: Could not parse timestamp '{created_at_str}': {e}")
                continue
        
        # Convert sets to counts for JSON serialization
        for period_data in period_activity.values():
            period_data['unique_catalog_items'] = len(period_data['catalog_items'])
            period_data['unique_projects'] = len(period_data['projects'])
            period_data['catalog_items'] = list(period_data['catalog_items'])
            period_data['projects'] = list(period_data['projects'])
        
        # Generate period range for missing periods (fill gaps with zero activity)
        # Only fill gaps for daily grouping to avoid complexity with weeks/months
        if group_by == 'day':
            current_date = start_date
            while current_date <= end_date:
                period_key = current_date.strftime('%Y-%m-%d')
                if period_key not in period_activity:
                    period_activity[period_key] = {
                        'total_deployments': 0,
                        'successful_deployments': 0,
                        'failed_deployments': 0,
                        'in_progress_deployments': 0,
                        'unique_catalog_items': 0,
                        'unique_projects': 0,
                        'catalog_items': [],
                        'projects': [],
                        'deployments': []
                    }
                current_date += timedelta(days=1)
        
        # Calculate trends and insights
        sorted_periods = sorted(period_activity.keys())
        if len(sorted_periods) >= 2:
            # Calculate trend based on first half vs second half of data
            mid_point = len(sorted_periods) // 2
            recent_activity = sum(period_activity[period]['total_deployments'] 
                               for period in sorted_periods[mid_point:])  
            previous_activity = sum(period_activity[period]['total_deployments'] 
                                 for period in sorted_periods[:mid_point])  
            
            trend = 'increasing' if recent_activity > previous_activity else 'decreasing' if recent_activity < previous_activity else 'stable'
            trend_percentage = ((recent_activity - previous_activity) / max(previous_activity, 1)) * 100
        else:
            trend = 'insufficient_data'
            trend_percentage = 0
        
        # Find peak activity period
        if period_activity:
            peak_period = max(period_activity.keys(), key=lambda p: period_activity[p]['total_deployments'])
            peak_activity = period_activity[peak_period]['total_deployments']
            # If peak activity is 0 (all periods have zero activity), set to N/A
            if peak_activity == 0:
                peak_period = 'N/A'
        else:
            peak_period = 'N/A'
            peak_activity = 0
        
        # Find most active hour
        if hourly_activity:
            peak_hour = max(hourly_activity.keys(), key=hourly_activity.get)
            peak_hour_count = hourly_activity[peak_hour]
        else:
            peak_hour = 'N/A'
            peak_hour_count = 0
        
        # Calculate success rate
        success_rate = (successful_deployments / max(total_deployments, 1)) * 100
        
        return {
            'summary': {
                'period_days': days_back,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'total_deployments': total_deployments,
                'successful_deployments': successful_deployments,
                'failed_deployments': failed_deployments,
                'in_progress_deployments': in_progress_deployments,
                'success_rate': round(success_rate, 1),
                'trend': trend,
                'trend_percentage': round(trend_percentage, 1),
                'peak_activity_period': peak_period,
                'peak_activity_count': peak_activity,
                'grouping': group_by,
                'peak_hour': f"{peak_hour}:00" if peak_hour != 'N/A' else peak_hour,
                'peak_hour_count': peak_hour_count,
                'unique_catalog_items': len(set(d.get('catalogItemName', 'Unknown') 
                                              for d in deployments if d.get('catalogItemName'))),
                'unique_projects': len(set(d.get('projectId') for d in deployments if d.get('projectId')))
            },
            'period_activity': dict(period_activity),
            'catalog_item_timeline': dict(catalog_item_timeline),
            'hourly_distribution': dict(hourly_activity),
            'status_timeline': dict(status_timeline)
        }
    
    def get_resources_usage_report(self, project_id: Optional[str] = None, 
                                  include_detailed_resources: bool = True) -> Dict[str, Any]:
        """Generate a comprehensive resources usage report across all deployments.
        
        This method analyzes all resources existing in each deployment, providing detailed
        information about resource types, counts, states, and their relationship to catalog items.
        
        Args:
            project_id: Optional project ID to filter deployments
            include_detailed_resources: Whether to fetch detailed resource information for each deployment
                                      (True = more detailed but slower, False = faster with basic counts)
        
        Returns:
            Dictionary containing comprehensive resource usage data including:
            - summary: Overall statistics and counts
            - deployments: List of deployments with their resource information
            - catalog_item_summary: Resource utilization grouped by catalog item
            - unlinked_deployments: Deployments that cannot be linked to catalog items
        """
        from rich.console import Console
        from collections import defaultdict, Counter
        console = Console()
        
        # Get all deployments
        deployments = self.list_deployments(project_id=project_id)
        
        # Get all catalog items for matching
        catalog_items = self.list_catalog_items()
        catalog_items_dict = {item.id: item for item in catalog_items}
        
        # Initialize data structures
        deployment_data = []
        catalog_item_summary = defaultdict(lambda: {
            'deployment_count': 0,
            'total_resources': 0,
            'resource_types': Counter(),
            'resource_states': Counter(),
            'catalog_item_info': None
        })
        
        resource_type_counter = Counter()
        resource_state_counter = Counter()
        unlinked_deployments = []
        
        # Process each deployment
        for i, deployment in enumerate(deployments):
            deployment_id = deployment.get('id')
            deployment_name = deployment.get('name', 'Unknown')
            deployment_status = deployment.get('status', 'Unknown')
            catalog_item_id = deployment.get('catalogItemId')
            catalog_item_name = deployment.get('catalogItemName')
            created_at = deployment.get('createdAt')
            
            if self.verbose:
                console.print(f"Processing deployment {i+1}/{len(deployments)}: {deployment_name}")
            
            # Initialize deployment data
            deployment_info = {
                'id': deployment_id,
                'name': deployment_name,
                'status': deployment_status,
                'catalog_item_id': catalog_item_id,
                'catalog_item_name': catalog_item_name,
                'created_at': created_at,
                'resource_count': 0,
                'catalog_item_info': None
            }
            
            # Get catalog item information
            if catalog_item_id and catalog_item_id in catalog_items_dict:
                catalog_item = catalog_items_dict[catalog_item_id]
                deployment_info['catalog_item_info'] = {
                    'id': catalog_item.id,
                    'name': catalog_item.name,
                    'type': catalog_item.type.name,
                    'status': catalog_item.status
                }
            
            # Get resources for this deployment
            resource_count = 0
            resource_breakdown = Counter()
            resource_state_breakdown = Counter()
            
            if include_detailed_resources:
                try:
                    resources = self.get_deployment_resources(deployment_id)
                    resource_count = len(resources)
                    
                    # Analyze resource details
                    for resource in resources:
                        resource_type = resource.get('type', 'Unknown')
                        resource_state = resource.get('state', resource.get('status', 'Unknown'))
                        
                        resource_breakdown[resource_type] += 1
                        resource_state_breakdown[resource_state] += 1
                        resource_type_counter[resource_type] += 1
                        resource_state_counter[resource_state] += 1
                    
                    deployment_info['resource_breakdown'] = dict(resource_breakdown)
                    deployment_info['resource_states'] = dict(resource_state_breakdown)
                    
                except Exception as e:
                    # If resource fetching fails, use basic count estimation
                    if self.verbose:
                        console.print(f"Warning: Could not fetch resources for deployment {deployment_name}: {e}")
                    
                    # Try to estimate resource count from deployment properties
                    resource_count = self._estimate_resource_count(deployment)
                    deployment_info['resource_breakdown'] = {'Unknown': resource_count}
                    deployment_info['resource_states'] = {'Unknown': resource_count}
            else:
                # Fast mode: estimate resource count without detailed fetching
                resource_count = self._estimate_resource_count(deployment)
                deployment_info['resource_breakdown'] = {'Estimated': resource_count}
                deployment_info['resource_states'] = {'Estimated': resource_count}
                resource_type_counter['Estimated'] += resource_count
                resource_state_counter['Estimated'] += resource_count
            
            deployment_info['resource_count'] = resource_count
            deployment_data.append(deployment_info)
            
            # Update catalog item summary
            if catalog_item_id and catalog_item_id in catalog_items_dict:
                catalog_item = catalog_items_dict[catalog_item_id]
                summary = catalog_item_summary[catalog_item_id]
                summary['deployment_count'] += 1
                summary['total_resources'] += resource_count
                summary['catalog_item_info'] = {
                    'id': catalog_item.id,
                    'name': catalog_item.name,
                    'type': catalog_item.type.name,
                    'status': catalog_item.status
                }
                
                if include_detailed_resources and 'resource_breakdown' in deployment_info:
                    for resource_type, count in deployment_info['resource_breakdown'].items():
                        summary['resource_types'][resource_type] += count
                    for resource_state, count in deployment_info['resource_states'].items():
                        summary['resource_states'][resource_state] += count
            else:
                # Track unlinked deployments
                deployment_info['unlinked_reason'] = self._analyze_unlink_reason(deployment, catalog_items_dict)
                unlinked_deployments.append(deployment_info)
        
        # Calculate summary statistics
        total_deployments = len(deployments)
        total_resources = sum(d['resource_count'] for d in deployment_data)
        linked_deployments = total_deployments - len(unlinked_deployments)
        unique_resource_types = len(resource_type_counter)
        unique_catalog_items = len([k for k, v in catalog_item_summary.items() if v['deployment_count'] > 0])
        
        return {
            'summary': {
                'total_deployments': total_deployments,
                'linked_deployments': linked_deployments,
                'unlinked_deployments': len(unlinked_deployments),
                'total_resources': total_resources,
                'unique_resource_types': unique_resource_types,
                'unique_catalog_items': unique_catalog_items,
                'resource_types': dict(resource_type_counter),
                'resource_states': dict(resource_state_counter),
                'average_resources_per_deployment': round(total_resources / max(total_deployments, 1), 2)
            },
            'deployments': deployment_data,
            'catalog_item_summary': dict(catalog_item_summary),
            'unlinked_deployments': unlinked_deployments
        }
    
    def _estimate_resource_count(self, deployment: Dict[str, Any]) -> int:
        """Estimate resource count for a deployment without fetching detailed resources.
        
        This method uses heuristics based on deployment properties to estimate
        the number of resources, useful for fast mode operation.
        
        Args:
            deployment: Deployment data dictionary
            
        Returns:
            Estimated number of resources
        """
        # Basic heuristic: most simple deployments have 1-3 resources
        # More complex deployments might have more based on certain indicators
        
        base_count = 1  # At least one resource (usually the main VM/container)
        
        # Look for indicators of complexity
        deployment_name = deployment.get('name', '').lower()
        catalog_item_name = deployment.get('catalogItemName', '').lower()
        
        # Heuristics based on naming patterns
        complexity_indicators = [
            'cluster', 'load-balancer', 'lb', 'database', 'db', 'multi-tier',
            'ha', 'high-availability', 'distributed', 'micro', 'service'
        ]
        
        complexity_score = 0
        for indicator in complexity_indicators:
            if indicator in deployment_name or indicator in catalog_item_name:
                complexity_score += 1
        
        # Estimate based on complexity
        if complexity_score >= 3:
            return base_count + 4  # Complex deployment
        elif complexity_score >= 1:
            return base_count + 2  # Moderate complexity
        else:
            return base_count  # Simple deployment
    
    def _analyze_unlink_reason(self, deployment: Dict[str, Any], 
                              catalog_items_dict: Dict[str, CatalogItem]) -> Dict[str, Any]:
        """Analyze why a deployment cannot be linked to a catalog item.
        
        Args:
            deployment: Deployment data dictionary
            catalog_items_dict: Dictionary of catalog items by ID
            
        Returns:
            Dictionary containing analysis of why the deployment is unlinked
        """
        catalog_item_id = deployment.get('catalogItemId')
        catalog_item_name = deployment.get('catalogItemName')
        
        if not catalog_item_id and not catalog_item_name:
            return {
                'primary_reason': 'missing_catalog_references',
                'details': 'No catalog item ID or name found in deployment'
            }
        elif catalog_item_id and catalog_item_id not in catalog_items_dict:
            return {
                'primary_reason': 'catalog_item_deleted',
                'details': f'Catalog item ID {catalog_item_id} no longer exists'
            }
        elif catalog_item_name and not catalog_item_id:
            # Try to find by name
            matching_items = [item for item in catalog_items_dict.values() 
                            if item.name.lower() == catalog_item_name.lower()]
            if not matching_items:
                return {
                    'primary_reason': 'catalog_name_mismatch',
                    'details': f'No catalog item found with name "{catalog_item_name}"'
                }
            else:
                return {
                    'primary_reason': 'weak_name_association',
                    'details': f'Found potential matches by name but no direct ID link'
                }
        else:
            return {
                'primary_reason': 'unknown',
                'details': 'Could not determine why deployment is unlinked'
            }
