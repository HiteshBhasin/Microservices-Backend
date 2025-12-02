from fastapi import APIRouter, Query, Body, HTTPException, status
from typing import Any, Dict
from enum import Enum
from services import connecteam_api_client
import os, logging

router = APIRouter()

class TaskStatus(str, Enum):
    """Valid task status values for Connecteam API"""
    draft = "draft"
    published = "published" 
    completed = "completed"
    all = "all"

try:
    from services import connecteam_service as services
except Exception as e:
    logging.exception("No Mcp services came through")

    

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
 try:
    resp = connecteam_api_client.retrieve_tenants()
    return _unwrap_result(resp)
 except(ConnectionError, TimeoutError, ValueError) as e:
    logging.warning(f"Primary Connecteam API failed: {e}")
    logging.info("Trying fallback service...")
    try:
        retrieve_tenants = services.ConnecteamClient()
        tenants_info = retrieve_tenants.retrieve_tenants()
        if isinstance(tenants_info, dict):
            return _unwrap_result(tenants_info)
    except HTTPException as e:
        logging.exception("an error occur the retrieve_tenants server is down. check connecteam_service")
        
        


@router.get("/tasks")
async def get_tasks(
    limit: int = Query(10, ge=1, le=100, description="Number of tasks to return (1-100)"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip for pagination"),
    status: TaskStatus = Query(TaskStatus.all, description="Task status filter"),
):
    try:
        """Get tasks from Connecteam with pagination and status filtering."""
        resp = connecteam_api_client.list_tasks(limit=limit, offset=offset, status=status.value)
        return _unwrap_result(resp)
    except (ConnectionError, TimeoutError, ValueError) as e:
        logging.warning(f"Primary Connecteam API failed: {e}")
        logging.info("Trying fallback service...")
        
        try:
            list_task = services.ConnecteamClient()
            tasks_info = await list_task.list_tasks(limit=limit,offset= offset, status= status)
            if isinstance(tasks_info, dict):
                return _unwrap_result(tasks_info)
        except HTTPException as e:
            logging.exception("an error occur the tasks_info server is down {e}. check connecteam_service")
            
                


@router.get("/task/{task_id}")
async def get_a_task(task_id: str):
    try:
        resp = connecteam_api_client.get_task(task_id)
        return _unwrap_result(resp)
    except(ConnectionError, TimeoutError, ValueError) as e:
        logging.warning(f"Primary Connecteam API failed: {e}")
        logging.info("Trying fallback service...")
        try:
            get_task = services.ConnecteamClient()
            task_info = await get_task.get_task(task_id=task_id)
            if isinstance(task_info, dict):
                return _unwrap_result(task_info)
        except HTTPException as e:
            logging.error("an error occur the task_info server is down {e}. check connecteam_service")
                
            


@router.post("/task", status_code=status.HTTP_201_CREATED)
async def create_task(payload: Dict[str, Any] = Body(...)):
    try:
        resp = connecteam_api_client.create_task(payload)
        return _unwrap_result(resp)
    except(ConnectionError, TimeoutError, ValueError) as e:
        logging.warning(f"Primary Connecteam API failed: {e}")
        logging.info("Trying fallback service...")
        try:
            create_task = services.ConnecteamClient()
            task_created = await create_task.create_task(payload=payload)
            if isinstance(task_created, dict):
                return _unwrap_result(task_created)
        except HTTPException as e:
            logging.error("an error occur the task_info server is down {e}. check connecteam_service")


@router.put("/task/{task_id}")
async def update_task(task_id: str, payload: Dict[str, Any] = Body(...)):
    try:
        resp = connecteam_api_client.update_task(task_id, payload)
        return _unwrap_result(resp)
    except(ConnectionError, TimeoutError, ValueError) as e:
        logging.warning(f"Primary Connecteam API failed: {e}")
        logging.info("Trying fallback service...")
        try:
            update_task = services.ConnecteamClient()
            task_created = await update_task.update_task(task_id=task_id,payload=payload)
            if isinstance(task_created, dict):
                return _unwrap_result(task_created) # not sure if we need this 
        except HTTPException as e:
            logging.error("an error occur the task_info server is down {e}. check connecteam_service")

    

@router.delete("/task/{task_id}")
async def delete_task(task_id: str):
    resp = connecteam_api_client.delete_task(task_id)
    return _unwrap_result(resp)

@router.get("/jobs")
async def list_get_jobs():
    resp = connecteam_api_client.list_get_jobs()
    return _unwrap_result(resp)