from .base_mcp_client import BaseMCPserver, ServiceFactory
from typing import Any, Dict


class DoorloopService(BaseMCPserver):
    """Concrete service wrapper for the DoorLoop MCP server."""

    def __init__(self, server_script: str):
        # server_name must match whatever you want to identify this service as
        super().__init__(server_name="doorloop_server", server_script=server_script)


class DoorloopClient:
    """High-level async client to call DoorLoop MCP tools.

    This wraps the BaseMCPserver factory and ensures call_tool is invoked
    with an arguments dict (empty when the tool takes no parameters).
    """

    def __init__(self, server_path: str = "mcp_server/doorloop_mcp_server.py"):
        self.server_path = server_path

    async def _get_service(self) -> DoorloopService:
        return await ServiceFactory.get_service(DoorloopService, self.server_path)

    async def retrieve_tenants(self) -> Dict[str, Any]:
        service = await self._get_service()
        async with service as mcp_service:
            return await mcp_service.call_tool("retrieve_tenants", {})

    async def retrieve_properties(self) -> Dict[str, Any]:
        service = await self._get_service()
        async with service as mcp_service:
            return await mcp_service.call_tool("retrieve_properties", {})

    async def retrieve_a_tenants(self, tenant_id: str) -> Dict[str, Any]:
        """Retrieve a single tenant by id via the MCP server."""
        service = await self._get_service()
        async with service as mcp_service:
            return await mcp_service.call_tool("retrieve_a_tenants", {"id": tenant_id})

    async def retrieve_leases(self) -> Dict[str, Any]:
        """Retrieve leases via the MCP server."""
        service = await self._get_service()
        async with service as mcp_service:
            return await mcp_service.call_tool("retrieve_leases", {})

    async def generate_properties_report(self) -> Dict[str, Any]:
        """Generate the properties report (JSON) via the MCP server."""
        service = await self._get_service()
        async with service as mcp_service:
            return await mcp_service.call_tool("generate_properties_report", {})

    async def generate_properties_report_pdf(self, out_path: str = "doorloop_properties_report.pdf") -> Dict[str, Any]:
        service = await self._get_service()
        async with service as mcp_service:
            return await mcp_service.call_tool("generate_properties_report_pdf", {"out_path": out_path})


__all__ = ["DoorloopClient", "DoorloopService"]
        