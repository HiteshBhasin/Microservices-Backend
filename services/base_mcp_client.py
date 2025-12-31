import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pathlib import Path
import os
import asyncio
from typing import Dict, Any
from abc import ABC
import logging

logger = logging.getLogger(__name__)


class BaseMCPserver(ABC):
    """Simple base client that starts an MCP stdio subprocess and exposes
    helper methods to call tools and list tools.
    """

    def __init__(self, server_name: str, server_script: str):
        self.server_name = server_name
        sp = Path(server_script)
        if not sp.is_absolute():
            repo_root = Path(__file__).resolve().parents[1]
            sp = (repo_root / server_script).resolve()
        self.server_script = str(sp)
        self.session = None
        self.stdio = None

    async def __aenter__(self):
        try:
            params = StdioServerParameters(
                command=sys.executable,
                args=["-u", self.server_script]
            )

            self.stdio = stdio_client(params)
            stdio_transport = await self.stdio.__aenter__()
            self.session = ClientSession(stdio_transport[0], stdio_transport[1])

            await self.session.initialize()
            return self

        except Exception:
            await self.__aexit__(None, None, None)
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.session:
                await self.session.close()
            if self.stdio:
                await self.stdio.__aexit__(exc_type, exc_val, exc_tb)
        except Exception:
            pass

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if not self.session:
            raise RuntimeError(f"{self.server_name} service not connected")
        try:
            result = await self.session.call_tool(tool_name, arguments)
            return {"result": getattr(result, 'content', result)}
        except Exception as e:
            logger.error(f"Tool {tool_name} execution failed: {e}")
            return {"error": str(e)}

    async def list_tools(self):
        if not self.session:
            raise RuntimeError(f"{self.server_name} service not connected")
        try:
            return await self.session.list_tools()
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            return {"error": str(e)}


class ServiceFactory:
    _instances = {}

    @classmethod
    async def get_service(cls, service_cls, server_path: str):
        key = (service_cls.__name__, server_path)
        inst = cls._instances.get(key)
        if inst is None:
            try:
                inst = service_cls(server_path)
            except TypeError:
                try:
                    inst = service_cls(server_script=server_path)
                except TypeError:
                    inst = service_cls()
            cls._instances[key] = inst
        return inst