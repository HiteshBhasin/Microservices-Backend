from .base_mcp_client import BaseMCPserver, ServiceFactory
from typing import Any, Dict


class ConnecteamService(BaseMCPserver):
    """Client wrapper identifying the Connecteam MCP server script."""

    def __init__(self, server_script: str):
        super().__init__(server_name="connectteam_server", server_script=server_script)


class ConnecteamClient:
    """High-level async client to call Connecteam MCP tools.

    Methods mirror the @mcp.tool() functions in `mcp_server/connectteam_mcp_server.py`.
    """

    def __init__(self, server_path: str = "mcp_server/connectteam_mcp_server.py"):
        self.server_path = server_path

    async def _get_service(self) -> ConnecteamService:
        return await ServiceFactory.get_service(ConnecteamService, self.server_path)

    async def retrieve_tenants(self) -> Dict[str, Any]:
        service = await self._get_service()
        async with service as mcp_service:
            return await mcp_service.call_tool("retrieve_tenants", {})

    async def list_tasks(self, limit: int = 10, offset: int = 0, status: str = "active") -> Dict[str, Any]:
        service = await self._get_service()
        async with service as mcp_service:
            return await mcp_service.call_tool("list_tasks", {"limit": limit, "offset": offset, "status": status})

    async def get_task(self, task_id: str) -> Dict[str, Any]:
        service = await self._get_service()
        async with service as mcp_service:
            return await mcp_service.call_tool("get_task", {"task_id": task_id})

    async def create_task(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        service = await self._get_service()
        async with service as mcp_service:
            return await mcp_service.call_tool("create_task", {"payload": payload})

    async def update_task(self, task_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        service = await self._get_service()
        async with service as mcp_service:
            return await mcp_service.call_tool("update_task", {"task_id": task_id, "payload": payload})

    async def delete_task(self, task_id: str) -> Dict[str, Any]:
        service = await self._get_service()
        async with service as mcp_service:
            return await mcp_service.call_tool("delete_task", {"task_id": task_id})

    async def generate_tasks_report(self, limit: int = 100) -> Dict[str, Any]:
        service = await self._get_service()
        async with service as mcp_service:
            return await mcp_service.call_tool("generate_tasks_report", {"limit": limit})

    async def generate_tasks_report_pdf(self, limit: int = 100, out_path: str = "connecteam_tasks_report.pdf") -> Dict[str, Any]:
        service = await self._get_service()
        async with service as mcp_service:
            return await mcp_service.call_tool("generate_tasks_report_pdf", {"limit": limit, "out_path": out_path})


__all__ = ["ConnecteamService", "ConnecteamClient"]
        