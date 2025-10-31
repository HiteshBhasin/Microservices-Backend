from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from typing import Dict, Any
from abc import ABC

class BaseMCPserver(ABC):
    """Generic base client for connecting to an MCP server."""

    def __init__(self, server_name: str, server_script: str):
        self.server_name = server_name
        self.server_script = server_script
        self.session = None
        self.stdio = None

    async def __aenter__(self):
        params = StdioServerParameters(
            command="python",
            args=[self.server_script]
        )
        self.stdio = stdio_client(params)
        read, write = await self.stdio.__aenter__()

        self.session = ClientSession(read_stream=read, write_stream=write)
        await self.session.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Gracefully close MCP connection."""
        if self.session:
            await self.session.close()
        if self.stdio:
            await self.stdio.__aexit__(exc_type, exc_val, exc_tb)

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool defined on the MCP server."""
        if not self.session:
            raise RuntimeError(f"{self.server_name} service not connected")
        try:
            result = await self.session.call_tool(tool_name, arguments)
            return {"result": result}
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}

    async def list_tools(self):
        """List available tools on the MCP server."""
        if not self.session:
            raise RuntimeError(f"{self.server_name} service not connected")
        return await self.session.list_tools()


class ServiceFactory:
    """Factory to manage and reuse MCP service clients."""
    _instances = {}

    @classmethod
    async def get_service(cls, service_class, *args, **kwargs):
        key = service_class.__name__
        if key not in cls._instances:
            cls._instances[key] = service_class(*args, **kwargs)
        return cls._instances[key]
