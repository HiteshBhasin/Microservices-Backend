import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pathlib import Path
import os
from mcp.types import CallToolRequest, ListToolsRequest, CallToolRequestParams
import asyncio
from typing import Dict, Any
from abc import ABC
import logging

logger = logging.getLogger(__name__)

class BaseMCPserver(ABC):
    """Generic base client for connecting to an MCP server."""

    def __init__(self, server_name: str, server_script: str):
        self.server_name = server_name
        # Resolve server script to an absolute path relative to repo root if needed
        sp = Path(server_script)
        if not sp.is_absolute():
            repo_root = Path(__file__).resolve().parents[1]
            sp = (repo_root / server_script).resolve()
        self.server_script = str(sp)
        self.session = None
        self.stdio = None

    async def __aenter__(self):
        try:
            # Create server parameters
            # Use the same Python executable running this process so subprocess
            # has the same environment/packages as the main app (avoids 'python'
            # resolving to a different interpreter without MCP installed).
            # Use unbuffered stdout/stderr (-u) so JSON messages aren't delayed by
            # stdio buffering. Provide the absolute script path to avoid cwd issues.
            params = StdioServerParameters(
                command=sys.executable,
                args=["-u", self.server_script]
            )
            
            # Create stdio client and connect
            self.stdio = stdio_client(params)
            stdio_transport = await self.stdio.__aenter__()
            
            # Create session
            self.session = ClientSession(stdio_transport[0], stdio_transport[1])
            
            # Initialize the session - THIS IS THE MISSING STEP!
            # initialize can hang if the child process doesn't start correctly;
            # wrap in a short timeout so we fail fast and can log helpful info.
            try:
                init_result = await asyncio.wait_for(self.session.initialize(), timeout=8)
                logger.info(f"Initialized MCP session: {init_result}")
            except asyncio.TimeoutError:
                logger.error("Timed out waiting for MCP session.initialize(); check that the MCP server script runs correctly and does not exit immediately.")
                raise
            
            return self
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP server: {e}")
            await self.__aexit__(None, None, None)
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Gracefully close MCP connection."""
        try:
            if self.session:
                await self.session.close()
            if self.stdio:
                await self.stdio.__aexit__(exc_type, exc_val, exc_tb)
        except Exception as e:
            logger.error(f"Error closing MCP connection: {e}")

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool defined on the MCP server."""
        if not self.session:
            raise RuntimeError(f"{self.server_name} service not connected")
        
        try:
            # Use the proper MCP tool calling method
            result = await self.session.call_tool(tool_name, arguments)
            
            if hasattr(result, 'content'):
                return {"result": result.content}
            else:
                return {"result": result}
                
        except Exception as e:
            logger.error(f"Tool {tool_name} execution failed: {e}")
            return {"error": f"Tool execution failed: {str(e)}"}

    async def list_tools(self):
        """List available tools on the MCP server."""
        if not self.session:
            raise RuntimeError(f"{self.server_name} service not connected")
        
        try:
            result = await self.session.list_tools()
            return result
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            return {"error": str(e)}


class ServiceFactory:
    """Simple factory/cache for MCP service wrapper instances.

    This avoids repeatedly re-creating service wrapper objects and provides a
    central place to obtain a service instance for a given server script.
    """

    _instances = {}

    @classmethod
    async def get_service(cls, service_cls, server_path: str):
        key = (service_cls.__name__, server_path)
        inst = cls._instances.get(key)
        if inst is None:
            # Try common constructor signatures
            try:
                inst = service_cls(server_path)
            except TypeError:
                try:
                    inst = service_cls(server_script=server_path)
                except TypeError:
                    # Fallback: try without args
                    inst = service_cls()
            cls._instances[key] = inst
        return inst