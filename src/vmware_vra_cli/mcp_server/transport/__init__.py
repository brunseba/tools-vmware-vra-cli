"""MCP transport layer."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable, Awaitable
import json
import asyncio
from ..models.mcp_types import JsonRpcRequest, JsonRpcResponse, JsonRpcNotification


class McpTransport(ABC):
    """Abstract base class for MCP transports."""
    
    def __init__(self):
        self.message_handler: Optional[Callable[[Dict[str, Any]], Awaitable[Optional[Dict[str, Any]]]]] = None
        self.is_connected = False
    
    def set_message_handler(self, handler: Callable[[Dict[str, Any]], Awaitable[Optional[Dict[str, Any]]]]):
        """Set the message handler for incoming messages."""
        self.message_handler = handler
    
    @abstractmethod
    async def start(self) -> None:
        """Start the transport."""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop the transport."""
        pass
    
    @abstractmethod
    async def send_message(self, message: Dict[str, Any]) -> None:
        """Send a message."""
        pass
    
    async def send_response(self, response: JsonRpcResponse) -> None:
        """Send a JSON-RPC response."""
        await self.send_message(response.model_dump(exclude_none=True))
    
    async def send_notification(self, notification: JsonRpcNotification) -> None:
        """Send a JSON-RPC notification."""
        await self.send_message(notification.model_dump(exclude_none=True))
    
    def _parse_message(self, raw_message: str) -> Optional[Dict[str, Any]]:
        """Parse a raw message string into a dictionary."""
        try:
            return json.loads(raw_message)
        except json.JSONDecodeError as e:
            return {
                "error": {
                    "code": -32700,  # Parse error
                    "message": f"Parse error: {str(e)}"
                }
            }
    
    async def _handle_message(self, raw_message: str) -> None:
        """Handle an incoming raw message."""
        if not self.message_handler:
            return
        
        message = self._parse_message(raw_message)
        if not message:
            return
        
        try:
            response = await self.message_handler(message)
            if response:
                await self.send_message(response)
        except Exception as e:
            # Send error response if we have a request ID
            if "id" in message:
                error_response = JsonRpcResponse(
                    id=message["id"],
                    error={
                        "code": -32603,  # Internal error
                        "message": f"Internal error: {str(e)}"
                    }
                )
                await self.send_response(error_response)
