# Custom MCP Client Development

This guide shows you how to develop custom MCP clients that integrate with the VMware vRA MCP server, enabling you to build specialized applications and tools.

## Overview

The Model Context Protocol (MCP) is a JSON-RPC 2.0 based protocol that enables AI assistants and other clients to interact with external systems through a standardized interface. This guide covers building custom clients for the VMware vRA MCP server.

## Protocol Basics

### Transport Layer
The VMware vRA MCP server uses stdio transport, meaning communication happens through stdin/stdout using JSON-RPC 2.0 messages.

### Message Format
All messages follow JSON-RPC 2.0 specification:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "method_name",
  "params": {
    "parameter": "value"
  }
}
```

## Client Implementation

### Python Client Example

```python
import json
import subprocess
import sys
from typing import Dict, Any, Optional

class VRAMCPClient:
    def __init__(self, server_command: str = "vra-mcp-server"):
        self.server_command = server_command
        self.process = None
        self.request_id = 0
    
    def start_server(self):
        """Start the MCP server process"""
        self.process = subprocess.Popen(
            [self.server_command],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
    
    def stop_server(self):
        """Stop the MCP server process"""
        if self.process:
            self.process.terminate()
            self.process.wait()
    
    def send_request(self, method: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Send a JSON-RPC request to the server"""
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }
        
        # Send request
        request_json = json.dumps(request) + '\n'
        self.process.stdin.write(request_json)
        self.process.stdin.flush()
        
        # Read response
        response_line = self.process.stdout.readline()
        return json.loads(response_line)
    
    def initialize(self) -> Dict[str, Any]:
        """Initialize the MCP server connection"""
        return self.send_request("initialize", {
            "protocolVersion": "2025-06-28",
            "capabilities": {
                "roots": {
                    "listChanged": False
                },
                "sampling": {}
            },
            "clientInfo": {
                "name": "custom-vra-client",
                "version": "1.0.0"
            }
        })
    
    def list_tools(self) -> Dict[str, Any]:
        """Get available tools from the server"""
        return self.send_request("tools/list")
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool with arguments"""
        return self.send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
    
    def __enter__(self):
        self.start_server()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_server()

# Usage Example
def main():
    with VRAMCPClient() as client:
        # Initialize connection
        init_response = client.initialize()
        print("Server initialized:", init_response.get("result", {}).get("serverInfo"))
        
        # List available tools
        tools_response = client.list_tools()
        tools = tools_response.get("result", {}).get("tools", [])
        print(f"Available tools: {len(tools)}")
        
        # Authenticate with vRA
        auth_response = client.call_tool("vra_auth_status", {})
        print("Authentication status:", auth_response)
        
        # List catalog items
        catalog_response = client.call_tool("vra_list_catalog_items", {
            "page_size": 10
        })
        print("Catalog items:", catalog_response)

if __name__ == "__main__":
    main()
```

### JavaScript/Node.js Client Example

```javascript
const { spawn } = require('child_process');
const readline = require('readline');

class VRAMCPClient {
    constructor(serverCommand = 'vra-mcp-server') {
        this.serverCommand = serverCommand;
        this.process = null;
        this.requestId = 0;
        this.pendingRequests = new Map();
    }
    
    async startServer() {
        this.process = spawn(this.serverCommand, [], {
            stdio: ['pipe', 'pipe', 'pipe']
        });
        
        // Set up response handling
        const rl = readline.createInterface({
            input: this.process.stdout,
            output: process.stdout,
            terminal: false
        });
        
        rl.on('line', (line) => {
            try {
                const response = JSON.parse(line);
                const resolve = this.pendingRequests.get(response.id);
                if (resolve) {
                    this.pendingRequests.delete(response.id);
                    resolve(response);
                }
            } catch (error) {
                console.error('Failed to parse response:', error);
            }
        });
    }
    
    stopServer() {
        if (this.process) {
            this.process.kill();
        }
    }
    
    async sendRequest(method, params = {}) {
        this.requestId++;
        const request = {
            jsonrpc: '2.0',
            id: this.requestId,
            method: method,
            params: params
        };
        
        return new Promise((resolve, reject) => {
            this.pendingRequests.set(this.requestId, resolve);
            
            const requestJson = JSON.stringify(request) + '\n';
            this.process.stdin.write(requestJson);
            
            // Set timeout
            setTimeout(() => {
                if (this.pendingRequests.has(this.requestId)) {
                    this.pendingRequests.delete(this.requestId);
                    reject(new Error('Request timeout'));
                }
            }, 30000);
        });
    }
    
    async initialize() {
        return this.sendRequest('initialize', {
            protocolVersion: '2025-06-28',
            capabilities: {
                roots: { listChanged: false },
                sampling: {}
            },
            clientInfo: {
                name: 'custom-vra-js-client',
                version: '1.0.0'
            }
        });
    }
    
    async listTools() {
        return this.sendRequest('tools/list');
    }
    
    async callTool(toolName, arguments) {
        return this.sendRequest('tools/call', {
            name: toolName,
            arguments: arguments
        });
    }
}

// Usage Example
async function main() {
    const client = new VRAMCPClient();
    
    try {
        await client.startServer();
        
        // Initialize connection
        const initResponse = await client.initialize();
        console.log('Server initialized:', initResponse.result.serverInfo);
        
        // List available tools
        const toolsResponse = await client.listTools();
        console.log(`Available tools: ${toolsResponse.result.tools.length}`);
        
        // Check authentication status
        const authResponse = await client.callTool('vra_auth_status', {});
        console.log('Authentication status:', authResponse);
        
        // List deployments
        const deploymentsResponse = await client.callTool('vra_list_deployments', {
            page_size: 5
        });
        console.log('Deployments:', deploymentsResponse);
        
    } catch (error) {
        console.error('Error:', error);
    } finally {
        client.stopServer();
    }
}

main().catch(console.error);
```

### Go Client Example

```go
package main

import (
    "bufio"
    "encoding/json"
    "fmt"
    "os"
    "os/exec"
    "sync"
)

type MCPRequest struct {
    JSONRPC string      `json:"jsonrpc"`
    ID      int         `json:"id"`
    Method  string      `json:"method"`
    Params  interface{} `json:"params"`
}

type MCPResponse struct {
    JSONRPC string      `json:"jsonrpc"`
    ID      int         `json:"id"`
    Result  interface{} `json:"result,omitempty"`
    Error   interface{} `json:"error,omitempty"`
}

type VRAMCPClient struct {
    cmd       *exec.Cmd
    stdin     *bufio.Writer
    stdout    *bufio.Scanner
    requestID int
    mutex     sync.Mutex
}

func NewVRAMCPClient(serverCommand string) *VRAMCPClient {
    return &VRAMCPClient{}
}

func (c *VRAMCPClient) StartServer(serverCommand string) error {
    c.cmd = exec.Command(serverCommand)
    
    // Setup stdin
    stdinPipe, err := c.cmd.StdinPipe()
    if err != nil {
        return err
    }
    c.stdin = bufio.NewWriter(stdinPipe)
    
    // Setup stdout
    stdoutPipe, err := c.cmd.StdoutPipe()
    if err != nil {
        return err
    }
    c.stdout = bufio.NewScanner(stdoutPipe)
    
    // Start the process
    return c.cmd.Start()
}

func (c *VRAMCPClient) StopServer() error {
    if c.cmd != nil {
        return c.cmd.Process.Kill()
    }
    return nil
}

func (c *VRAMCPClient) SendRequest(method string, params interface{}) (*MCPResponse, error) {
    c.mutex.Lock()
    c.requestID++
    id := c.requestID
    c.mutex.Unlock()
    
    request := MCPRequest{
        JSONRPC: "2.0",
        ID:      id,
        Method:  method,
        Params:  params,
    }
    
    // Send request
    requestBytes, err := json.Marshal(request)
    if err != nil {
        return nil, err
    }
    
    _, err = c.stdin.Write(append(requestBytes, '\n'))
    if err != nil {
        return nil, err
    }
    c.stdin.Flush()
    
    // Read response
    if !c.stdout.Scan() {
        return nil, fmt.Errorf("failed to read response")
    }
    
    var response MCPResponse
    err = json.Unmarshal(c.stdout.Bytes(), &response)
    if err != nil {
        return nil, err
    }
    
    return &response, nil
}

func (c *VRAMCPClient) Initialize() (*MCPResponse, error) {
    params := map[string]interface{}{
        "protocolVersion": "2025-06-28",
        "capabilities": map[string]interface{}{
            "roots":    map[string]bool{"listChanged": false},
            "sampling": map[string]interface{}{},
        },
        "clientInfo": map[string]string{
            "name":    "custom-vra-go-client",
            "version": "1.0.0",
        },
    }
    
    return c.SendRequest("initialize", params)
}

func (c *VRAMCPClient) ListTools() (*MCPResponse, error) {
    return c.SendRequest("tools/list", map[string]interface{}{})
}

func (c *VRAMCPClient) CallTool(toolName string, arguments map[string]interface{}) (*MCPResponse, error) {
    params := map[string]interface{}{
        "name":      toolName,
        "arguments": arguments,
    }
    return c.SendRequest("tools/call", params)
}

func main() {
    client := NewVRAMCPClient("vra-mcp-server")
    
    err := client.StartServer("vra-mcp-server")
    if err != nil {
        fmt.Printf("Failed to start server: %v\n", err)
        return
    }
    defer client.StopServer()
    
    // Initialize connection
    initResponse, err := client.Initialize()
    if err != nil {
        fmt.Printf("Failed to initialize: %v\n", err)
        return
    }
    fmt.Printf("Server initialized: %v\n", initResponse.Result)
    
    // List available tools
    toolsResponse, err := client.ListTools()
    if err != nil {
        fmt.Printf("Failed to list tools: %v\n", err)
        return
    }
    fmt.Printf("Tools response: %v\n", toolsResponse.Result)
    
    // Check authentication status
    authResponse, err := client.CallTool("vra_auth_status", map[string]interface{}{})
    if err != nil {
        fmt.Printf("Failed to check auth: %v\n", err)
        return
    }
    fmt.Printf("Auth status: %v\n", authResponse.Result)
}
```

## Available Tools

The VMware vRA MCP server provides 26+ tools across these categories:

### Authentication Tools
- `vra_auth_login` - Authenticate with vRA
- `vra_auth_logout` - Clear stored tokens  
- `vra_auth_status` - Check authentication status
- `vra_auth_refresh` - Refresh access tokens

### Catalog Management Tools
- `vra_list_catalog_items` - List catalog items
- `vra_get_catalog_item` - Get item details
- `vra_get_catalog_item_schema` - Get request schema
- `vra_request_catalog_item` - Request deployment

### Deployment Management Tools  
- `vra_list_deployments` - List deployments
- `vra_get_deployment` - Get deployment details
- `vra_delete_deployment` - Delete deployment
- `vra_get_deployment_resources` - Get resources
- `vra_export_deployments` - Export deployment data

### Reporting Tools
- `vra_report_activity_timeline` - Activity reports
- `vra_report_catalog_usage` - Usage analysis
- `vra_report_resources_usage` - Resource analysis
- `vra_report_unsync` - Unsynced deployments

### Workflow Tools
- `vra_list_workflows` - List vRO workflows
- `vra_get_workflow_schema` - Get workflow schema
- `vra_run_workflow` - Execute workflow
- `vra_get_workflow_run` - Get execution status
- `vra_cancel_workflow_run` - Cancel execution

### Tag Management Tools
- `vra_list_tags` - List available tags
- `vra_create_tag` - Create new tags
- `vra_assign_tag` - Assign tags to resources
- `vra_get_tag_assignments` - Get tag assignments

## Tool Parameter Examples

### Authentication
```json
// vra_auth_login
{
  "username": "admin@corp.local",
  "password": "password",
  "url": "https://vra.company.com",
  "tenant": "corp.local",
  "domain": "vsphere.local"
}

// vra_auth_status - no parameters
{}
```

### Catalog Operations
```json
// vra_list_catalog_items
{
  "project_id": "project-123",
  "page_size": 50,
  "first_page_only": false
}

// vra_request_catalog_item  
{
  "catalog_item_id": "blueprint-ubuntu",
  "project_id": "project-123",
  "name": "my-vm-001",
  "description": "Development VM",
  "inputs": {
    "cpu_count": 2,
    "memory_gb": 4
  }
}
```

### Reporting
```json
// vra_report_activity_timeline
{
  "days_back": 30,
  "group_by": "week",
  "project_id": "project-123"
}

// vra_report_catalog_usage
{
  "include_zero": false,
  "sort_by": "deployments",
  "detailed_resources": true
}
```

## Error Handling

All tools return standardized error responses:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32000,
    "message": "Authentication failed: Invalid credentials",
    "data": {
      "error_type": "AuthenticationError",
      "details": "Token has expired"
    }
  }
}
```

Common error codes:
- `-32000`: Server error (authentication, API errors)
- `-32602`: Invalid params
- `-32601`: Method not found
- `-32700`: Parse error

## Best Practices

### 1. Connection Management
```python
# Always use context managers or try/finally
try:
    client.start_server()
    # Use client
finally:
    client.stop_server()
```

### 2. Error Handling
```python
def safe_tool_call(client, tool_name, arguments):
    try:
        response = client.call_tool(tool_name, arguments)
        if 'error' in response:
            print(f"Tool error: {response['error']['message']}")
            return None
        return response.get('result')
    except Exception as e:
        print(f"Client error: {e}")
        return None
```

### 3. Pagination
```python
def get_all_items(client, tool_name, page_size=100):
    all_items = []
    page = 0
    
    while True:
        response = client.call_tool(tool_name, {
            'page_size': page_size,
            'page': page
        })
        
        if 'error' in response:
            break
            
        items = response.get('result', {}).get('items', [])
        if not items:
            break
            
        all_items.extend(items)
        page += 1
        
    return all_items
```

### 4. Timeout Handling
```python
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Request timed out")

def call_with_timeout(client, tool_name, arguments, timeout=30):
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    
    try:
        result = client.call_tool(tool_name, arguments)
        signal.alarm(0)  # Cancel timeout
        return result
    except TimeoutError:
        print(f"Tool {tool_name} timed out after {timeout}s")
        return None
```

## Use Cases

### 1. Custom Dashboard
Build a web dashboard that shows real-time vRA infrastructure status.

### 2. CI/CD Integration
Integrate vRA provisioning into your deployment pipeline.

### 3. Monitoring & Alerting
Create custom monitoring solutions that track resource usage and deployment health.

### 4. Automation Scripts
Build scripts for bulk operations, maintenance, and governance.

### 5. Integration Platforms
Connect vRA to other enterprise systems (ITSM, CMDB, etc.).

## Testing

### Unit Testing
```python
import unittest
from unittest.mock import Mock, patch

class TestVRAMCPClient(unittest.TestCase):
    def setUp(self):
        self.client = VRAMCPClient()
    
    @patch('subprocess.Popen')
    def test_initialize(self, mock_popen):
        # Mock the server process
        mock_process = Mock()
        mock_process.stdout.readline.return_value = '{"jsonrpc":"2.0","id":1,"result":{"serverInfo":{"name":"test"}}}\n'
        mock_popen.return_value = mock_process
        
        self.client.start_server()
        response = self.client.initialize()
        
        self.assertIn('result', response)
        self.assertIn('serverInfo', response['result'])
```

### Integration Testing
```python
def test_full_workflow():
    with VRAMCPClient() as client:
        # Initialize
        init_response = client.initialize()
        assert init_response.get('result') is not None
        
        # Check auth
        auth_response = client.call_tool('vra_auth_status', {})
        if 'error' in auth_response:
            # Authenticate first
            login_response = client.call_tool('vra_auth_login', {
                'username': 'test_user',
                'password': 'test_pass',
                'url': 'https://vra-test.company.com'
            })
            assert 'result' in login_response
        
        # List catalog items
        catalog_response = client.call_tool('vra_list_catalog_items', {})
        assert 'result' in catalog_response
```

## Deployment

### Docker Container
```dockerfile
FROM python:3.10-slim

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY vra_client.py .

CMD ["python", "vra_client.py"]
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vra-mcp-client
spec:
  replicas: 1
  selector:
    matchLabels:
      app: vra-mcp-client
  template:
    metadata:
      labels:
        app: vra-mcp-client
    spec:
      containers:
      - name: client
        image: vra-mcp-client:latest
        env:
        - name: VRA_URL
          value: "https://vra.company.com"
        - name: VRA_USERNAME
          valueFrom:
            secretKeyRef:
              name: vra-credentials
              key: username
        - name: VRA_PASSWORD
          valueFrom:
            secretKeyRef:
              name: vra-credentials
              key: password
```

## Next Steps

- [MCP Tools Reference](../tools-reference.md)
- [Claude Desktop Integration](claude-desktop.md)
- [VS Code Continue Integration](vscode-continue.md)
- [Advanced Configuration](../setup.md)