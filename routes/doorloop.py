from fastapi import APIRouter, Query, Body, HTTPException, status, Request
from fastapi.responses import FileResponse
from typing import Any, Dict
import os
from uuid import uuid4
from services.doorloop_services import DoorloopClient

router = APIRouter()
# Generalized api key function.
def _require_api_key() -> str:
    key = os.getenv("DOORLOOP_API_KEY")
    if not key:
        raise HTTPException(
            status_code=400,
            detail="DOORLOOP_API_KEY not configured; set it in .env or environment"
        )
    return key
#This function is a response handler for MCP (Model Context Protocol) service calls
def _unwrap_result(resp: Dict[str, Any]) -> Any:
    if not isinstance(resp, dict):
        return resp
    if "error" in resp:
        raise HTTPException(status_code=500, detail=str(resp["error"]))
    if "result" in resp:
        return resp["result"]
    return resp or {"message": "Empty response from MCP service"}


@router.get("/tenants")
async def get_tenants():
    _require_api_key()
    svc = DoorloopClient()
    resp = await svc.retrieve_tenants()
    return _unwrap_result(resp)


@router.get("/properties")
async def get_properties(limit: int = Query(100, ge=1)):
    _require_api_key()
    svc = DoorloopClient()
    resp = await svc.retrieve_properties()
    return _unwrap_result(resp)


@router.get("/tenant/{tenant_id}")
async def get_tenant(tenant_id: str):
    _require_api_key()
    svc = DoorloopClient()
    resp = await svc.retrieve_a_tenant(tenant_id)
    return _unwrap_result(resp)


@router.get("/leases")
async def get_leases():
    _require_api_key()
    svc = DoorloopClient()
    resp = await svc.retrieve_leases()
    return _unwrap_result(resp)


@router.get("/properties/report")
async def properties_report():
    _require_api_key()
    svc = DoorloopClient()
    resp = await svc.generate_properties_report()
    return _unwrap_result(resp)


@router.get("/properties/report/pdf")
async def properties_report_pdf():
    """Generate a PDF report and return as a downloadable file."""
    _require_api_key()
    svc = DoorloopClient()
    filename = f"doorloop_properties_report_{uuid4().hex}.pdf"
    resp = await svc.generate_properties_report_pdf(out_path=filename)
    out = _unwrap_result(resp)

    pdf_path = out.get("pdf_path") if isinstance(out, dict) else None
    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(status_code=500, detail="PDF not found or not generated")

    return FileResponse(path=pdf_path, media_type="application/pdf", filename=os.path.basename(pdf_path))
