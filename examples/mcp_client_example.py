#!/usr/bin/env python3
"""
Example client script for VMware vRA MCP Server.

This script demonstrates how to interact with the MCP server programmatically.
"""

import requests
import json
import time
from typing import Dict, Any, Optional


class VRAMCPClient:
    """Client for VMware vRA MCP Server."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the client.
        
        Args:
            base_url: Base URL of the MCP server
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a request to the MCP server.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional arguments for requests
            
        Returns:
            JSON response from server
            
        Raises:
            requests.RequestException: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict[str, Any]:
        """Check server health."""
        return self._make_request('GET', '/health')
    
    def login(self, username: str, password: str, url: str, 
              tenant: Optional[str] = None, domain: Optional[str] = None) -> Dict[str, Any]:
        """Authenticate to vRA.
        
        Args:
            username: vRA username
            password: vRA password
            url: vRA server URL
            tenant: vRA tenant (optional)
            domain: vRA domain (optional)
            
        Returns:
            Authentication response
        """
        data = {
            'username': username,
            'password': password,
            'url': url,
            'tenant': tenant,
            'domain': domain
        }
        return self._make_request('POST', '/auth/login', json=data)
    
    def auth_status(self) -> Dict[str, Any]:
        """Check authentication status."""
        return self._make_request('GET', '/auth/status')
    
    def logout(self) -> Dict[str, Any]:
        """Logout and clear tokens."""
        return self._make_request('POST', '/auth/logout')
    
    def list_catalog_items(self, project_id: Optional[str] = None, 
                          page_size: int = 100, first_page_only: bool = False) -> Dict[str, Any]:
        """List catalog items.
        
        Args:
            project_id: Filter by project ID
            page_size: Number of items per page
            first_page_only: Fetch only first page
            
        Returns:
            List of catalog items
        """
        params = {
            'page_size': page_size,
            'first_page_only': first_page_only
        }
        if project_id:
            params['project_id'] = project_id
        
        return self._make_request('GET', '/catalog/items', params=params)
    
    def get_catalog_item(self, item_id: str) -> Dict[str, Any]:
        """Get catalog item details.
        
        Args:
            item_id: Catalog item ID
            
        Returns:
            Catalog item details
        """
        return self._make_request('GET', f'/catalog/items/{item_id}')
    
    def get_catalog_item_schema(self, item_id: str) -> Dict[str, Any]:
        """Get catalog item schema.
        
        Args:
            item_id: Catalog item ID
            
        Returns:
            Catalog item schema
        """
        return self._make_request('GET', f'/catalog/items/{item_id}/schema')
    
    def request_catalog_item(self, item_id: str, project_id: str, 
                           inputs: Optional[Dict[str, Any]] = None,
                           name: Optional[str] = None, 
                           reason: Optional[str] = None) -> Dict[str, Any]:
        """Request a catalog item.
        
        Args:
            item_id: Catalog item ID
            project_id: Project ID
            inputs: Input parameters
            name: Deployment name
            reason: Request reason
            
        Returns:
            Request response with deployment ID
        """
        data = {
            'item_id': item_id,
            'project_id': project_id,
            'inputs': inputs or {},
            'name': name,
            'reason': reason
        }
        return self._make_request('POST', f'/catalog/items/{item_id}/request', json=data)
    
    def list_deployments(self, project_id: Optional[str] = None,
                        status: Optional[str] = None, 
                        page_size: int = 100, first_page_only: bool = False) -> Dict[str, Any]:
        """List deployments.
        
        Args:
            project_id: Filter by project ID
            status: Filter by status
            page_size: Number of items per page
            first_page_only: Fetch only first page
            
        Returns:
            List of deployments
        """
        params = {
            'page_size': page_size,
            'first_page_only': first_page_only
        }
        if project_id:
            params['project_id'] = project_id
        if status:
            params['status'] = status
        
        return self._make_request('GET', '/deployments', params=params)
    
    def get_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """Get deployment details.
        
        Args:
            deployment_id: Deployment ID
            
        Returns:
            Deployment details
        """
        return self._make_request('GET', f'/deployments/{deployment_id}')
    
    def get_deployment_resources(self, deployment_id: str) -> Dict[str, Any]:
        """Get deployment resources.
        
        Args:
            deployment_id: Deployment ID
            
        Returns:
            Deployment resources
        """
        return self._make_request('GET', f'/deployments/{deployment_id}/resources')
    
    def delete_deployment(self, deployment_id: str, confirm: bool = True) -> Dict[str, Any]:
        """Delete a deployment.
        
        Args:
            deployment_id: Deployment ID
            confirm: Confirm deletion
            
        Returns:
            Deletion response
        """
        params = {'confirm': confirm}
        return self._make_request('DELETE', f'/deployments/{deployment_id}', params=params)


def main():
    """Example usage of the MCP client."""
    
    # Initialize client
    client = VRAMCPClient("http://localhost:8000")
    
    print("🏥 VMware vRA MCP Client Example")
    print("=" * 40)
    
    # Check server health
    print("\n1. Checking server health...")
    try:
        health = client.health_check()
        print(f"✅ Server is {health['status']}")
        print(f"   Version: {health['version']}")
        print(f"   Uptime: {health['uptime']}")
    except Exception as e:
        print(f"❌ Server health check failed: {e}")
        return
    
    # Check authentication status
    print("\n2. Checking authentication status...")
    try:
        auth_status = client.auth_status()
        if auth_status['success']:
            print("✅ Authenticated")
        else:
            print(f"⚠️  Not authenticated: {auth_status['message']}")
            print("\n   To authenticate, use:")
            print("   client.login('username', 'password', 'https://vra-server.com')")
    except Exception as e:
        print(f"❌ Auth status check failed: {e}")
    
    # Example of how to authenticate (commented out for safety)
    """
    print("\\n3. Authenticating...")
    try:
        login_response = client.login(
            username="your-username",
            password="your-password", 
            url="https://your-vra-server.com",
            tenant="your-tenant"
        )
        if login_response['success']:
            print("✅ Authentication successful")
        else:
            print(f"❌ Authentication failed: {login_response['message']}")
    except Exception as e:
        print(f"❌ Login failed: {e}")
    """
    
    # Example of listing catalog items (will fail without authentication)
    print("\n3. Attempting to list catalog items...")
    try:
        catalog_items = client.list_catalog_items(page_size=10, first_page_only=True)
        print(f"✅ Found {len(catalog_items['items'])} catalog items")
        for item in catalog_items['items'][:3]:  # Show first 3
            print(f"   - {item['name']} (ID: {item['id']})")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("⚠️  Unauthorized - authentication required")
        else:
            print(f"❌ Failed to list catalog items: {e}")
    except Exception as e:
        print(f"❌ Error listing catalog items: {e}")
    
    print("\n🎉 Example completed!")
    print("\nNext steps:")
    print("1. Start the MCP server: vra-server")
    print("2. Authenticate with your vRA instance using the login method")
    print("3. Use the client methods to interact with vRA")
    
    print("\nFor more information, see:")
    print("- API Documentation: http://localhost:8000/docs")
    print("- Server Documentation: docs/mcp-server.md")


if __name__ == "__main__":
    main()
