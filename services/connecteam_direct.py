import asyncio
from typing import Any, Dict


def _import_server_module():
    # import lazily to avoid executing network calls at import time
    from mcp_server import connectteam_mcp_server as ct

    return ct


async def retrieve_tenants() -> Dict[str, Any]:
    ct = _import_server_module()
    return await asyncio.to_thread(ct.retrieve_tenants)


async def list_tasks(limit: int = 10, offset: int = 0, status: str = "active") -> Dict[str, Any]:
    ct = _import_server_module()
    return await asyncio.to_thread(ct.list_tasks, limit, offset, status)


async def get_task(task_id: str) -> Dict[str, Any]:
    ct = _import_server_module()
    return await asyncio.to_thread(ct.get_task, task_id)


async def create_task(payload: Dict[str, Any]) -> Dict[str, Any]:
    ct = _import_server_module()
    return await asyncio.to_thread(ct.create_task, payload)


async def update_task(task_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    ct = _import_server_module()
    return await asyncio.to_thread(ct.update_task, task_id, payload)


async def delete_task(task_id: str) -> Dict[str, Any]:
    ct = _import_server_module()
    return await asyncio.to_thread(ct.delete_task, task_id)


# async def generate_tasks_report(limit: int = 100) -> Dict[str, Any]:
#     ct = _import_server_module()
#     return await asyncio.to_thread(ct.generate_tasks_report, limit)


# async def generate_tasks_report_pdf(limit: int = 100, out_path: str = "connecteam_tasks_report.pdf") -> Dict[str, Any]:
#     ct = _import_server_module()
#     return await asyncio.to_thread(ct.generate_tasks_report_pdf, limit, out_path)


__all__ = [
    "retrieve_tenants",
    "list_tasks",
    "get_task",
    "create_task",
    "update_task",
    "delete_task",
    # "generate_tasks_report",
    # "generate_tasks_report_pdf",
]
