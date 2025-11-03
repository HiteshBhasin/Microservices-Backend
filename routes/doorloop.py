from fastapi import APIRouter, HTTPException
from typing import Any, Dict
import os
from services.doorloop_services import DoorloopClient

router = APIRouter()

def _require_api_key() -> str:
    """Ensure DoorLoop API key is configured."""
    key = os.getenv("DOORLOOP_API_KEY")
    if not key:
        raise HTTPException(
            status_code=400,
            detail="DOORLOOP_API_KEY not configured; set it in .env or environment"
        )
    return key

def _unwrap_result(resp: Dict[str, Any]) -> Any:
    """Response handler for MCP (Model Context Protocol) service calls."""
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
async def get_properties():
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


@router.get("/communications")
async def get_communications():
    """Retrieve DoorLoop communications data."""
    _require_api_key()
    svc = DoorloopClient()
    resp = await svc.retrieve_doorloop_communication()
    return _unwrap_result(resp)


@router.get("/balance-sheet/report")
async def balance_sheet_report():
    """Generate DoorLoop balance sheet report with PDF."""
    _require_api_key()
    svc = DoorloopClient()
    resp = await svc.generate_report()
    return _unwrap_result(resp)
