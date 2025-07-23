"""Standard I/O transport for MCP server."""

import sys
import json
import asyncio
from typing import Any, Dict
from . import McpTransport


class StdioTransport(McpTransport):
    """Standard I/O transport implementation."""
    
    def __init__(self):
        super().__init__()
        self._running = False
        self._read_task = None
    
    async def start(self) -> None:
        """Start reading from stdin."""
        self.is_connected = True
        self._running = True
        self._read_task = asyncio.create_task(self._read_loop())
    
    async def stop(self) -> None:
        """Stop the transport."""
        self._running = False
        self.is_connected = False
        if self._read_task:
            self._read_task.cancel()
            try:
                await self._read_task
            except asyncio.CancelledError:
                pass
    
    async def send_message(self, message: Dict[str, Any]) -> None:
        """Send a message to stdout."""
        if not self.is_connected:
            return
        
        try:
            json_str = json.dumps(message, separators=(',', ':'))
            print(json_str, file=sys.stdout, flush=True)
        except Exception as e:
            # Log error but don't raise - we don't want to crash the server
            print(f"Error sending message: {e}", file=sys.stderr)
    
    async def _read_loop(self) -> None:
        """Read messages from stdin in a loop."""
        try:
            # Use asyncio to read from stdin without blocking
            reader = asyncio.StreamReader()
            protocol = asyncio.StreamReaderProtocol(reader)
            transport, _ = await asyncio.get_event_loop().connect_read_pipe(
                lambda: protocol, sys.stdin
            )
            
            while self._running:
                try:
                    # Read line from stdin
                    line = await reader.readline()
                    if not line:
                        # EOF reached
                        break
                    
                    line_str = line.decode('utf-8').strip()
                    if line_str:
                        await self._handle_message(line_str)
                        
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    print(f"Error reading message: {e}", file=sys.stderr)
                    continue
            
            transport.close()
            
        except Exception as e:
            print(f"Error in read loop: {e}", file=sys.stderr)
        finally:
            self._running = False
            self.is_connected = False
