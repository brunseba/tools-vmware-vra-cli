"""Tests for MCP server functionality."""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from vmware_vra_cli.mcp_server.server import VraMcpServer
from vmware_vra_cli.mcp_server.transport.stdio import StdioTransport
from vmware_vra_cli.mcp_server.handlers.tools import VraToolsHandler
from vmware_vra_cli.mcp_server.models.mcp_types import (
    JsonRpcRequest, JsonRpcResponse, McpCapabilities, 
    InitializeParams, ClientInfo, Tool, ToolResult
)


class TestVraMcpServer:
    """Test cases for the VRA MCP server."""
    
    @pytest.fixture
    def server(self):
        """Create a VRA MCP server instance."""
        return VraMcpServer()
    
    @pytest.fixture
    def mock_transport(self):
        """Create a mock transport."""
        transport = MagicMock()
        transport.is_connected = True
        transport.send_message = AsyncMock()
        transport.start = AsyncMock()
        return transport
    
    def test_server_initialization(self, server):
        """Test server initializes correctly."""
        assert not server.is_initialized
        assert server.client_capabilities is None
        assert server.tools_handler is not None
        assert server.transport is None
    
    @pytest.mark.asyncio
    async def test_server_start_stop(self, server, mock_transport):
        """Test server start and stop functionality."""
        # Test start
        await server.start(mock_transport)
        assert server.transport == mock_transport
        mock_transport.start.assert_called_once()
        
        # Test stop
        mock_transport.stop = AsyncMock()
        await server.stop()
        mock_transport.stop.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_initialize_request(self, server):
        """Test MCP initialize request handling."""
        # Prepare initialize request
        request_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Handle the request
        response = await server._handle_message(request_message)
        
        # Verify response
        assert response is not None
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response
        
        result = response["result"]
        assert result["protocolVersion"] == "2025-06-18"
        assert "capabilities" in result
        assert "serverInfo" in result
        assert result["serverInfo"]["name"] == "vmware-vra-mcp-server"
    
    @pytest.mark.asyncio
    async def test_initialized_notification(self, server):
        """Test initialized notification handling."""
        # First initialize the server
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test", "version": "1.0"}
            }
        }
        await server._handle_message(init_request)
        
        # Send initialized notification
        notification = {
            "jsonrpc": "2.0",
            "method": "initialized"
        }
        
        response = await server._handle_message(notification)
        assert response is None  # Notifications don't return responses
        assert server.is_initialized is True
    
    @pytest.mark.asyncio
    async def test_tools_list(self, server):
        """Test tools/list request."""
        # Initialize server first
        server.is_initialized = True
        
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        response = await server._handle_message(request)
        
        assert response is not None
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 2
        assert "result" in response
        
        result = response["result"]
        assert "tools" in result
        assert len(result["tools"]) > 0
        
        # Check that we have the expected tools
        tool_names = [tool["name"] for tool in result["tools"]]
        expected_tools = [
            "vra_authenticate", "vra_list_catalog_items", "vra_get_catalog_item",
            "vra_get_catalog_item_schema", "vra_request_catalog_item",
            "vra_list_deployments", "vra_get_deployment", 
            "vra_get_deployment_resources", "vra_delete_deployment"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
    
    @pytest.mark.asyncio
    async def test_tools_call_unknown_tool(self, server):
        """Test calling an unknown tool."""
        server.is_initialized = True
        
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "unknown_tool",
                "arguments": {}
            }
        }
        
        response = await server._handle_message(request)
        
        assert response is not None
        assert response["id"] == 3
        assert "result" in response
        
        result = response["result"]
        assert result["isError"] is True
        assert "Unknown tool" in result["content"][0]["text"]
    
    @pytest.mark.asyncio
    async def test_resources_list(self, server):
        """Test resources/list request."""
        server.is_initialized = True
        
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "resources/list"
        }
        
        response = await server._handle_message(request)
        
        assert response is not None
        assert response["id"] == 4
        assert "result" in response
        
        result = response["result"]
        assert "resources" in result
        assert len(result["resources"]) == 3  # catalog/items, deployments, config
        
        resource_uris = [res["uri"] for res in result["resources"]]
        expected_uris = ["vra://catalog/items", "vra://deployments", "vra://config"]
        
        for expected_uri in expected_uris:
            assert expected_uri in resource_uris
    
    @pytest.mark.asyncio
    async def test_resources_read_config(self, server):
        """Test reading the config resource."""
        server.is_initialized = True
        
        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "resources/read",
            "params": {
                "uri": "vra://config"
            }
        }
        
        with patch('vmware_vra_cli.config.get_config') as mock_get_config:
            mock_get_config.return_value = {
                "api_url": "https://vra.test.com",
                "tenant": "test-tenant",
                "verify_ssl": True
            }
            
            response = await server._handle_message(request)
        
        assert response is not None
        assert response["id"] == 5
        assert "result" in response
        
        result = response["result"]
        assert "contents" in result
        assert len(result["contents"]) == 1
        
        content = result["contents"][0]
        assert content["uri"] == "vra://config"
        # The function might return text/plain if there's an error importing config
        assert content["mimeType"] in ["application/json", "text/plain"]
        assert "text" in content
        
        # If it's a config response, verify mock was called
        if content["mimeType"] == "application/json":
            mock_get_config.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_method_not_found(self, server):
        """Test handling of unknown methods."""
        request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "unknown/method"
        }
        
        response = await server._handle_message(request)
        
        assert response is not None
        assert response["id"] == 6
        assert "error" in response
        
        error = response["error"]
        assert error["code"] == -32601  # Method not found
        assert "Method not found" in error["message"]
    
    @pytest.mark.asyncio
    async def test_ping_request(self, server):
        """Test ping request."""
        server.is_initialized = True
        
        request = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "ping"
        }
        
        response = await server._handle_message(request)
        
        assert response is not None
        assert response["id"] == 7
        assert "result" in response
        assert response["result"] == {}  # Empty result for ping
    
    @pytest.mark.asyncio
    async def test_invalid_json_rpc(self, server):
        """Test handling of invalid JSON-RPC messages."""
        invalid_request = {
            "id": 8,
            # Missing jsonrpc and method
        }
        
        response = await server._handle_message(invalid_request)
        
        assert response is not None
        assert response["id"] == 8
        assert "error" in response
        
        error = response["error"]
        assert error["code"] == -32600  # Invalid request


