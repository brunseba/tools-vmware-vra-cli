"""MCP protocol types and message definitions."""

from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field
from enum import Enum


class JsonRpcVersion(str, Enum):
    """JSON-RPC version."""
    V2_0 = "2.0"


class McpCapabilities(BaseModel):
    """MCP server capabilities."""
    tools: Optional[Dict[str, Any]] = None
    resources: Optional[Dict[str, Any]] = None
    prompts: Optional[Dict[str, Any]] = None
    logging: Optional[Dict[str, Any]] = None


class ServerInfo(BaseModel):
    """MCP server information."""
    name: str
    version: str


class ClientInfo(BaseModel):
    """MCP client information."""
    name: str
    version: str


class InitializeParams(BaseModel):
    """Initialize request parameters."""
    protocolVersion: str
    capabilities: McpCapabilities
    clientInfo: ClientInfo


class InitializeResult(BaseModel):
    """Initialize request result."""
    protocolVersion: str
    capabilities: McpCapabilities
    serverInfo: ServerInfo


class JsonRpcRequest(BaseModel):
    """JSON-RPC request message."""
    jsonrpc: JsonRpcVersion = JsonRpcVersion.V2_0
    id: Union[str, int]
    method: str
    params: Optional[Dict[str, Any]] = None


class JsonRpcResponse(BaseModel):
    """JSON-RPC response message."""
    jsonrpc: JsonRpcVersion = JsonRpcVersion.V2_0
    id: Union[str, int]
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


class JsonRpcNotification(BaseModel):
    """JSON-RPC notification message."""
    jsonrpc: JsonRpcVersion = JsonRpcVersion.V2_0
    method: str
    params: Optional[Dict[str, Any]] = None


class McpError(BaseModel):
    """MCP error information."""
    code: int
    message: str
    data: Optional[Any] = None


class Tool(BaseModel):
    """MCP tool definition."""
    name: str
    description: str
    inputSchema: Dict[str, Any]


class ToolResult(BaseModel):
    """MCP tool execution result."""
    content: List[Dict[str, Any]]
    isError: Optional[bool] = False


class Resource(BaseModel):
    """MCP resource definition."""
    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = None


class ResourceContent(BaseModel):
    """MCP resource content."""
    uri: str
    mimeType: Optional[str] = None
    text: Optional[str] = None
    blob: Optional[str] = None  # Base64 encoded


class Prompt(BaseModel):
    """MCP prompt definition."""
    name: str
    description: Optional[str] = None
    arguments: Optional[List[Dict[str, Any]]] = None


class PromptMessage(BaseModel):
    """MCP prompt message."""
    role: Literal["user", "assistant", "system"]
    content: Dict[str, Any]


class PromptResult(BaseModel):
    """MCP prompt result."""
    description: Optional[str] = None
    messages: List[PromptMessage]


class LogLevel(str, Enum):
    """Log levels."""
    DEBUG = "debug"
    INFO = "info"
    NOTICE = "notice"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    ALERT = "alert"
    EMERGENCY = "emergency"


class LogEntry(BaseModel):
    """Log entry."""
    level: LogLevel
    message: str
    logger: Optional[str] = None


# MCP Method Names
class McpMethods:
    """MCP protocol method names."""
    INITIALIZE = "initialize"
    INITIALIZED = "initialized"
    PING = "ping"
    
    # Tools
    TOOLS_LIST = "tools/list"
    TOOLS_CALL = "tools/call"
    
    # Resources
    RESOURCES_LIST = "resources/list"
    RESOURCES_READ = "resources/read"
    RESOURCES_SUBSCRIBE = "resources/subscribe"
    RESOURCES_UNSUBSCRIBE = "resources/unsubscribe"
    
    # Prompts
    PROMPTS_LIST = "prompts/list"
    PROMPTS_GET = "prompts/get"
    
    # Logging
    LOGGING_SET_LEVEL = "logging/setLevel"
    
    # Notifications
    NOTIFICATIONS_CANCELLED = "notifications/cancelled"
    NOTIFICATIONS_PROGRESS = "notifications/progress"
    NOTIFICATIONS_MESSAGE = "notifications/message"
    NOTIFICATIONS_RESOURCE_UPDATED = "notifications/resources/updated"
    NOTIFICATIONS_RESOURCE_LIST_CHANGED = "notifications/resources/list_changed"
    NOTIFICATIONS_TOOL_LIST_CHANGED = "notifications/tools/list_changed"
    NOTIFICATIONS_PROMPT_LIST_CHANGED = "notifications/prompts/list_changed"


# Error Codes (JSON-RPC and MCP specific)
class ErrorCodes:
    """MCP and JSON-RPC error codes."""
    # JSON-RPC error codes
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    
    # MCP specific error codes
    INVALID_TOOL = -32000
    INVALID_RESOURCE = -32001
    INVALID_PROMPT = -32002
    RESOURCE_NOT_FOUND = -32003
    TOOL_EXECUTION_ERROR = -32004
