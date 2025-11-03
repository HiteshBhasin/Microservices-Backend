from .base_mcp_client import BaseMCPserver, ServiceFactory
from typing import Any, Dict
import asyncio
import logging
import os

logger = logging.getLogger(__name__)

# Import direct in-process fallback
try:
    from services import connecteam_direct as direct
except Exception:
    try:
        from . import connecteam_direct as direct
    except Exception:
        direct = None

# Read toggle from environment: when USE_DIRECT is falsey (0/false/no) we do NOT use direct fallback
USE_DIRECT = os.getenv("USE_DIRECT", "1").strip().lower() not in ("0", "false", "no")


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

    async def _mcp_call(self, tool_name: str, args: Dict[str, Any]) -> Any:
        service = await self._get_service()
        async with service as mcp_service:
            return await mcp_service.call_tool(tool_name, args)

    async def _call_with_fallback(self, tool_name: str, args: Dict[str, Any], direct_func=None) -> Any:
        try:
            return await asyncio.wait_for(self._mcp_call(tool_name, args), timeout=10)
        except Exception as exc:
            logger.warning("MCP call %s failed; exc=%s; will %s fallback", tool_name, exc, "attempt" if USE_DIRECT else "NOT attempt")
            logger.debug("MCP call exception details", exc_info=True)
            if USE_DIRECT and direct_func and direct is not None:
                try:
                    result = await direct_func()
                except TypeError:
                    result = await direct_func(**args)
                # Log a compact summary of the result for debugging
                try:
                    if isinstance(result, dict):
                        logger.debug("Direct fallback result keys=%s", list(result.keys()))
                    elif isinstance(result, list):
                        logger.debug("Direct fallback result list_len=%d", len(result))
                    else:
                        logger.debug("Direct fallback result type=%s", type(result))
                except Exception:
                    logger.debug("Direct fallback result (unable to summarize)", exc_info=True)
                return result
            raise

    async def retrieve_tenants(self) -> Dict[str, Any]:
        return await self._call_with_fallback("retrieve_tenants", {}, direct_func=(getattr(direct, "retrieve_tenants") if direct else None))

    async def list_tasks(self, limit: int = 10, offset: int = 0, status: str = "all") -> Dict[str, Any]:
        # Note: taskboard_id will be taken from environment variable CONNECTEAM_TASKBOARD_ID in the MCP server
        return await self._call_with_fallback("list_tasks", {"limit": limit, "offset": offset, "status": status}, direct_func=(getattr(direct, "list_tasks") if direct else None))

    async def get_task(self, task_id: str) -> Dict[str, Any]:
        return await self._call_with_fallback("get_task", {"task_id": task_id}, direct_func=(lambda: direct.get_task(task_id) if direct else None))

    async def create_task(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call_with_fallback("create_task", {"payload": payload}, direct_func=(lambda: direct.create_task(payload) if direct else None))

    async def update_task(self, task_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call_with_fallback("update_task", {"task_id": task_id, "payload": payload}, direct_func=(lambda: direct.update_task(task_id, payload) if direct else None))

    async def delete_task(self, task_id: str) -> Dict[str, Any]:
        return await self._call_with_fallback("delete_task", {"task_id": task_id}, direct_func=(lambda: direct.delete_task(task_id) if direct else None))

    # async def generate_tasks_report(self, limit: int = 100) -> Dict[str, Any]:
        # return await self._call_with_fallback("generate_tasks_report", {"limit": limit}, direct_func=(lambda: direct.generate_tasks_report(limit) if direct else None))

    # async def generate_tasks_report_pdf(self, limit: int = 100, out_path: str = "connecteam_tasks_report.pdf") -> Dict[str, Any]:
        # return await self._call_with_fallback("generate_tasks_report_pdf", {"limit": limit, "out_path": out_path}, direct_func=(lambda: direct.generate_tasks_report_pdf(limit, out_path) if direct else None))


__all__ = ["ConnecteamService", "ConnecteamClient"]
        