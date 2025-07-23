"""MCP tools handler for VMware vRA operations."""

import json
from typing import Any, Dict, List, Optional
from ..models.mcp_types import Tool, ToolResult, ErrorCodes
from ...api.catalog import CatalogClient
from ...auth import TokenManager
from ...config import get_config


class VraToolsHandler:
    """Handler for VMware vRA MCP tools."""
    
    def __init__(self):
        self._catalog_client = None
    
    def _get_catalog_client(self) -> Optional[CatalogClient]:
        """Get or create catalog client with authentication."""
        if self._catalog_client:
            return self._catalog_client
        
        try:
            config = get_config()
            token = TokenManager.get_access_token()
            
            # Try to refresh token if not available
            if not token:
                token = TokenManager.refresh_access_token(
                    config["api_url"], 
                    config["verify_ssl"]
                )
            
            if not token:
                return None
            
            self._catalog_client = CatalogClient(
                base_url=config["api_url"],
                token=token,
                verify_ssl=config["verify_ssl"]
            )
            return self._catalog_client
            
        except Exception:
            return None
    
    def get_available_tools(self) -> List[Tool]:
        """Get list of available MCP tools."""
        return [
            Tool(
                name="vra_authenticate",
                description="Authenticate to VMware vRA server",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "username": {"type": "string", "description": "vRA username"},
                        "password": {"type": "string", "description": "vRA password"},
                        "url": {"type": "string", "description": "vRA server URL"},
                        "tenant": {"type": "string", "description": "vRA tenant (optional)"},
                        "domain": {"type": "string", "description": "vRA domain (optional)"}
                    },
                    "required": ["username", "password", "url"]
                }
            ),
            Tool(
                name="vra_list_catalog_items",
                description="List VMware vRA catalog items",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Filter by project ID"},
                        "page_size": {"type": "integer", "default": 100, "description": "Number of items per page"},
                        "first_page_only": {"type": "boolean", "default": False, "description": "Fetch only first page"}
                    }
                }
            ),
            Tool(
                name="vra_get_catalog_item",
                description="Get details of a specific catalog item",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "item_id": {"type": "string", "description": "Catalog item ID"}
                    },
                    "required": ["item_id"]
                }
            ),
            Tool(
                name="vra_get_catalog_item_schema",
                description="Get request schema for a catalog item",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "item_id": {"type": "string", "description": "Catalog item ID"}
                    },
                    "required": ["item_id"]
                }
            ),
            Tool(
                name="vra_request_catalog_item",
                description="Request a catalog item deployment",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "item_id": {"type": "string", "description": "Catalog item ID"},
                        "project_id": {"type": "string", "description": "Project ID"},
                        "inputs": {"type": "object", "description": "Input parameters for the catalog item"},
                        "reason": {"type": "string", "description": "Reason for the request"},
                        "name": {"type": "string", "description": "Deployment name"}
                    },
                    "required": ["item_id", "project_id"]
                }
            ),
            Tool(
                name="vra_list_deployments",
                description="List VMware vRA deployments",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Filter by project ID"},
                        "status": {"type": "string", "description": "Filter by status"},
                        "page_size": {"type": "integer", "default": 100, "description": "Number of items per page"},
                        "first_page_only": {"type": "boolean", "default": False, "description": "Fetch only first page"}
                    }
                }
            ),
            Tool(
                name="vra_get_deployment",
                description="Get details of a specific deployment",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "deployment_id": {"type": "string", "description": "Deployment ID"}
                    },
                    "required": ["deployment_id"]
                }
            ),
            Tool(
                name="vra_get_deployment_resources",
                description="Get resources of a specific deployment",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "deployment_id": {"type": "string", "description": "Deployment ID"}
                    },
                    "required": ["deployment_id"]
                }
            ),
            Tool(
                name="vra_delete_deployment",
                description="Delete a deployment",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "deployment_id": {"type": "string", "description": "Deployment ID"},
                        "confirm": {"type": "boolean", "default": True, "description": "Confirm deletion"}
                    },
                    "required": ["deployment_id"]
                }
            )
        ]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Execute a tool with given arguments."""
        try:
            if name == "vra_authenticate":
                return await self._handle_authenticate(arguments)
            elif name == "vra_list_catalog_items":
                return await self._handle_list_catalog_items(arguments)
            elif name == "vra_get_catalog_item":
                return await self._handle_get_catalog_item(arguments)
            elif name == "vra_get_catalog_item_schema":
                return await self._handle_get_catalog_item_schema(arguments)
            elif name == "vra_request_catalog_item":
                return await self._handle_request_catalog_item(arguments)
            elif name == "vra_list_deployments":
                return await self._handle_list_deployments(arguments)
            elif name == "vra_get_deployment":
                return await self._handle_get_deployment(arguments)
            elif name == "vra_get_deployment_resources":
                return await self._handle_get_deployment_resources(arguments)
            elif name == "vra_delete_deployment":
                return await self._handle_delete_deployment(arguments)
            else:
                return ToolResult(
                    content=[{
                        "type": "text",
                        "text": f"Unknown tool: {name}"
                    }],
                    isError=True
                )
        except Exception as e:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Tool execution error: {str(e)}"
                }],
                isError=True
            )
    
    async def _handle_authenticate(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle authentication request."""
        try:
            from ...auth import VRAAuthenticator
            from ...config import save_login_config
            
            username = arguments["username"]
            password = arguments["password"]
            url = arguments["url"]
            tenant = arguments.get("tenant")
            domain = arguments.get("domain")
            
            config = get_config()
            authenticator = VRAAuthenticator(url, config["verify_ssl"])
            tokens = authenticator.authenticate(username, password, domain)
            
            # Store tokens securely
            TokenManager.store_tokens(
                tokens['access_token'], 
                tokens['refresh_token']
            )
            
            # Save configuration
            save_login_config(api_url=url, tenant=tenant, domain=domain)
            
            # Clear cached client to force re-authentication
            self._catalog_client = None
            
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Successfully authenticated to {url}"
                }]
            )
            
        except Exception as e:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Authentication failed: {str(e)}"
                }],
                isError=True
            )
    
    async def _handle_list_catalog_items(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle list catalog items request."""
        client = self._get_catalog_client()
        if not client:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": "Not authenticated. Please run vra_authenticate first."
                }],
                isError=True
            )
        
        try:
            project_id = arguments.get("project_id")
            page_size = arguments.get("page_size", 100)
            first_page_only = arguments.get("first_page_only", False)
            
            items = client.list_catalog_items(
                project_id=project_id,
                page_size=page_size,
                fetch_all=not first_page_only
            )
            
            items_data = [item.dict() for item in items]
            
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Found {len(items)} catalog items:\n{json.dumps(items_data, indent=2)}"
                }]
            )
            
        except Exception as e:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Failed to list catalog items: {str(e)}"
                }],
                isError=True
            )
    
    async def _handle_get_catalog_item(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle get catalog item request."""
        client = self._get_catalog_client()
        if not client:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": "Not authenticated. Please run vra_authenticate first."
                }],
                isError=True
            )
        
        try:
            item_id = arguments["item_id"]
            item = client.get_catalog_item(item_id)
            
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Catalog item details:\n{json.dumps(item.dict(), indent=2)}"
                }]
            )
            
        except Exception as e:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Failed to get catalog item: {str(e)}"
                }],
                isError=True
            )
    
    async def _handle_get_catalog_item_schema(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle get catalog item schema request."""
        client = self._get_catalog_client()
        if not client:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": "Not authenticated. Please run vra_authenticate first."
                }],
                isError=True
            )
        
        try:
            item_id = arguments["item_id"]
            schema = client.get_catalog_item_schema(item_id)
            
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Catalog item schema:\n{json.dumps(schema, indent=2)}"
                }]
            )
            
        except Exception as e:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Failed to get catalog item schema: {str(e)}"
                }],
                isError=True
            )
    
    async def _handle_request_catalog_item(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle request catalog item."""
        client = self._get_catalog_client()
        if not client:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": "Not authenticated. Please run vra_authenticate first."
                }],
                isError=True
            )
        
        try:
            item_id = arguments["item_id"]
            project_id = arguments["project_id"]
            inputs = arguments.get("inputs", {})
            reason = arguments.get("reason")
            name = arguments.get("name")
            
            result = client.request_catalog_item(item_id, inputs, project_id, reason)
            
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Catalog item requested successfully:\n{json.dumps(result, indent=2)}"
                }]
            )
            
        except Exception as e:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Failed to request catalog item: {str(e)}"
                }],
                isError=True
            )
    
    async def _handle_list_deployments(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle list deployments request."""
        client = self._get_catalog_client()
        if not client:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": "Not authenticated. Please run vra_authenticate first."
                }],
                isError=True
            )
        
        try:
            project_id = arguments.get("project_id")
            status = arguments.get("status")
            page_size = arguments.get("page_size", 100)
            first_page_only = arguments.get("first_page_only", False)
            
            deployments = client.list_deployments(
                project_id=project_id,
                status=status,
                page_size=page_size,
                fetch_all=not first_page_only
            )
            
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Found {len(deployments)} deployments:\n{json.dumps(deployments, indent=2)}"
                }]
            )
            
        except Exception as e:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Failed to list deployments: {str(e)}"
                }],
                isError=True
            )
    
    async def _handle_get_deployment(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle get deployment request."""
        client = self._get_catalog_client()
        if not client:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": "Not authenticated. Please run vra_authenticate first."
                }],
                isError=True
            )
        
        try:
            deployment_id = arguments["deployment_id"]
            deployment = client.get_deployment(deployment_id)
            
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Deployment details:\n{json.dumps(deployment, indent=2)}"
                }]
            )
            
        except Exception as e:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Failed to get deployment: {str(e)}"
                }],
                isError=True
            )
    
    async def _handle_get_deployment_resources(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle get deployment resources request."""
        client = self._get_catalog_client()
        if not client:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": "Not authenticated. Please run vra_authenticate first."
                }],
                isError=True
            )
        
        try:
            deployment_id = arguments["deployment_id"]
            resources = client.get_deployment_resources(deployment_id)
            
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Deployment resources:\n{json.dumps(resources, indent=2)}"
                }]
            )
            
        except Exception as e:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Failed to get deployment resources: {str(e)}"
                }],
                isError=True
            )
    
    async def _handle_delete_deployment(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle delete deployment request."""
        client = self._get_catalog_client()
        if not client:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": "Not authenticated. Please run vra_authenticate first."
                }],
                isError=True
            )
        
        try:
            deployment_id = arguments["deployment_id"]
            confirm = arguments.get("confirm", True)
            
            if not confirm:
                return ToolResult(
                    content=[{
                        "type": "text",
                        "text": "Deployment deletion cancelled (confirm=false)"
                    }]
                )
            
            result = client.delete_deployment(deployment_id)
            
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Deployment deletion initiated: {deployment_id}"
                }]
            )
            
        except Exception as e:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Failed to delete deployment: {str(e)}"
                }],
                isError=True
            )
