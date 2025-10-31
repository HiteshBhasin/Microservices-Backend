from fastapi import APIRouter, Query, Body, HTTPException, status
from fastapi.responses import FileResponse
from typing import Any, Dict, Optional
from services.connecteam_service import ConnecteamClient
import os

router = APIRouter()


def _unwrap_result(resp: Dict[str, Any]) -> Any:
    """Normalize the client response: raise on 'error', return 'result' if present.

    The MCP client returns a dict like {'result': ...} or {'error': ...}.
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
    service = ConnecteamClient()
    resp = await service.retrieve_tenants()
    return _unwrap_result(resp)


@router.get("/tasks")
async def get_tasks(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: str = Query("active"),
):
    service = ConnecteamClient()
    resp = await service.list_tasks(limit=limit, offset=offset, status=status)
    return _unwrap_result(resp)


@router.get("/task/{task_id}")
async def get_a_task(task_id: str):
    service = ConnecteamClient()
    resp = await service.get_task(task_id)
    return _unwrap_result(resp)


@router.post("/task", status_code=status.HTTP_201_CREATED)
async def create_task(payload: Dict[str, Any] = Body(...)):
    service = ConnecteamClient()
    resp = await service.create_task(payload)
    return _unwrap_result(resp)


@router.put("/task/{task_id}")
async def update_task(task_id: str, payload: Dict[str, Any] = Body(...)):
    service = ConnecteamClient()
    resp = await service.update_task(task_id, payload)
    return _unwrap_result(resp)


@router.delete("/task/{task_id}")
async def delete_task(task_id: str):
    service = ConnecteamClient()
    resp = await service.delete_task(task_id)
    return _unwrap_result(resp)


@router.get("/tasks/report")
async def tasks_report(limit: int = Query(100, ge=1)):
    service = ConnecteamClient()
    resp = await service.generate_tasks_report(limit=limit)
    return _unwrap_result(resp)


@router.get("/tasks/report/pdf")
async def tasks_report_pdf(limit: int = Query(100, ge=1)):
    """Generate a PDF report on the server and return it as a FileResponse.

    The MCP tool writes a PDF file and returns a dict containing 'pdf_path'.
    """
    service = ConnecteamClient()
    resp = await service.generate_tasks_report_pdf(limit=limit)
    out = _unwrap_result(resp)
    # If the MCP tool returned a dict with 'pdf_path', serve the file
    pdf_path = None
    if isinstance(out, dict) and out.get("pdf_path"):
        pdf_path = out.get("pdf_path")
    elif isinstance(resp, dict) and resp.get("pdf_path"):
        pdf_path = resp.get("pdf_path")

    if not pdf_path:
        raise HTTPException(status_code=500, detail={"error": "PDF not generated", "result": out})

    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail=f"PDF not found: {pdf_path}")

    return FileResponse(path=pdf_path, media_type="application/pdf", filename=os.path.basename(pdf_path))