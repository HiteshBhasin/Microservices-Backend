from fastapi import APIRouter, Query, Body, HTTPException, status
from typing import Any, Dict
from enum import Enum
from services import connecteam_api_client
from middle_layer import conneteam_bridge
import logging

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
    """Normalize the client response: raise on 'error', return 'result' if present."""
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
    except (ConnectionError, TimeoutError, ValueError):
        logging.info("Primary Connecteam API failed, trying fallback service...")
        try:
            retrieve_tenants = services.ConnecteamClient()
            tenants_info = retrieve_tenants.retrieve_tenants()
            if isinstance(tenants_info, dict):
                return _unwrap_result(tenants_info)
        except HTTPException:
            logging.exception("Fallback retrieve_tenants failed")
            raise HTTPException(status_code=500, detail="Both primary and fallback Connecteam services failed.")


@router.get("/tasks")
async def get_tasks(
    limit: int = Query(100, ge=1, le=100, description="Number of tasks to return (1-100)"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip for pagination"),
    status: TaskStatus = Query(TaskStatus.all, description="Task status filter"),
    user_id: str = Query(None, description="Filter by user ID(s) - comma separated list (optional)"),
    title: str = Query(None, description="Filter by task title - partial match (optional)"),
    duedate: str = Query(None, description="Filter by due date - YYYY-MM-DD format (optional)"),
):
    try:
        resp = connecteam_api_client.list_tasks(limit=limit, offset=offset, status=status.value)
        result = _unwrap_result(resp)

        if not result:
            return []

        # If the API already returned a list, wrap it for the bridge
        if isinstance(result, list):
            data_to_process = {"data": {"tasks": result}}
        # If the API returned a dict with data.tasks, pass that through
        elif isinstance(result, dict) and isinstance(result.get("data", {}).get("tasks"), list):
            data_to_process = result
        else:
            # Unknown shape; return raw
            return result

        processed = conneteam_bridge.get_times(
            data_to_process,
            get_user=connecteam_api_client.get_user,
            status=status.value if status.value != "all" else None,
            user_id=user_id,
            title=title,
            duedate=duedate,
        )
        return processed if processed is not None else result
    except (ConnectionError, TimeoutError, ValueError) as e:
        logging.warning(f"Primary Connecteam API failed: {e}")
        logging.info("Trying fallback service...")
        try:
            list_task = services.ConnecteamClient()
            tasks_info = await list_task.list_tasks(limit=limit, offset=offset, status=status)
            if isinstance(tasks_info, dict):
                return _unwrap_result(tasks_info)
        except HTTPException as e:
            logging.exception("Fallback list_tasks failed")
            raise HTTPException(status_code=500, detail="Both primary and fallback Connecteam services failed.")
            
                


@router.get("/task/{task_id}")
async def get_a_task(task_id: str):
    try:
        resp = connecteam_api_client.get_task(task_id)
        return _unwrap_result(resp)
    except (ConnectionError, TimeoutError, ValueError) as e:
        logging.warning(f"Primary Connecteam API failed: {e}")
        logging.info("Trying fallback service...")
        try:
            get_task = services.ConnecteamClient()
            task_info = await get_task.get_task(task_id=task_id)
            if isinstance(task_info, dict):
                return _unwrap_result(task_info)
        except HTTPException as e:
            logging.error("Fallback get_task failed")
            raise HTTPException(status_code=500, detail="Both primary and fallback Connecteam services failed.")
                
            


@router.post("/task", status_code=status.HTTP_201_CREATED)
async def create_task(payload: Dict[str, Any] = Body(...)):
    try:
        resp = connecteam_api_client.create_task(payload)
        return _unwrap_result(resp)
    except (ConnectionError, TimeoutError, ValueError) as e:
        logging.warning(f"Primary Connecteam API failed: {e}")
        logging.info("Trying fallback service...")
        try:
            create_task = services.ConnecteamClient()
            task_created = await create_task.create_task(payload=payload)
            if isinstance(task_created, dict):
                return _unwrap_result(task_created)
        except HTTPException as e:
            logging.error("Fallback create_task failed")
            raise HTTPException(status_code=500, detail="Both primary and fallback Connecteam services failed.")


@router.put("/task/{task_id}")
async def update_task(task_id: str, payload: Dict[str, Any] = Body(...)):
    try:
        resp = connecteam_api_client.update_task(task_id, payload)
        return _unwrap_result(resp)
    except (ConnectionError, TimeoutError, ValueError) as e:
        logging.warning(f"Primary Connecteam API failed: {e}")
        logging.info("Trying fallback service...")
        try:
            update_task = services.ConnecteamClient()
            task_created = await update_task.update_task(task_id=task_id,payload=payload)
            if isinstance(task_created, dict):
                return _unwrap_result(task_created) # not sure if we need this 
        except HTTPException as e:
            logging.error("Fallback update_task failed")
            raise HTTPException(status_code=500, detail="Both primary and fallback Connecteam services failed.")

    

@router.delete("/task/{task_id}")
async def delete_task(task_id: str):
    resp = connecteam_api_client.delete_task(task_id)
    return _unwrap_result(resp)

@router.get("/jobs")
async def list_get_jobs():
    resp = connecteam_api_client.list_get_jobs()
    return _unwrap_result(resp)


@router.get("/taskboard")
async def get_taskboard():
    resp = connecteam_api_client.list_taskboards()
    return _unwrap_result(resp)


@router.get("/activity")
async def get_time_activity(
    startDate: str,
    endDate: str,
    user_id: str = Query(None, description="Filter by user ID(s) - comma separated list (optional)"),
    title: str = Query(None, description="Filter by task title - partial match (optional)"),
    duedate: str = Query(None, description="Filter by due date - YYYY-MM-DD format (optional)"),
):
    try:
        resp = connecteam_api_client.get_time_activity(startDate=startDate, endDate=endDate)
        result = _unwrap_result(resp)

        if not result:
            return []

        # If the API already returned a list, wrap it for the bridge
        if isinstance(result, list):
            data_to_process = {"data": {"tasks": result}}
        # If the API returned a dict with data.tasks, pass that through
        elif isinstance(result, dict) and isinstance(result.get("data", {}).get("tasks"), list):
            data_to_process = result
        else:
            # Unknown shape; return raw
            return result

        processed = conneteam_bridge.get_times(
            data_to_process,
            get_user=connecteam_api_client.get_user,
            user_id=user_id,
            title=title,
            duedate=duedate,
        )
        return processed if processed is not None else result
    except Exception:
        logging.exception("Error retrieving activity data")
        raise HTTPException(status_code=500, detail="Failed to retrieve activity data")
    