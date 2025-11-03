import asyncio
from typing import Any, Dict
import os

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


# async def generate_properties_report() -> Dict[str, Any]:
#     dl = _import_server_module()
#     return await asyncio.to_thread(dl.generate_properties_report)


# async def generate_properties_report_pdf(out_path: str = "doorloop_properties_report.pdf") -> Dict[str, Any]:
#     dl = _import_server_module()
#     # call the module-level function that writes a PDF and returns a dict
#     return await asyncio.to_thread(dl.generate_properties_report_pdf, out_path)


__all__ = [
    "retrieve_tenants",
    "retrieve_properties",
    "retrieve_a_tenants",
    "retrieve_leases",
    # "generate_properties_report",
    # "generate_properties_report_pdf",
]
