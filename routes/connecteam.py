from fastapi import APIRouter, Query, Body, HTTPException, status
from typing import Any, Dict
from enum import Enum
from services import connecteam_api_client
import os

router = APIRouter()

class TaskStatus(str, Enum):
    """Valid task status values for Connecteam API"""
    draft = "draft"
    published = "published" 
    completed = "completed"
    all = "all"


def _unwrap_result(resp: Dict[str, Any]) -> Any:
    """Normalize the client response: raise on 'error', return 'result' if present.

    The HTTP client returns a dict, possibly with {'error': ...}.
    """
    if not isinstance(resp, dict):
        return resp
    if "error" in resp:
        detail = resp.get("error")
        # If the error value is a dict with more info, include it
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)
    if "result" in resp:
        return resp["result"]
    return resp


@router.get("/tenants")
async def get_tenants():
    resp = connecteam_api_client.retrieve_tenants()
    return _unwrap_result(resp)


@router.get("/tasks")
async def get_tasks(
    limit: int = Query(10, ge=1, le=100, description="Number of tasks to return (1-100)"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip for pagination"),
    status: TaskStatus = Query(TaskStatus.all, description="Task status filter"),
):
    """Get tasks from Connecteam with pagination and status filtering."""
    resp = connecteam_api_client.list_tasks(limit=limit, offset=offset, status=status.value)
    return _unwrap_result(resp)


@router.get("/task/{task_id}")
async def get_a_task(task_id: str):
    resp = connecteam_api_client.get_task(task_id)
    return _unwrap_result(resp)


@router.post("/task", status_code=status.HTTP_201_CREATED)
async def create_task(payload: Dict[str, Any] = Body(...)):
    resp = connecteam_api_client.create_task(payload)
    return _unwrap_result(resp)


@router.put("/task/{task_id}")
async def update_task(task_id: str, payload: Dict[str, Any] = Body(...)):
    resp = connecteam_api_client.update_task(task_id, payload)
    return _unwrap_result(resp)


@router.delete("/task/{task_id}")
async def delete_task(task_id: str):
    resp = connecteam_api_client.delete_task(task_id)
    return _unwrap_result(resp)