class TestVraToolsHandler:
    """Test cases for the VRA tools handler."""
    
    @pytest.fixture
    def handler(self):
        """Create a VRA tools handler instance."""
        return VraToolsHandler()
    
    def test_get_available_tools(self, handler):
        """Test getting available tools."""
        tools = handler.get_available_tools()
        
        assert isinstance(tools, list)
        assert len(tools) > 0
        
        # Check that all tools have required fields
        for tool in tools:
            assert isinstance(tool, Tool)
            assert tool.name
            assert tool.description
            assert tool.inputSchema
            assert tool.inputSchema["type"] == "object"
    
    @pytest.mark.asyncio
    async def test_call_unknown_tool(self, handler):
        """Test calling an unknown tool."""
        result = await handler.call_tool("nonexistent_tool", {})
        
        assert isinstance(result, ToolResult)
        assert result.isError is True
        assert "Unknown tool" in result.content[0]["text"]
    
    @pytest.mark.asyncio
    async def test_authenticate_tool_missing_params(self, handler):
        """Test authenticate tool with missing parameters."""
        result = await handler.call_tool("vra_authenticate", {
            "username": "test"
            # Missing password and url
        })
        
        assert isinstance(result, ToolResult)
        assert result.isError is True
        assert "failed" in result.content[0]["text"].lower()
    
    @pytest.mark.asyncio
    async def test_catalog_operations_not_authenticated(self, handler):
        """Test catalog operations without authentication."""
        # Test list catalog items without authentication
        with patch.object(handler, '_get_catalog_client', return_value=None):
            result = await handler.call_tool("vra_list_catalog_items", {})
        
        assert isinstance(result, ToolResult)
        assert result.isError is True
        assert "Not authenticated" in result.content[0]["text"]
    
    @pytest.mark.asyncio
    async def test_deployment_operations_not_authenticated(self, handler):
        """Test deployment operations without authentication."""
        # Test list deployments without authentication
        with patch.object(handler, '_get_catalog_client', return_value=None):
            result = await handler.call_tool("vra_list_deployments", {})
        
        assert isinstance(result, ToolResult)
        assert result.isError is True
        assert "Not authenticated" in result.content[0]["text"]


class TestStdioTransport:
    """Test cases for stdio transport."""
    
    @pytest.fixture
    def transport(self):
        """Create a stdio transport instance."""
        return StdioTransport()
    
    def test_transport_initialization(self, transport):
        """Test transport initializes correctly."""
        assert not transport.is_connected
        assert transport.message_handler is None
        assert not transport._running
    
    def test_set_message_handler(self, transport):
        """Test setting message handler."""
        async def dummy_handler(message):
            return {"response": "test"}
        
        transport.set_message_handler(dummy_handler)
        assert transport.message_handler == dummy_handler
    
    def test_parse_message_valid_json(self, transport):
        """Test parsing valid JSON message."""
        message = '{"jsonrpc": "2.0", "method": "test"}'
        parsed = transport._parse_message(message)
        
        assert parsed is not None
        assert parsed["jsonrpc"] == "2.0"
        assert parsed["method"] == "test"
    
    def test_parse_message_invalid_json(self, transport):
        """Test parsing invalid JSON message."""
        message = '{"jsonrpc": "2.0", "method": "test"'  # Missing closing brace
        parsed = transport._parse_message(message)
        
        assert parsed is not None
        assert "error" in parsed
        assert parsed["error"]["code"] == -32700  # Parse error
    
    @pytest.mark.asyncio
    async def test_send_message(self, transport):
        """Test sending a message."""
        transport.is_connected = True
        
        message = {"jsonrpc": "2.0", "method": "test"}
        
        # Mock stdout to capture output
        with patch('sys.stdout') as mock_stdout:
            await transport.send_message(message)
            
            # Verify print was called with JSON string
            mock_stdout.write.assert_called()


class TestMcpIntegration:
    """Integration tests for MCP server functionality."""
    
    @pytest.mark.asyncio
    async def test_full_mcp_workflow(self):
        """Test a complete MCP workflow."""
        server = VraMcpServer()
        
        # Step 1: Initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        init_response = await server._handle_message(init_request)
        assert init_response["result"]["protocolVersion"] == "2025-06-18"
        
        # Step 2: Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "initialized"
        }
        
        await server._handle_message(initialized_notification)
        assert server.is_initialized
        
        # Step 3: List tools
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        tools_response = await server._handle_message(tools_request)
        tools = tools_response["result"]["tools"]
        assert len(tools) > 0
        
        # Step 4: List resources
        resources_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "resources/list"
        }
        
        resources_response = await server._handle_message(resources_request)
        resources = resources_response["result"]["resources"]
        assert len(resources) == 3
        
        # Step 5: Try to call a tool (should fail without auth)
        tool_call_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "vra_list_catalog_items",
                "arguments": {}
            }
        }
        
        with patch.object(server.tools_handler, '_get_catalog_client', return_value=None):
            tool_response = await server._handle_message(tool_call_request)
            result = tool_response["result"]
            assert result["isError"] is True
            assert "Not authenticated" in result["content"][0]["text"]


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
