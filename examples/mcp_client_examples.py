#!/usr/bin/env python3
"""
VMware vRA MCP Client Examples

This module provides practical examples of how to integrate with the
VMware vRA MCP Server using various client patterns.

Examples:
1. Basic MCP Client Setup
2. Complete VM Deployment Workflow
3. Resource Monitoring Dashboard
4. Batch Operations
5. Error Handling Patterns
"""

import asyncio
import json
import subprocess
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional


class SimpleMcpClient:
    """
    A simple MCP client for VMware vRA that demonstrates the basic
    communication patterns with the MCP server.
    """
    
    def __init__(self):
        self.process = None
        self.request_id = 0
    
    async def connect(self):
        """Start the MCP server process and establish communication."""
        try:
            self.process = await asyncio.create_subprocess_exec(
                'vra-mcp-server',
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            print("🔗 Connected to MCP server")
        except FileNotFoundError:
            raise Exception("vra-mcp-server not found. Please ensure it's installed and in PATH.")
    
    def _next_request_id(self) -> int:
        """Generate next request ID."""
        self.request_id += 1
        return self.request_id
    
    async def _send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a JSON-RPC request to the MCP server."""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": method
        }
        if params:
            request["params"] = params
        
        # Send request
        request_json = json.dumps(request) + '\n'
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()
        
        # Read response
        response_line = await self.process.stdout.readline()
        if not response_line:
            raise Exception("No response from MCP server")
        
        return json.loads(response_line.decode())
    
    async def _send_notification(self, method: str, params: Optional[Dict[str, Any]] = None):
        """Send a JSON-RPC notification (no response expected)."""
        notification = {
            "jsonrpc": "2.0",
            "method": method
        }
        if params:
            notification["params"] = params
        
        # Send notification
        notification_json = json.dumps(notification) + '\n'
        self.process.stdin.write(notification_json.encode())
        await self.process.stdin.drain()
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the MCP session."""
        response = await self._send_request("initialize", {
            "protocolVersion": "2025-06-18",
            "capabilities": {"tools": {}, "resources": {}},
            "clientInfo": {"name": "python-mcp-client", "version": "1.0.0"}
        })
        
        if "error" in response:
            raise Exception(f"Initialization failed: {response['error']['message']}")
        
        # Send initialized notification
        await self._send_notification("initialized")
        
        print(f"✅ Initialized with server: {response['result']['serverInfo']['name']}")
        return response["result"]
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """Get available tools from the MCP server."""
        response = await self._send_request("tools/list")
        
        if "error" in response:
            raise Exception(f"Failed to list tools: {response['error']['message']}")
        
        return response["result"]["tools"]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool."""
        response = await self._send_request("tools/call", {
            "name": name,
            "arguments": arguments
        })
        
        if "error" in response:
            raise Exception(f"Tool call failed: {response['error']['message']}")
        
        return response["result"]
    
    async def list_resources(self) -> List[Dict[str, Any]]:
        """Get available resources from the MCP server."""
        response = await self._send_request("resources/list")
        
        if "error" in response:
            raise Exception(f"Failed to list resources: {response['error']['message']}")
        
        return response["result"]["resources"]
    
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a specific resource."""
        response = await self._send_request("resources/read", {"uri": uri})
        
        if "error" in response:
            raise Exception(f"Failed to read resource: {response['error']['message']}")
        
        return response["result"]
    
    async def disconnect(self):
        """Clean up and disconnect from the MCP server."""
        if self.process:
            self.process.stdin.close()
            await self.process.wait()
            print("🔌 Disconnected from MCP server")


class VraWorkflowClient:
    """
    High-level client for common VMware vRA workflows using the MCP server.
    """
    
    def __init__(self):
        self.mcp_client = SimpleMcpClient()
        self.authenticated = False
    
    async def connect(self):
        """Connect to MCP server and initialize."""
        await self.mcp_client.connect()
        await self.mcp_client.initialize()
    
    async def authenticate(self, username: str, password: str, url: str, tenant: str = "vsphere.local"):
        """Authenticate to VMware vRA."""
        result = await self.mcp_client.call_tool("vra_authenticate", {
            "username": username,
            "password": password,
            "url": url,
            "tenant": tenant
        })
        
        if result["isError"]:
            raise Exception(f"Authentication failed: {result['content'][0]['text']}")
        
        self.authenticated = True
        print("✅ Successfully authenticated to vRA")
        return result
    
    async def get_catalog_items(self, project_id: Optional[str] = None, search: Optional[str] = None) -> List[Dict]:
        """Get catalog items with optional filtering."""
        if not self.authenticated:
            raise Exception("Must authenticate first")
        
        params = {"page_size": 100}
        if project_id:
            params["project_id"] = project_id
        if search:
            params["search"] = search
        
        result = await self.mcp_client.call_tool("vra_list_catalog_items", params)
        
        if result["isError"]:
            raise Exception(f"Failed to get catalog items: {result['content'][0]['text']}")
        
        return json.loads(result["content"][0]["text"])
    
    async def get_deployments(self, project_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict]:
        """Get deployments with optional filtering."""
        if not self.authenticated:
            raise Exception("Must authenticate first")
        
        params = {"page_size": 100}
        if project_id:
            params["project_id"] = project_id
        if status:
            params["status"] = status
        
        result = await self.mcp_client.call_tool("vra_list_deployments", params)
        
        if result["isError"]:
            raise Exception(f"Failed to get deployments: {result['content'][0]['text']}")
        
        return json.loads(result["content"][0]["text"])
    
    async def deploy_vm(self, template_name: str, project_id: str, deployment_name: str, 
                      inputs: Dict[str, Any], timeout: int = 600) -> str:
        """Deploy a VM and monitor until completion."""
        if not self.authenticated:
            raise Exception("Must authenticate first")
        
        # Find the catalog item
        catalog_items = await self.get_catalog_items(project_id)
        vm_template = next(
            (item for item in catalog_items if template_name.lower() in item["name"].lower()),
            None
        )
        
        if not vm_template:
            available_items = [item["name"] for item in catalog_items]
            raise Exception(f"VM template '{template_name}' not found. Available: {available_items}")
        
        print(f"📋 Found template: {vm_template['name']}")
        
        # Request the deployment
        result = await self.mcp_client.call_tool("vra_request_catalog_item", {
            "item_id": vm_template["id"],
            "project_id": project_id,
            "name": deployment_name,
            "inputs": inputs,
            "reason": "Deployed via MCP client"
        })
        
        if result["isError"]:
            raise Exception(f"Deployment request failed: {result['content'][0]['text']}")
        
        deployment_info = json.loads(result["content"][0]["text"])
        deployment_id = deployment_info["id"]
        
        print(f"🚀 Deployment requested: {deployment_id}")
        
        # Monitor deployment
        await self._monitor_deployment(deployment_id, timeout)
        
        return deployment_id
    
    async def _monitor_deployment(self, deployment_id: str, timeout: int = 600):
        """Monitor deployment progress."""
        import time
        start_time = time.time()
        last_status = None
        
        while time.time() - start_time < timeout:
            result = await self.mcp_client.call_tool("vra_get_deployment", {
                "deployment_id": deployment_id
            })
            
            if result["isError"]:
                print(f"⚠️ Error checking status: {result['content'][0]['text']}")
                await asyncio.sleep(30)
                continue
            
            deployment = json.loads(result["content"][0]["text"])
            status = deployment["status"]
            
            if status != last_status:
                print(f"📊 Status: {status}")
                last_status = status
            
            if status == "CREATE_SUCCESSFUL":
                print("✅ Deployment completed successfully!")
                
                # Show resources
                resources_result = await self.mcp_client.call_tool("vra_get_deployment_resources", {
                    "deployment_id": deployment_id
                })\n                
                if not resources_result["isError"]:
                    resources = json.loads(resources_result["content"][0]["text"])
                    print(f"📦 Created {len(resources)} resources:")
                    for resource in resources[:5]:  # Show first 5
                        print(f"  • {resource.get('name', 'Unnamed')} ({resource.get('type', 'Unknown type')})")
                
                return
            
            elif status in ["CREATE_FAILED", "DELETE_SUCCESSFUL", "DELETE_FAILED"]:
                raise Exception(f"Deployment failed with status: {status}")
            
            await asyncio.sleep(30)
        
        raise Exception(f"Deployment timeout after {timeout} seconds")
    
    async def delete_deployment(self, deployment_id: str):
        """Delete a deployment."""
        if not self.authenticated:
            raise Exception("Must authenticate first")
        
        result = await self.mcp_client.call_tool("vra_delete_deployment", {
            "deployment_id": deployment_id,
            "confirm": True
        })
        
        if result["isError"]:
            raise Exception(f"Failed to delete deployment: {result['content'][0]['text']}")
        
        print(f"🗑️ Deployment {deployment_id} deletion initiated")
        return result
    
    async def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get a comprehensive dashboard summary."""
        if not self.authenticated:
            raise Exception("Must authenticate first")
        
        # Get current state via resources
        resources = await self.mcp_client.list_resources()
        
        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "resources_available": len(resources)
        }
        
        # Read each resource
        for resource in resources:
            uri = resource["uri"]
            try:
                content = await self.mcp_client.read_resource(uri)
                data = json.loads(content["contents"][0]["text"])
                
                if "catalog" in uri:
                    dashboard["catalog_items"] = len(data)
                    dashboard["catalog_types"] = list(set(item.get("type", "unknown") for item in data))
                
                elif "deployments" in uri:
                    dashboard["total_deployments"] = len(data)
                    status_counts = {}
                    for deployment in data:
                        status = deployment.get("status", "unknown")
                        status_counts[status] = status_counts.get(status, 0) + 1
                    dashboard["deployment_status"] = status_counts
                
                elif "config" in uri:
                    dashboard["server_config"] = {
                        "url": data.get("api_url"),
                        "tenant": data.get("tenant")
                    }
            
            except Exception as e:
                print(f"⚠️ Failed to read resource {uri}: {e}")
        
        return dashboard
    
    async def disconnect(self):
        """Disconnect from the MCP server."""
        await self.mcp_client.disconnect()


# Example usage functions

async def example_basic_connection():
    """Example 1: Basic connection and tool listing."""
    print("🔧 Example 1: Basic Connection")
    print("=" * 50)
    
    client = SimpleMcpClient()
    
    try:
        # Connect and initialize
        await client.connect()
        server_info = await client.initialize()
        
        print(f"Server: {server_info['serverInfo']['name']} v{server_info['serverInfo']['version']}")
        
        # List available tools
        tools = await client.list_tools()
        print(f"📚 Available tools ({len(tools)}):")
        for tool in tools:
            print(f"  • {tool['name']}: {tool['description']}")
        
        # List available resources
        resources = await client.list_resources()
        print(f"📂 Available resources ({len(resources)}):")
        for resource in resources:
            print(f"  • {resource['name']} ({resource['uri']})")
    
    finally:
        await client.disconnect()


async def example_vm_deployment():
    """Example 2: Complete VM deployment workflow."""
    print("🚀 Example 2: VM Deployment")
    print("=" * 50)
    
    # Configuration (replace with your actual values)
    config = {
        "username": "admin@corp.local",
        "password": "password123",  # Use environment variable in production
        "url": "https://vra.example.com",
        "tenant": "corp.local",
        "project_id": "project-12345",
        "template_name": "CentOS",
        "deployment_name": f"test-vm-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "inputs": {
            "cpu": 2,
            "memory": 4096,
            "hostname": "testvm01"
        }
    }
    
    client = VraWorkflowClient()
    
    try:
        await client.connect()
        
        # Authenticate
        await client.authenticate(
            config["username"],
            config["password"],
            config["url"],
            config["tenant"]
        )
        
        # Deploy VM
        deployment_id = await client.deploy_vm(
            config["template_name"],
            config["project_id"],
            config["deployment_name"],
            config["inputs"]
        )
        
        print(f"🎉 VM deployed successfully: {deployment_id}")
        
        # Optional: Clean up (uncomment to delete)
        # print("🧹 Cleaning up...")
        # await client.delete_deployment(deployment_id)
    
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
    
    finally:
        await client.disconnect()


async def example_monitoring_dashboard():
    """Example 3: Resource monitoring dashboard."""
    print("📊 Example 3: Monitoring Dashboard")
    print("=" * 50)
    
    # Configuration
    config = {
        "username": "admin@corp.local",
        "password": "password123",
        "url": "https://vra.example.com",
        "tenant": "corp.local"
    }
    
    client = VraWorkflowClient()
    
    try:
        await client.connect()
        await client.authenticate(
            config["username"],
            config["password"],
            config["url"],
            config["tenant"]
        )
        
        # Get dashboard summary
        dashboard = await client.get_dashboard_summary()
        
        # Print formatted dashboard
        print(f"📈 VMware vRA Dashboard - {dashboard['timestamp']}")
        print("-" * 60)
        
        if "server_config" in dashboard:
            server = dashboard["server_config"]
            print(f"🌐 Server: {server.get('url', 'N/A')}")
            print(f"🏢 Tenant: {server.get('tenant', 'N/A')}")
        
        if "catalog_items" in dashboard:
            print(f"📋 Catalog Items: {dashboard['catalog_items']}")
            if "catalog_types" in dashboard:
                print(f"   Types: {', '.join(dashboard['catalog_types'])}")
        
        if "total_deployments" in dashboard:
            print(f"🚀 Total Deployments: {dashboard['total_deployments']}")
            if "deployment_status" in dashboard:
                print("   Status Breakdown:")
                for status, count in dashboard["deployment_status"].items():
                    print(f"     • {status}: {count}")
        
        print(f"📂 Resources Available: {dashboard['resources_available']}")
    
    except Exception as e:
        print(f"❌ Dashboard failed: {e}")
    
    finally:
        await client.disconnect()


async def example_batch_operations():
    """Example 4: Batch operations and error handling."""
    print("⚡ Example 4: Batch Operations")
    print("=" * 50)
    
    config = {
        "username": "admin@corp.local",
        "password": "password123",
        "url": "https://vra.example.com",
        "tenant": "corp.local",
        "project_id": "project-12345"
    }
    
    client = VraWorkflowClient()
    
    try:
        await client.connect()
        await client.authenticate(
            config["username"],
            config["password"],
            config["url"],
            config["tenant"]
        )
        
        # Batch operation: Get multiple resource types
        print("📦 Fetching multiple resources...")
        
        tasks = [
            client.get_catalog_items(config["project_id"]),
            client.get_deployments(config["project_id"]),
            client.get_deployments(status="CREATE_SUCCESSFUL")
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        catalog_items, all_deployments, successful_deployments = results
        
        # Process results with error handling
        if isinstance(catalog_items, Exception):
            print(f"❌ Failed to get catalog items: {catalog_items}")
        else:
            print(f"📋 Found {len(catalog_items)} catalog items")
        
        if isinstance(all_deployments, Exception):
            print(f"❌ Failed to get deployments: {all_deployments}")
        else:
            print(f"🚀 Found {len(all_deployments)} total deployments")
        
        if isinstance(successful_deployments, Exception):
            print(f"❌ Failed to get successful deployments: {successful_deployments}")
        else:
            print(f"✅ Found {len(successful_deployments)} successful deployments")
    
    except Exception as e:
        print(f"❌ Batch operations failed: {e}")
    
    finally:
        await client.disconnect()


async def main():
    """Run all examples."""
    examples = [
        ("Basic Connection", example_basic_connection),
        ("VM Deployment", example_vm_deployment),
        ("Monitoring Dashboard", example_monitoring_dashboard),
        ("Batch Operations", example_batch_operations)
    ]
    
    print("🎯 VMware vRA MCP Client Examples")
    print("=" * 60)
    print()
    
    if len(sys.argv) > 1:
        # Run specific example
        example_name = sys.argv[1]
        for name, func in examples:
            if example_name.lower() in name.lower():
                await func()
                return
        
        print(f"❌ Example '{example_name}' not found")
        print("Available examples:")
        for name, _ in examples:
            print(f"  • {name}")
        return
    
    # Run all examples
    for i, (name, func) in enumerate(examples, 1):
        print(f"Running example {i}/{len(examples)}: {name}")
        try:
            await func()
        except Exception as e:
            print(f"❌ Example failed: {e}")
        
        print()
        if i < len(examples):
            print("⏳ Waiting 2 seconds before next example...")
            await asyncio.sleep(2)
            print()


if __name__ == "__main__":
    # Usage:
    # python mcp_client_examples.py                    # Run all examples
    # python mcp_client_examples.py "basic"           # Run basic connection example
    # python mcp_client_examples.py "deployment"      # Run VM deployment example
    # python mcp_client_examples.py "dashboard"       # Run dashboard example
    # python mcp_client_examples.py "batch"           # Run batch operations example
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Examples interrupted by user")
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)
