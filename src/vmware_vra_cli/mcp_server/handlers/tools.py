"""MCP tools handler for VMware vRA operations."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from ..models.mcp_types import Tool, ToolResult, ErrorCodes
from ...api.catalog import CatalogClient
from ...auth import TokenManager
from ...config import get_config
from ...catalog.schema_registry import SchemaRegistry
from ...catalog.schema_engine import SchemaEngine
from ...catalog.form_builder import FormBuilder


class VraToolsHandler:
    """Handler for VMware vRA MCP tools."""
    
    def __init__(self):
        self._catalog_client = None
        self._schema_registry = None
        self._schema_engine = None
    
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
    
    def _get_schema_registry(self) -> SchemaRegistry:
        """Get or create schema registry with auto-discovery."""
        if self._schema_registry:
            return self._schema_registry
        
        self._schema_registry = SchemaRegistry()
        
        # Auto-discover schema directories
        current_dir = Path.cwd()
        possible_dirs = [
            current_dir / 'inputs' / 'schema_exports',
            current_dir / 'schemas',
            Path.home() / '.vmware-vra-cli' / 'schemas'
        ]
        
        for dir_path in possible_dirs:
            if dir_path.exists():
                self._schema_registry.add_schema_directory(dir_path)
        
        return self._schema_registry
    
    def _get_schema_engine(self) -> SchemaEngine:
        """Get or create schema engine."""
        if not self._schema_engine:
            self._schema_engine = SchemaEngine()
        return self._schema_engine
    
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
            ),
            # Schema Catalog Tools
            Tool(
                name="vra_schema_load_schemas",
                description="Load catalog schemas from JSON files into persistent cache",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string", "default": "*_schema.json", "description": "File pattern to match schema files"},
                        "force_reload": {"type": "boolean", "default": False, "description": "Force reload even if already loaded"}
                    }
                }
            ),
            Tool(
                name="vra_schema_list_schemas",
                description="List available catalog schemas from cache",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "item_type": {"type": "string", "description": "Filter by catalog item type"},
                        "name_filter": {"type": "string", "description": "Filter by name (case-insensitive substring match)"}
                    }
                }
            ),
            Tool(
                name="vra_schema_search_schemas",
                description="Search catalog schemas by name or description",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query (case-insensitive)"}
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="vra_schema_show_schema",
                description="Show detailed schema information for a catalog item",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "catalog_item_id": {"type": "string", "description": "Catalog item ID"}
                    },
                    "required": ["catalog_item_id"]
                }
            ),
            Tool(
                name="vra_schema_execute_schema",
                description="Execute a catalog item using its schema with AI-guided input collection",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "catalog_item_id": {"type": "string", "description": "Catalog item ID"},
                        "project_id": {"type": "string", "description": "vRA project ID"},
                        "deployment_name": {"type": "string", "description": "Custom deployment name (optional)"},
                        "inputs": {"type": "object", "description": "Input values dictionary (optional)"},
                        "dry_run": {"type": "boolean", "default": False, "description": "Validate inputs without executing"}
                    },
                    "required": ["catalog_item_id", "project_id"]
                }
            ),
            Tool(
                name="vra_schema_generate_template",
                description="Generate input template for a catalog item",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "catalog_item_id": {"type": "string", "description": "Catalog item ID"},
                        "project_id": {"type": "string", "description": "vRA project ID"}
                    },
                    "required": ["catalog_item_id", "project_id"]
                }
            ),
            Tool(
                name="vra_schema_clear_cache",
                description="Clear the persistent schema registry cache",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="vra_schema_registry_status",
                description="Show schema registry status and statistics",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            # Reporting Tools
            Tool(
                name="vra_report_activity_timeline",
                description="Generate deployment activity timeline report",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Filter by project ID"},
                        "days_back": {"type": "integer", "default": 30, "minimum": 1, "maximum": 365, "description": "Days back for activity timeline"},
                        "group_by": {"type": "string", "enum": ["day", "week", "month", "year"], "default": "day", "description": "Group results by time period"},
                        "statuses": {"type": "string", "default": "CREATE_SUCCESSFUL,UPDATE_SUCCESSFUL,SUCCESSFUL,CREATE_FAILED,UPDATE_FAILED,FAILED,CREATE_INPROGRESS,UPDATE_INPROGRESS,INPROGRESS", "description": "Comma-separated list of statuses to include"}
                    }
                }
            ),
            Tool(
                name="vra_report_catalog_usage",
                description="Generate catalog usage report with deployment statistics",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Filter by project ID"},
                        "include_zero": {"type": "boolean", "default": False, "description": "Include catalog items with zero deployments"},
                        "sort_by": {"type": "string", "enum": ["deployments", "resources", "name"], "default": "deployments", "description": "Sort results by field"},
                        "detailed_resources": {"type": "boolean", "default": False, "description": "Fetch exact resource counts (slower but more accurate)"}
                    }
                }
            ),
            Tool(
                name="vra_report_resources_usage",
                description="Generate comprehensive resources usage report",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Filter by project ID"},
                        "detailed_resources": {"type": "boolean", "default": True, "description": "Fetch detailed resource information"},
                        "sort_by": {"type": "string", "enum": ["deployment-name", "catalog-item", "resource-count", "status"], "default": "catalog-item", "description": "Sort deployments by field"},
                        "group_by": {"type": "string", "enum": ["catalog-item", "resource-type", "deployment-status"], "default": "catalog-item", "description": "Group results by field"}
                    }
                }
            ),
            Tool(
                name="vra_report_unsync",
                description="Generate report of deployments not linked to catalog items",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Filter by project ID"},
                        "detailed_resources": {"type": "boolean", "default": False, "description": "Fetch exact resource counts (slower but more accurate)"},
                        "reason_filter": {"type": "string", "description": "Filter by specific reason (e.g., missing_catalog_references, catalog_item_deleted)"}
                    }
                }
            ),
            # Workflow Tools
            Tool(
                name="vra_list_workflows",
                description="List available vRealize Orchestrator workflows",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page_size": {"type": "integer", "default": 100, "minimum": 1, "maximum": 2000, "description": "Number of items per page"},
                        "first_page_only": {"type": "boolean", "default": False, "description": "Fetch only the first page"}
                    }
                }
            ),
            Tool(
                name="vra_get_workflow_schema",
                description="Get workflow input/output schema",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string", "description": "Workflow ID"}
                    },
                    "required": ["workflow_id"]
                }
            ),
            Tool(
                name="vra_run_workflow",
                description="Execute a workflow with given inputs",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string", "description": "Workflow ID"},
                        "inputs": {"type": "object", "description": "Input parameters for the workflow"}
                    },
                    "required": ["workflow_id"]
                }
            ),
            Tool(
                name="vra_get_workflow_run",
                description="Get workflow execution details",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string", "description": "Workflow ID"},
                        "execution_id": {"type": "string", "description": "Execution ID"}
                    },
                    "required": ["workflow_id", "execution_id"]
                }
            ),
            Tool(
                name="vra_cancel_workflow_run",
                description="Cancel a running workflow execution",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string", "description": "Workflow ID"},
                        "execution_id": {"type": "string", "description": "Execution ID"}
                    },
                    "required": ["workflow_id", "execution_id"]
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
            # Schema Catalog Tools
            elif name == "vra_schema_load_schemas":
                return await self._handle_schema_load_schemas(arguments)
            elif name == "vra_schema_list_schemas":
                return await self._handle_schema_list_schemas(arguments)
            elif name == "vra_schema_search_schemas":
                return await self._handle_schema_search_schemas(arguments)
            elif name == "vra_schema_show_schema":
                return await self._handle_schema_show_schema(arguments)
            elif name == "vra_schema_execute_schema":
                return await self._handle_schema_execute_schema(arguments)
            elif name == "vra_schema_generate_template":
                return await self._handle_schema_generate_template(arguments)
            elif name == "vra_schema_clear_cache":
                return await self._handle_schema_clear_cache(arguments)
            elif name == "vra_schema_registry_status":
                return await self._handle_schema_registry_status(arguments)
            # Reporting Tools
            elif name == "vra_report_activity_timeline":
                return await self._handle_report_activity_timeline(arguments)
            elif name == "vra_report_catalog_usage":
                return await self._handle_report_catalog_usage(arguments)
            elif name == "vra_report_resources_usage":
                return await self._handle_report_resources_usage(arguments)
            elif name == "vra_report_unsync":
                return await self._handle_report_unsync(arguments)
            # Workflow Tools
            elif name == "vra_list_workflows":
                return await self._handle_list_workflows(arguments)
            elif name == "vra_get_workflow_schema":
                return await self._handle_get_workflow_schema(arguments)
            elif name == "vra_run_workflow":
                return await self._handle_run_workflow(arguments)
            elif name == "vra_get_workflow_run":
                return await self._handle_get_workflow_run(arguments)
            elif name == "vra_cancel_workflow_run":
                return await self._handle_cancel_workflow_run(arguments)
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
    
    # Schema Catalog Handler Methods
    
    async def _handle_schema_load_schemas(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle load schemas request."""
        try:
            registry = self._get_schema_registry()
            pattern = arguments.get("pattern", "*_schema.json")
            force_reload = arguments.get("force_reload", False)
            
            count = registry.load_schemas(pattern=pattern, force_reload=force_reload)
            
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Successfully loaded {count} catalog schemas from persistent cache"
                }]
            )
            
        except Exception as e:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Failed to load schemas: {str(e)}"
                }],
                isError=True
            )
    
    async def _handle_schema_list_schemas(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle list schemas request."""
        try:
            registry = self._get_schema_registry()
            item_type = arguments.get("item_type")
            name_filter = arguments.get("name_filter")
            
            schemas = registry.list_schemas(item_type=item_type, name_filter=name_filter)
            
            if not schemas:
                return ToolResult(
                    content=[{
                        "type": "text",
                        "text": "No schemas found matching criteria. Try loading schemas first with vra_schema_load_schemas."
                    }]
                )
            
            schema_data = []
            for schema in schemas:
                schema_data.append({
                    "id": schema.id,
                    "name": schema.name,
                    "type": schema.type.value if hasattr(schema.type, 'value') else str(schema.type),
                    "description": schema.description
                })
            
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Found {len(schemas)} catalog schemas:\n{json.dumps(schema_data, indent=2)}"
                }]
            )
            
        except Exception as e:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Failed to list schemas: {str(e)}"
                }],
                isError=True
            )
    
    async def _handle_schema_search_schemas(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle search schemas request."""
        try:
            registry = self._get_schema_registry()
            query = arguments["query"]
            
            matches = registry.search_schemas(query)
            
            if not matches:
                return ToolResult(
                    content=[{
                        "type": "text",
                        "text": f"No schemas found matching '{query}'"
                    }]
                )
            
            match_data = []
            for match in matches:
                match_data.append({
                    "id": match.id,
                    "name": match.name,
                    "type": match.type.value if hasattr(match.type, 'value') else str(match.type),
                    "description": match.description
                })
            
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Found {len(matches)} schemas matching '{query}':\n{json.dumps(match_data, indent=2)}"
                }]
            )
            
        except Exception as e:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Failed to search schemas: {str(e)}"
                }],
                isError=True
            )
    
    async def _handle_schema_show_schema(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle show schema request."""
        try:
            registry = self._get_schema_registry()
            engine = self._get_schema_engine()
            catalog_item_id = arguments["catalog_item_id"]
            
            schema = registry.get_schema(catalog_item_id)
            if not schema:
                return ToolResult(
                    content=[{
                        "type": "text",
                        "text": f"Schema not found for catalog item: {catalog_item_id}"
                    }],
                    isError=True
                )
            
            # Get detailed field information
            fields = engine.extract_form_fields(schema)
            
            schema_info = {
                "catalog_item": {
                    "id": schema.catalog_item_info.id,
                    "name": schema.catalog_item_info.name,
                    "type": schema.catalog_item_info.type.value if hasattr(schema.catalog_item_info.type, 'value') else str(schema.catalog_item_info.type),
                    "description": schema.catalog_item_info.description
                },
                "fields": []
            }
            
            for field in fields:
                field_info = {
                    "name": field.name,
                    "title": field.title,
                    "type": field.type,
                    "required": field.required,
                    "description": field.description
                }
                
                if field.choices:
                    field_info["choices"] = field.choices
                
                if field.validation:
                    field_info["validation"] = field.validation
                
                schema_info["fields"].append(field_info)
            
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Schema details for {schema.catalog_item_info.name}:\n{json.dumps(schema_info, indent=2)}"
                }]
            )
            
        except Exception as e:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Failed to show schema: {str(e)}"
                }],
                isError=True
            )
    
    async def _handle_schema_execute_schema(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle execute schema request."""
        try:
            registry = self._get_schema_registry()
            engine = self._get_schema_engine()
            catalog_item_id = arguments["catalog_item_id"]
            project_id = arguments["project_id"]
            deployment_name = arguments.get("deployment_name")
            inputs = arguments.get("inputs", {})
            dry_run = arguments.get("dry_run", False)
            
            # Get schema
            schema = registry.get_schema(catalog_item_id)
            if not schema:
                return ToolResult(
                    content=[{
                        "type": "text",
                        "text": f"Schema not found for catalog item: {catalog_item_id}"
                    }],
                    isError=True
                )
            
            # Validate provided inputs
            validation_result = engine.validate_inputs(schema, inputs)
            
            if not validation_result.valid:
                error_msg = f"Input validation failed:\n" + "\n".join(validation_result.errors)
                return ToolResult(
                    content=[{
                        "type": "text",
                        "text": error_msg
                    }],
                    isError=True
                )
            
            # Generate deployment name if not provided
            if not deployment_name:
                deployment_name = f"mcp-deployment-{schema.catalog_item_info.name.lower().replace(' ', '-').replace('_', '-')}"
            
            if dry_run:
                return ToolResult(
                    content=[{
                        "type": "text",
                        "text": f"DRY RUN - Validation successful for {schema.catalog_item_info.name}\n"
                               f"Deployment: {deployment_name}\n"
                               f"Project: {project_id}\n"
                               f"Inputs: {len(validation_result.processed_inputs)} fields\n"
                               f"Processed inputs: {json.dumps(validation_result.processed_inputs, indent=2)}"
                    }]
                )
            
            # Execute via catalog client
            client = self._get_catalog_client()
            if not client:
                return ToolResult(
                    content=[{
                        "type": "text",
                        "text": "Not authenticated to vRA. Please run vra_authenticate first."
                    }],
                    isError=True
                )
            
            result = client.request_catalog_item(
                catalog_item_id=catalog_item_id,
                inputs=validation_result.processed_inputs,
                project_id=project_id,
                deployment_name=deployment_name
            )
            
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Successfully executed {schema.catalog_item_info.name}\n"
                           f"Deployment ID: {result.get('deploymentId')}\n"
                           f"Request ID: {result.get('id')}\n"
                           f"Deployment Name: {deployment_name}"
                }]
            )
            
        except Exception as e:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Failed to execute schema: {str(e)}"
                }],
                isError=True
            )
    
    async def _handle_schema_generate_template(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle generate template request."""
        try:
            registry = self._get_schema_registry()
            catalog_item_id = arguments["catalog_item_id"]
            project_id = arguments["project_id"]
            
            schema = registry.get_schema(catalog_item_id)
            if not schema:
                return ToolResult(
                    content=[{
                        "type": "text",
                        "text": f"Schema not found for catalog item: {catalog_item_id}"
                    }],
                    isError=True
                )
            
            # Generate template
            template = {
                "_metadata": {
                    "catalog_item_id": catalog_item_id,
                    "catalog_item_name": schema.catalog_item_info.name,
                    "project_id": project_id,
                    "generated_by": "vmware-vra-cli-mcp-server"
                }
            }
            
            # Add field templates
            for field_name, prop in schema.schema_definition.properties.items():
                value = prop.default if prop.default is not None else None
                
                # Add metadata comments
                template[f"_{field_name}_type"] = prop.type
                if prop.description:
                    template[f"_{field_name}_description"] = prop.description
                if field_name in schema.schema_definition.required:
                    template[f"_{field_name}_required"] = True
                
                template[field_name] = value
            
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Input template for {schema.catalog_item_info.name}:\n{json.dumps(template, indent=2)}"
                }]
            )
            
        except Exception as e:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Failed to generate template: {str(e)}"
                }],
                isError=True
            )
    
    async def _handle_schema_clear_cache(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle clear cache request."""
        try:
            registry = self._get_schema_registry()
            registry.clear_cache()
            
            # Clear local cache too
            self._schema_registry = None
            self._schema_engine = None
            
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": "Schema cache cleared successfully"
                }]
            )
            
        except Exception as e:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Failed to clear cache: {str(e)}"
                }],
                isError=True
            )
    
    async def _handle_schema_registry_status(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle registry status request."""
        try:
            registry = self._get_schema_registry()
            
            # Get basic counts
            all_schemas = registry.list_schemas()
            total_schemas = len(all_schemas)
            
            # Count by type
            type_counts = {}
            for schema in all_schemas:
                schema_type = schema.type.value if hasattr(schema.type, 'value') else str(schema.type)
                type_counts[schema_type] = type_counts.get(schema_type, 0) + 1
            
            status_info = {
                "total_schemas": total_schemas,
                "schema_directories": len(registry.schema_dirs),
                "types": type_counts,
                "directories": [str(d) for d in registry.schema_dirs],
                "cache_location": str(registry.cache_file) if hasattr(registry, 'cache_file') else "Unknown"
            }
            
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Schema Registry Status:\n{json.dumps(status_info, indent=2)}"
                }]
            )
            
        except Exception as e:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Failed to get registry status: {str(e)}"
                }],
                isError=True
            )
    
    # Reporting Handler Methods
    
    async def _handle_report_activity_timeline(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle activity timeline report request."""
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
            days_back = arguments.get("days_back", 30)
            group_by = arguments.get("group_by", "day")
            statuses = arguments.get("statuses", "CREATE_SUCCESSFUL,UPDATE_SUCCESSFUL,SUCCESSFUL,CREATE_FAILED,UPDATE_FAILED,FAILED,CREATE_INPROGRESS,UPDATE_INPROGRESS,INPROGRESS")
            
            # Convert status string to list
            include_statuses = [status.strip().upper() for status in statuses.split(',')]
            
            timeline_data = client.get_activity_timeline(
                project_id=project_id,
                days_back=days_back,
                include_statuses=include_statuses,
                group_by=group_by
            )
            
            # Format the response nicely
            summary = timeline_data['summary']
            response_text = f"📈 Activity Timeline Report ({days_back} days, grouped by {group_by})\n\n"
            response_text += f"📊 Summary:\n"
            response_text += f"• Total deployments: {summary['total_deployments']}\n"
            response_text += f"• Successful: {summary['successful_deployments']}\n"
            response_text += f"• Failed: {summary['failed_deployments']}\n"
            response_text += f"• In progress: {summary['in_progress_deployments']}\n"
            response_text += f"• Success rate: {summary['success_rate']}%\n"
            response_text += f"• Trend: {summary['trend']} ({summary['trend_percentage']}%)\n"
            response_text += f"• Peak activity: {summary['peak_activity_period']} ({summary['peak_activity_count']} deployments)\n"
            response_text += f"• Peak hour: {summary['peak_hour']} ({summary['peak_hour_count']} deployments)\n"
            response_text += f"• Unique catalog items: {summary['unique_catalog_items']}\n"
            response_text += f"• Unique projects: {summary['unique_projects']}\n\n"
            
            # Add detailed activity data
            response_text += f"📅 Period Activity:\n"
            for period, data in sorted(timeline_data['period_activity'].items()):
                response_text += f"• {period}: {data['total_deployments']} deployments (✅{data['successful_deployments']} ❌{data['failed_deployments']} ⏳{data['in_progress_deployments']})\n"
            
            response_text += f"\n🔍 Full Data:\n{json.dumps(timeline_data, indent=2)}"
            
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": response_text
                }]
            )
            
        except Exception as e:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Failed to generate activity timeline report: {str(e)}"
                }],
                isError=True
            )
    
    async def _handle_report_catalog_usage(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle catalog usage report request."""
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
            include_zero = arguments.get("include_zero", False)
            sort_by = arguments.get("sort_by", "deployments")
            detailed_resources = arguments.get("detailed_resources", False)
            
            usage_stats = client.get_catalog_usage_stats(
                project_id=project_id,
                fetch_resource_counts=detailed_resources
            )
            
            # Filter out zero deployments unless requested
            if not include_zero:
                usage_stats = [stats for stats in usage_stats if stats['deployment_count'] > 0]
            
            # Sort results
            if sort_by == 'deployments':
                usage_stats.sort(key=lambda x: x['deployment_count'], reverse=True)
            elif sort_by == 'resources':
                usage_stats.sort(key=lambda x: x['resource_count'], reverse=True)
            elif sort_by == 'name':
                usage_stats.sort(key=lambda x: x['catalog_item'].name.lower())
            
            # Get summary statistics
            all_deployments = client.list_deployments(project_id=project_id)
            total_catalog_deployments = sum(stat['deployment_count'] for stat in usage_stats)
            total_catalog_resources = sum(stat['resource_count'] for stat in usage_stats)
            active_items = len([s for s in usage_stats if s['deployment_count'] > 0])
            
            # Format response
            response_text = f"📊 Catalog Usage Report\n\n"
            response_text += f"📈 Summary:\n"
            response_text += f"• Total catalog items shown: {len(usage_stats)}\n"
            response_text += f"• Active items (with deployments): {active_items}\n"
            response_text += f"• Total deployments (system-wide): {len(all_deployments)}\n"
            response_text += f"• Catalog-linked deployments: {total_catalog_deployments}\n"
            response_text += f"• Unlinked deployments: {len(all_deployments) - total_catalog_deployments}\n"
            response_text += f"• Total resources: {total_catalog_resources}\n"
            if active_items > 0:
                avg_deployments = total_catalog_deployments / active_items
                response_text += f"• Average deployments per active item: {avg_deployments:.1f}\n"
            response_text += f"\n📋 Catalog Items (sorted by {sort_by}):\n"
            
            for i, stat in enumerate(usage_stats[:20]):  # Limit to top 20
                item = stat['catalog_item']
                response_text += f"{i+1}. {item.name}\n"
                response_text += f"   • Deployments: {stat['deployment_count']} (✅{stat['success_count']} ❌{stat['failed_count']} ⏳{stat['in_progress_count']})\n"
                response_text += f"   • Resources: {stat['resource_count']}\n"
                response_text += f"   • Success rate: {stat['success_rate']:.1f}%\n"
                response_text += f"   • Type: {item.type.name}\n\n"
            
            if len(usage_stats) > 20:
                response_text += f"... and {len(usage_stats) - 20} more items\n\n"
            
            # Convert to JSON-serializable format for full data
            catalog_items_data = []
            for stat in usage_stats:
                catalog_items_data.append({
                    'id': stat['catalog_item'].id,
                    'name': stat['catalog_item'].name,
                    'type': stat['catalog_item'].type.name,
                    'deployment_count': stat['deployment_count'],
                    'resource_count': stat['resource_count'],
                    'success_count': stat['success_count'],
                    'failed_count': stat['failed_count'],
                    'in_progress_count': stat['in_progress_count'],
                    'success_rate': stat['success_rate'],
                    'status_breakdown': stat['status_counts']
                })
            
            response_text += f"🔍 Full Data:\n{json.dumps(catalog_items_data, indent=2)}"
            
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": response_text
                }]
            )
            
        except Exception as e:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Failed to generate catalog usage report: {str(e)}"
                }],
                isError=True
            )
    
    async def _handle_report_resources_usage(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle resources usage report request."""
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
            detailed_resources = arguments.get("detailed_resources", True)
            sort_by = arguments.get("sort_by", "catalog-item")
            group_by = arguments.get("group_by", "catalog-item")
            
            report_data = client.get_resources_usage_report(
                project_id=project_id,
                include_detailed_resources=detailed_resources
            )
            
            summary = report_data['summary']
            
            # Format response
            response_text = f"🔧 Resources Usage Report\n\n"
            response_text += f"📈 Summary:\n"
            response_text += f"• Total deployments: {summary['total_deployments']}\n"
            response_text += f"• Linked deployments: {summary['linked_deployments']}\n"
            response_text += f"• Unlinked deployments: {summary['unlinked_deployments']}\n"
            response_text += f"• Total resources: {summary['total_resources']}\n"
            response_text += f"• Unique resource types: {summary['unique_resource_types']}\n"
            response_text += f"• Unique catalog items: {summary['unique_catalog_items']}\n"
            if summary['total_deployments'] > 0:
                avg_resources = summary['total_resources'] / summary['total_deployments']
                response_text += f"• Average resources per deployment: {avg_resources:.1f}\n"
            
            # Resource type breakdown
            if summary.get('resource_types'):
                response_text += f"\n🔧 Resource Types:\n"
                sorted_types = sorted(summary['resource_types'].items(), key=lambda x: x[1], reverse=True)
                for resource_type, count in sorted_types[:10]:  # Top 10
                    percentage = (count / summary['total_resources']) * 100 if summary['total_resources'] > 0 else 0
                    response_text += f"• {resource_type}: {count} ({percentage:.1f}%)\n"
            
            # Resource state breakdown
            if summary.get('resource_states'):
                response_text += f"\n📊 Resource States:\n"
                sorted_states = sorted(summary['resource_states'].items(), key=lambda x: x[1], reverse=True)
                for resource_state, count in sorted_states:
                    percentage = (count / summary['total_resources']) * 100 if summary['total_resources'] > 0 else 0
                    response_text += f"• {resource_state}: {count} ({percentage:.1f}%)\n"
            
            response_text += f"\n🔍 Full Report Data:\n{json.dumps(report_data, indent=2)}"
            
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": response_text
                }]
            )
            
        except Exception as e:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Failed to generate resources usage report: {str(e)}"
                }],
                isError=True
            )
    
    async def _handle_report_unsync(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle unsync report request."""
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
            detailed_resources = arguments.get("detailed_resources", False)
            reason_filter = arguments.get("reason_filter")
            
            unsync_data = client.get_unsynced_deployments(
                project_id=project_id,
                fetch_resource_counts=detailed_resources
            )
            
            # Apply reason filter if specified
            if reason_filter:
                filtered_deployments = []
                for unsync in unsync_data['unsynced_deployments']:
                    if unsync['analysis']['primary_reason'] == reason_filter:
                        filtered_deployments.append(unsync)
                
                unsync_data['unsynced_deployments'] = filtered_deployments
                unsync_data['summary']['unsynced_deployments'] = len(filtered_deployments)
                unsync_data['summary']['unsynced_percentage'] = (
                    len(filtered_deployments) / max(unsync_data['summary']['total_deployments'], 1) * 100
                )
            
            summary = unsync_data['summary']
            
            # Format response
            response_text = f"🔍 Unsynced Deployments Report\n\n"
            response_text += f"📊 Summary:\n"
            response_text += f"• Total deployments: {summary['total_deployments']}\n"
            response_text += f"• Linked deployments: {summary['linked_deployments']}\n"
            response_text += f"• ⚠️  Unsynced deployments: {summary['unsynced_deployments']}\n"
            response_text += f"• Unsynced percentage: {summary['unsynced_percentage']:.1f}%\n"
            response_text += f"• Unsynced resources: {summary['total_unsynced_resources']}\n"
            response_text += f"• Total catalog items: {summary['catalog_items_count']}\n"
            
            if reason_filter:
                response_text += f"• 🔎 Filtered by reason: {reason_filter}\n"
            
            # Reason breakdown
            if unsync_data.get('reason_groups'):
                response_text += f"\n🔍 Root Causes:\n"
                for reason, count in sorted(unsync_data['reason_groups'].items(), key=lambda x: x[1], reverse=True):
                    reason_display = reason.replace('_', ' ').title()
                    response_text += f"• {reason_display}: {count}\n"
            
            # Status breakdown
            if unsync_data.get('status_breakdown'):
                response_text += f"\n📈 Status Breakdown:\n"
                for status, count in sorted(unsync_data['status_breakdown'].items(), key=lambda x: x[1], reverse=True):
                    response_text += f"• {status}: {count}\n"
            
            # Sample unsynced deployments
            if unsync_data['unsynced_deployments']:
                response_text += f"\n📋 Sample Unsynced Deployments (first 10):\n"
                for i, unsync in enumerate(unsync_data['unsynced_deployments'][:10]):
                    deployment = unsync['deployment']
                    analysis = unsync['analysis']
                    response_text += f"{i+1}. {deployment.get('name', 'Unknown')} (ID: {deployment.get('id', 'N/A')})\n"
                    response_text += f"   • Status: {deployment.get('status', 'N/A')}\n"
                    response_text += f"   • Resources: {unsync['resource_count']}\n"
                    response_text += f"   • Reason: {analysis['primary_reason'].replace('_', ' ').title()}\n"
                    if analysis.get('suggestions'):
                        response_text += f"   • Suggestion: {analysis['suggestions'][0]}\n"
                    response_text += "\n"
                
                if len(unsync_data['unsynced_deployments']) > 10:
                    remaining = len(unsync_data['unsynced_deployments']) - 10
                    response_text += f"... and {remaining} more unsynced deployments\n"
            else:
                response_text += f"\n✅ No unsynced deployments found! All deployments are properly linked.\n"
            
            response_text += f"\n🔍 Full Data:\n{json.dumps(unsync_data, indent=2)}"
            
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": response_text
                }]
            )
            
        except Exception as e:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Failed to generate unsync report: {str(e)}"
                }],
                isError=True
            )
    
    # Workflow Handler Methods
    
    async def _handle_list_workflows(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle list workflows request."""
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
            page_size = arguments.get("page_size", 100)
            first_page_only = arguments.get("first_page_only", False)
            
            workflows = client.list_workflows(
                page_size=page_size,
                fetch_all=not first_page_only
            )
            
            # Format response
            response_text = f"🔄 Available Workflows\n\n"
            response_text += f"Found {len(workflows)} workflows:\n\n"
            
            for i, workflow in enumerate(workflows[:20]):  # Limit display to first 20
                # Extract workflow info from the link structure
                workflow_id = workflow.get('id', 'N/A')
                workflow_name = workflow.get('name', 'Unknown')
                workflow_description = workflow.get('description', 'No description')
                
                response_text += f"{i+1}. {workflow_name}\n"
                response_text += f"   • ID: {workflow_id}\n"
                response_text += f"   • Description: {workflow_description}\n\n"
            
            if len(workflows) > 20:
                response_text += f"... and {len(workflows) - 20} more workflows\n\n"
            
            response_text += f"🔍 Full Data:\n{json.dumps(workflows, indent=2)}"
            
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": response_text
                }]
            )
            
        except Exception as e:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Failed to list workflows: {str(e)}"
                }],
                isError=True
            )
    
    async def _handle_get_workflow_schema(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle get workflow schema request."""
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
            workflow_id = arguments["workflow_id"]
            schema = client.get_workflow_schema(workflow_id)
            
            # Format the schema nicely
            response_text = f"🔧 Workflow Schema: {workflow_id}\n\n"
            
            if schema.get('name'):
                response_text += f"Name: {schema['name']}\n"
            if schema.get('description'):
                response_text += f"Description: {schema['description']}\n"
            if schema.get('version'):
                response_text += f"Version: {schema['version']}\n"
            
            # Input parameters
            input_params = schema.get('input-parameters', [])
            if input_params:
                response_text += f"\n📥 Input Parameters ({len(input_params)}):\n"
                for param in input_params:
                    param_name = param.get('name', 'Unknown')
                    param_type = param.get('type', 'Unknown')
                    param_desc = param.get('description', 'No description')
                    response_text += f"• {param_name} ({param_type}): {param_desc}\n"
            
            # Output parameters
            output_params = schema.get('output-parameters', [])
            if output_params:
                response_text += f"\n📤 Output Parameters ({len(output_params)}):\n"
                for param in output_params:
                    param_name = param.get('name', 'Unknown')
                    param_type = param.get('type', 'Unknown')
                    param_desc = param.get('description', 'No description')
                    response_text += f"• {param_name} ({param_type}): {param_desc}\n"
            
            response_text += f"\n🔍 Full Schema:\n{json.dumps(schema, indent=2)}"
            
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": response_text
                }]
            )
            
        except Exception as e:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Failed to get workflow schema: {str(e)}"
                }],
                isError=True
            )
    
    async def _handle_run_workflow(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle run workflow request."""
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
            workflow_id = arguments["workflow_id"]
            inputs = arguments.get("inputs", {})
            
            workflow_run = client.run_workflow(workflow_id, inputs)
            
            response_text = f"▶️ Workflow Execution Started\n\n"
            response_text += f"• Workflow ID: {workflow_id}\n"
            response_text += f"• Execution ID: {workflow_run.id}\n"
            response_text += f"• Name: {workflow_run.name}\n"
            response_text += f"• State: {workflow_run.state}\n"
            if workflow_run.start_date:
                response_text += f"• Start Date: {workflow_run.start_date}\n"
            response_text += f"• Input Parameters: {len(inputs)} provided\n\n"
            
            response_text += f"🔍 Execution Details:\n"
            response_text += f"ID: {workflow_run.id}\n"
            response_text += f"State: {workflow_run.state}\n"
            if workflow_run.input_parameters:
                response_text += f"Inputs: {json.dumps(workflow_run.input_parameters, indent=2)}\n"
            
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": response_text
                }]
            )
            
        except Exception as e:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Failed to run workflow: {str(e)}"
                }],
                isError=True
            )
    
    async def _handle_get_workflow_run(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle get workflow run request."""
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
            workflow_id = arguments["workflow_id"]
            execution_id = arguments["execution_id"]
            
            workflow_run = client.get_workflow_run(workflow_id, execution_id)
            
            response_text = f"📊 Workflow Execution Details\n\n"
            response_text += f"• Workflow ID: {workflow_id}\n"
            response_text += f"• Execution ID: {execution_id}\n"
            response_text += f"• Name: {workflow_run.name}\n"
            response_text += f"• State: {workflow_run.state}\n"
            if workflow_run.start_date:
                response_text += f"• Start Date: {workflow_run.start_date}\n"
            if workflow_run.end_date:
                response_text += f"• End Date: {workflow_run.end_date}\n"
            
            # Add state-specific information
            if workflow_run.state == "completed":
                response_text += "\n✅ Workflow completed successfully!\n"
            elif workflow_run.state == "failed":
                response_text += "\n❌ Workflow execution failed.\n"
            elif workflow_run.state == "running":
                response_text += "\n🔄 Workflow is currently running...\n"
            elif workflow_run.state == "canceled":
                response_text += "\n🚫 Workflow execution was canceled.\n"
            
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": response_text
                }]
            )
            
        except Exception as e:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Failed to get workflow run: {str(e)}"
                }],
                isError=True
            )
    
    async def _handle_cancel_workflow_run(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle cancel workflow run request."""
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
            workflow_id = arguments["workflow_id"]
            execution_id = arguments["execution_id"]
            
            result = client.cancel_workflow_run(workflow_id, execution_id)
            
            if result:
                response_text = f"🚫 Workflow Execution Canceled\n\n"
                response_text += f"• Workflow ID: {workflow_id}\n"
                response_text += f"• Execution ID: {execution_id}\n"
                response_text += f"• Status: Cancellation requested\n\n"
                response_text += "ℹ️ The workflow execution has been requested to cancel. "
                response_text += "Check the execution status to confirm cancellation."
            else:
                response_text = f"❌ Failed to cancel workflow execution\n\n"
                response_text += f"• Workflow ID: {workflow_id}\n"
                response_text += f"• Execution ID: {execution_id}\n"
                response_text += "The workflow might already be completed or in a non-cancelable state."
            
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": response_text
                }],
                isError=not result
            )
            
        except Exception as e:
            return ToolResult(
                content=[{
                    "type": "text",
                    "text": f"Failed to cancel workflow run: {str(e)}"
                }],
                isError=True
            )
