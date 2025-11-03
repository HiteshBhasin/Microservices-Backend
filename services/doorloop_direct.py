import asyncio
from typing import Any, Dict

# This module provides a direct (non-MCP) path to DoorLoop functions by
# calling the helper functions defined in `mcp_server/doorloop_mcp_server.py`.
# We run the blocking functions in a thread so FastAPI's event loop isn't blocked.


def _import_server_module():
    # import here to avoid import-time side-effects earlier in app startup
    from mcp_server import doorloop_mcp_server as dl
    return dl


async def retrieve_tenants() -> Dict[str, Any]:
    dl = _import_server_module()
    return await asyncio.to_thread(dl.retrieve_tenants)


async def retrieve_properties() -> Dict[str, Any]:
    dl = _import_server_module()
    return await asyncio.to_thread(dl.retrieve_properties)


async def retrieve_a_tenants(tenant_id: str) -> Dict[str, Any]:
    dl = _import_server_module()
    return await asyncio.to_thread(dl.retrieve_a_tenants, tenant_id)


async def retrieve_leases() -> Dict[str, Any]:
    dl = _import_server_module()
    return await asyncio.to_thread(dl.retrieve_leases)


async def retrieve_doorloop_communication() -> Dict[str, Any]:
    """Retrieve DoorLoop communications data."""
    dl = _import_server_module()
    return await asyncio.to_thread(dl.retrieve_doorloop_communication)


async def generate_report() -> Dict[str, Any]:
    """Generate DoorLoop balance sheet report."""
    dl = _import_server_module()
    return await asyncio.to_thread(dl.generate_report)


__all__ = [
    "retrieve_tenants",
    "retrieve_properties", 
    "retrieve_a_tenants",
    "retrieve_leases",
    "retrieve_doorloop_communication",
    "generate_report",
]
