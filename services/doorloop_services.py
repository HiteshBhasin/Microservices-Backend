from .base_mcp_client import BaseMCPserver, ServiceFactory
from typing import Any, Dict
import logging
import asyncio
import os

logger = logging.getLogger(__name__)

# Import direct in-process fallback functions
try:
    from services import doorloop_direct as direct
except Exception:
    try:
        from . import doorloop_direct as direct
    except Exception:
        direct = None

# Read toggle from environment: when USE_DIRECT is falsey (0/false/no) we do NOT use direct fallback
USE_DIRECT = os.getenv("USE_DIRECT", "1").strip().lower() not in ("0", "false", "no")


class DoorloopService(BaseMCPserver):
    """Concrete service wrapper for the DoorLoop MCP server."""
    def __init__(self, server_script: str):
        super().__init__(server_name="doorloop_server", server_script=server_script)


class DoorloopClient:
    """High-level async client to call DoorLoop MCP tools."""
    def __init__(self, server_path: str = "mcp_server/doorloop_mcp_server.py"):
        self.server_path = server_path

    async def _get_service(self) -> DoorloopService:
        if not hasattr(self, "_service"):
            self._service = await ServiceFactory.get_service(DoorloopService, self.server_path)
        return self._service

    async def _mcp_call(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Try to call the MCP tool and return the result dict. Raise on failure."""
        service = await self._get_service()
        async with service as mcp_service:
            return await mcp_service.call_tool(tool_name, args)

    async def _call_with_fallback(self, tool_name: str, args: Dict[str, Any], direct_func=None) -> Dict[str, Any]:
        """Attempt MCP call, fallback to direct in-process function if available.

        Respects the `USE_DIRECT` env toggle. When `USE_DIRECT` is false (0/false/no)
        the method will not attempt the in-process fallback and will raise the
        original MCP exception.
        """
        try:
            return await asyncio.wait_for(self._mcp_call(tool_name, args), timeout=10)
        except Exception as exc:
            # Log full exception (stack trace) to help debugging MCP stdio failures
            logger.warning("MCP call %s failed; exc=%s; will %s fallback", tool_name, exc, "attempt" if USE_DIRECT else "NOT attempt")
            logger.debug("MCP call exception details", exc_info=True)
            if USE_DIRECT and direct_func and direct is not None:
                try:
                    # direct_func is an async function exported by services/doorloop_direct
                    return await direct_func()
                except TypeError:
                    # direct_func may expect args
                    return await direct_func(**args)
            # Re-raise so the caller sees the original failure when fallback disabled
            raise

    async def retrieve_tenants(self) -> Dict[str, Any]:
        return await self._call_with_fallback("retrieve_tenants", {}, direct_func=(getattr(direct, "retrieve_tenants") if direct else None))

    async def retrieve_properties(self) -> Dict[str, Any]:
        return await self._call_with_fallback("retrieve_properties", {}, direct_func=(getattr(direct, "retrieve_properties") if direct else None))

    async def retrieve_a_tenant(self, tenant_id: str) -> Dict[str, Any]:
        return await self._call_with_fallback("retrieve_a_tenant", {"id": tenant_id}, direct_func=(lambda: direct.retrieve_a_tenants(tenant_id) if direct else None))

    async def retrieve_leases(self) -> Dict[str, Any]:
        return await self._call_with_fallback("retrieve_leases", {}, direct_func=(getattr(direct, "retrieve_leases") if direct else None))

    async def generate_properties_report(self) -> Dict[str, Any]:
        return await self._call_with_fallback("generate_properties_report", {}, direct_func=(getattr(direct, "generate_properties_report") if direct else None))

    async def generate_properties_report_pdf(self, out_path: str = "doorloop_properties_report.pdf") -> Dict[str, Any]:
        return await self._call_with_fallback(
            "generate_properties_report_pdf",
            {"out_path": out_path},
            direct_func=(lambda: direct.generate_properties_report_pdf(out_path) if direct else None),
        )


__all__ = ["DoorloopClient", "DoorloopService"]
