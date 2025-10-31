from fastapi import APIRouter, Query, Body, HTTPException, status
from fastapi.responses import FileResponse
from typing import Any, Dict
from services.doorloop_services import DoorloopClient
import os
from uuid import uuid4

router = APIRouter()


def _unwrap_result(resp: Dict[str, Any]) -> Any:
    """Normalize the client response: raise on 'error', return 'result' if present."""
    if not isinstance(resp, dict):
        return resp
    if "error" in resp:
        detail = resp.get("error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)
    if "result" in resp:
        return resp["result"]
    return resp


@router.get("/tenants")
async def get_tenants():
    svc = DoorloopClient()
    resp = await svc.retrieve_tenants()
    return _unwrap_result(resp)


@router.get("/properties")
async def get_properties(limit: int = Query(100, ge=1)):
    svc = DoorloopClient()
    # Current client returns all properties; keep limit param for future use
    resp = await svc.retrieve_properties()
    return _unwrap_result(resp)


@router.get("/tenant/{tenant_id}")
async def get_tenant(tenant_id: str):
    svc = DoorloopClient()
    resp = await svc.retrieve_a_tenants(tenant_id)
    return _unwrap_result(resp)


@router.get("/leases")
async def get_leases():
    svc = DoorloopClient()
    resp = await svc.retrieve_leases()
    return _unwrap_result(resp)


@router.get("/properties/report")
async def properties_report():
    svc = DoorloopClient()
    resp = await svc.generate_properties_report()
    return _unwrap_result(resp)


@router.get("/properties/report/pdf")
async def properties_report_pdf():
    """Generate a PDF report on the server and return it as a FileResponse.

    The MCP tool writes a PDF file and returns a dict containing 'pdf_path'.
    We request a unique filename to avoid collisions.
    """
    svc = DoorloopClient()
    filename = f"doorloop_properties_report_{uuid4().hex}.pdf"
    resp = await svc.generate_properties_report_pdf(out_path=filename)
    out = _unwrap_result(resp)

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
from fastapi import APIRouter

app = APIRouter()

