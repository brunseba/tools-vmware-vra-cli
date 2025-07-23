"""VMware vRA MCP Server implementation."""

import asyncio
import argparse
import sys
from typing import Any, Dict, Optional, List
from .models.mcp_types import (
    JsonRpcRequest, JsonRpcResponse, JsonRpcNotification,
    InitializeParams, InitializeResult, McpCapabilities, ServerInfo,
    McpMethods, ErrorCodes, Tool, ToolResult, Resource, ResourceContent
)
from .transport import McpTransport
from .transport.stdio import StdioTransport
from .handlers.tools import VraToolsHandler
from .. import __version__


class VraMcpServer:
    """VMware vRA MCP Server."""
    
    def __init__(self):
        self.is_initialized = False
        self.client_capabilities = None
        self.tools_handler = VraToolsHandler()
        self.transport: Optional[McpTransport] = None
    
    async def start(self, transport: McpTransport) -> None:
        """Start the MCP server with the given transport."""
        self.transport = transport
        transport.set_message_handler(self._handle_message)
        await transport.start()
    
    async def stop(self) -> None:
        """Stop the MCP server."""
        if self.transport:
            await self.transport.stop()
    
    async def _handle_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle incoming messages."""
        try:
            # Check if it's a request (has id) or notification (no id)
            if "id" in message:
                return await self._handle_request(message)
            else:
                await self._handle_notification(message)
                return None
        except Exception as e:
            # Return error response for requests
            if "id" in message:
                return {
                    "jsonrpc": "2.0",
                    "id": message["id"],
                    "error": {
                        "code": ErrorCodes.INTERNAL_ERROR,
                        "message": f"Internal error: {str(e)}"
                    }
                }
            return None
    
    async def _handle_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle JSON-RPC requests."""
        try:
            request = JsonRpcRequest(**message)
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "error": {
                    "code": ErrorCodes.INVALID_REQUEST,
                    "message": f"Invalid request: {str(e)}"
                }
            }
        
        method = request.method
        params = request.params or {}
        
        try:
            if method == McpMethods.INITIALIZE:
                result = await self._handle_initialize(params)
            elif method == McpMethods.PING:
                result = {}  # Simple pong response
            elif method == McpMethods.TOOLS_LIST:
                result = await self._handle_tools_list(params)
            elif method == McpMethods.TOOLS_CALL:
                result = await self._handle_tools_call(params)
            elif method == McpMethods.RESOURCES_LIST:
                result = await self._handle_resources_list(params)
            elif method == McpMethods.RESOURCES_READ:
                result = await self._handle_resources_read(params)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request.id,
                    "error": {
                        "code": ErrorCodes.METHOD_NOT_FOUND,
                        "message": f"Method not found: {method}"
                    }
                }
            
            return {
                "jsonrpc": "2.0",
                "id": request.id,
                "result": result
            }
            
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request.id,
                "error": {
                    "code": ErrorCodes.INTERNAL_ERROR,
                    "message": f"Error handling {method}: {str(e)}"
                }
            }
    
    async def _handle_notification(self, message: Dict[str, Any]) -> None:
        """Handle JSON-RPC notifications."""
        try:
            notification = JsonRpcNotification(**message)
            method = notification.method
            params = notification.params or {}
            
            if method == McpMethods.INITIALIZED:
                await self._handle_initialized(params)
            # Add other notification handlers as needed
            
        except Exception as e:
            # Notifications don't return responses, just log errors
            print(f"Error handling notification: {e}", file=sys.stderr)
    
    async def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request."""
        try:
            init_params = InitializeParams(**params)
            self.client_capabilities = init_params.capabilities
            
            # Define server capabilities
            server_capabilities = McpCapabilities(
                tools={},  # We support tools
                resources={"subscribe": True},  # We support resources with subscription
                logging={}  # We support logging
            )
            
            server_info = ServerInfo(
                name="vmware-vra-mcp-server",
                version=__version__
            )
            
            result = InitializeResult(
                protocolVersion="2025-06-18",
                capabilities=server_capabilities,
                serverInfo=server_info
            )
            
            return result.model_dump(exclude_none=True)
            
        except Exception as e:
            raise Exception(f"Initialize failed: {str(e)}")
    
    async def _handle_initialized(self, params: Dict[str, Any]) -> None:
        """Handle initialized notification."""
        self.is_initialized = True
    
    async def _handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request."""
        if not self.is_initialized:
            raise Exception("Server not initialized")
        
        tools = self.tools_handler.get_available_tools()
        return {
            "tools": [tool.model_dump(exclude_none=True) for tool in tools]
        }
    
    async def _handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request."""
        if not self.is_initialized:
            raise Exception("Server not initialized")
        
        name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not name:
            raise Exception("Tool name is required")
        
        result = await self.tools_handler.call_tool(name, arguments)
        return result.model_dump(exclude_none=True)
    
    async def _handle_resources_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/list request."""
        if not self.is_initialized:
            raise Exception("Server not initialized")
        
        # Define available resources
        resources = [
            Resource(
                uri="vra://catalog/items",
                name="VMware vRA Catalog Items",
                description="Access to vRA service catalog items",
                mimeType="application/json"
            ),
            Resource(
                uri="vra://deployments",
                name="VMware vRA Deployments",
                description="Access to vRA deployments",
                mimeType="application/json"
            ),
            Resource(
                uri="vra://config",
                name="VMware vRA Configuration",
                description="Current vRA server configuration",
                mimeType="application/json"
            )
        ]
        
        return {
            "resources": [resource.model_dump(exclude_none=True) for resource in resources]
        }
    
    async def _handle_resources_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/read request."""
        if not self.is_initialized:
            raise Exception("Server not initialized")
        
        uri = params.get("uri")
        if not uri:
            raise Exception("Resource URI is required")
        
        if uri == "vra://catalog/items":
            # Return current catalog items as a resource
            client = self.tools_handler._get_catalog_client()
            if client:
                try:
                    items = client.list_catalog_items(page_size=50, fetch_all=False)
                    items_data = [item.dict() for item in items]
                    content = ResourceContent(
                        uri=uri,
                        mimeType="application/json",
                        text=str(items_data)
                    )
                    return {"contents": [content.model_dump(exclude_none=True)]}
                except Exception as e:
                    content = ResourceContent(
                        uri=uri,
                        mimeType="text/plain",
                        text=f"Error fetching catalog items: {str(e)}"
                    )
                    return {"contents": [content.model_dump(exclude_none=True)]}
            else:
                content = ResourceContent(
                    uri=uri,
                    mimeType="text/plain",
                    text="Not authenticated. Use vra_authenticate tool first."
                )
                return {"contents": [content.model_dump(exclude_none=True)]}
        
        elif uri == "vra://deployments":
            # Return current deployments as a resource
            client = self.tools_handler._get_catalog_client()
            if client:
                try:
                    deployments = client.list_deployments(page_size=50, fetch_all=False)
                    content = ResourceContent(
                        uri=uri,
                        mimeType="application/json",
                        text=str(deployments)
                    )
                    return {"contents": [content.model_dump(exclude_none=True)]}
                except Exception as e:
                    content = ResourceContent(
                        uri=uri,
                        mimeType="text/plain",
                        text=f"Error fetching deployments: {str(e)}"
                    )
                    return {"contents": [content.model_dump(exclude_none=True)]}
            else:
                content = ResourceContent(
                    uri=uri,
                    mimeType="text/plain",
                    text="Not authenticated. Use vra_authenticate tool first."
                )
                return {"contents": [content.model_dump(exclude_none=True)]}
        
        elif uri == "vra://config":
            # Return current configuration as a resource
            try:
                from ...config import get_config
                config = get_config()
                # Remove sensitive information
                safe_config = {k: v for k, v in config.items() if k not in ['password']}
                content = ResourceContent(
                    uri=uri,
                    mimeType="application/json", 
                    text=str(safe_config)
                )
                return {"contents": [content.model_dump(exclude_none=True)]}
            except Exception as e:
                content = ResourceContent(
                    uri=uri,
                    mimeType="text/plain",
                    text=f"Error fetching configuration: {str(e)}"
                )
                return {"contents": [content.model_dump(exclude_none=True)]}
        
        else:
            raise Exception(f"Unknown resource URI: {uri}")


async def run_stdio_server():
    """Run the MCP server with stdio transport."""
    server = VraMcpServer()
    transport = StdioTransport()
    
    try:
        await server.start(transport)
        # Keep the server running
        while transport.is_connected:
            await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        await server.stop()


def main():
    """Main entry point for the MCP server."""
    parser = argparse.ArgumentParser(description="VMware vRA MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio"],
        default="stdio",
        help="Transport method (default: stdio)"
    )
    
    args = parser.parse_args()
    
    if args.transport == "stdio":
        try:
            asyncio.run(run_stdio_server())
        except KeyboardInterrupt:
            print("Server stopped.", file=sys.stderr)
        except Exception as e:
            print(f"Server error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Unsupported transport: {args.transport}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
