from fastapi import APIRouter, HTTPException
from typing import Any, Dict, List
import os , sys, logging
from services.doorloop_services import DoorloopClient
from services import doorloop_api_client  # Pure HTTP API client (no MCP)
from pathlib import Path
PROJECT_ROOT = Path(__file__).absolute().parent.parent

if str(PROJECT_ROOT) not in sys.path:
 	sys.path.insert(0, str(PROJECT_ROOT))

try:
    from services import doorloop_services as services
except Exception as e:
    logging.exception("there was an error loading mcp service file")
    

try:
    from middle_layer import doorloop_bridge
except Exception as exc:
	raise ImportError(f"Failed to import mcp_server. Ensure project root is correct: {PROJECT_ROOT}\nOriginal error: {exc}")
    

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

def _unwrap_result(resp: Any) -> Any:
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
    # Use pure HTTP API client instead of MCP to avoid pipe errors
    try:
        resp = doorloop_api_client.retrieve_tenants()
        filter_res = doorloop_bridge.get_doorloop_tenants(resp)
        return _unwrap_result(filter_res)
    except(ConnectionError, TimeoutError, ValueError) as e:
        logging.warning(f"Primary Doorloop API failed: {e}")
        logging.info("Trying fallback service...")
        try:
            tenants = services.DoorloopClient()
            tenants_info = tenants.retrieve_tenants()
            if isinstance(tenants_info, dict):
                return _unwrap_result(tenants_info)
        except HTTPException as e:
            logging.exception("an error occur the retrieve_tenants server is down. check connecteam_service")
            raise  HTTPException(status_code=500,detail="Both primary and fallback Doorloop services failed.")
            
            
@router.get("/properties")
async def get_properties():
    _require_api_key()
    try:
        resp = doorloop_api_client.retrieve_properties()
        return _unwrap_result(resp)
    except(ConnectionError, ValueError, TimeoutError) as e:
        logging.warning(f"Primary Doorloop API failed: {e}")
        logging.info("Trying fallback service...")
        try:
            properties = services.DoorloopClient()
            properties_info  = properties.retrieve_properties()
            if isinstance(properties_info, dict):
                return _unwrap_result(properties_info)
        except HTTPException as e:
            logging.error(f"Fallback Connecteam service also failed: {e}")
            raise  HTTPException(status_code=500,detail="Both primary and fallback Doorloop services failed.")
                       


@router.get("/tenant/{tenant_id}")
async def get_tenant(tenant_id: str):
    _require_api_key()
    try:
        resp = doorloop_api_client.retrieve_a_tenants(tenant_id)
        return _unwrap_result(resp)
    except (ConnectionError, ValueError, TimeoutError) as e:
        logging.warning(f"Primary Doorloop API failed: {e}")
        logging.info("Trying fallback service...")
        try:
            each__tenant = services.DoorloopClient()
            tenant_info  = each__tenant.retrieve_a_tenant(tenant_id= tenant_id)
            if isinstance(tenant_info, dict):
                return _unwrap_result(tenant_info)
        except HTTPException as e:
            logging.error(f"Fallback Connecteam service also failed: {e}")
            raise  HTTPException(status_code=500,detail="Both primary and fallback Doorloop services failed.")
        

@router.get("/leases")
async def get_leases():
    _require_api_key()
    try:
        resp = doorloop_api_client.retrieve_leases()
        return _unwrap_result(resp)
    except (ConnectionError, ValueError, TimeoutError) as e:
        logging.warning(f"Primary Doorloop API failed: {e}")
        logging.info("Trying fallback service...")
        try:
            lease = services.DoorloopClient()
            get_lease  = lease.retrieve_leases()
            if isinstance(get_lease, dict):
                return _unwrap_result(get_lease)
        except HTTPException as e:
            logging.error(f"Fallback Connecteam service also failed: {e}")
            raise  HTTPException(status_code=500,detail="Both primary and fallback Doorloop services failed.")


@router.get("/communications")
async def get_communications():
    """Retrieve DoorLoop communications data."""
    _require_api_key()
    try:
        resp = doorloop_api_client.retrieve_doorloop_communication()
        return _unwrap_result(resp)
    except (ConnectionError, ValueError, TimeoutError) as e:
        logging.warning(f"Primary Doorloop API failed: {e}")
        logging.info("Trying fallback service...")
        try:
            comms = services.DoorloopClient() #-> need to create communication method in the doorloop_direct
            # get_comms = comms.
            # if isinstance(get_lease, dict):
            #     return _unwrap_result(get_lease)
        except HTTPException as e:
            logging.error(f"Fallback Connecteam service also failed: {e}")
            raise  HTTPException(status_code=500,detail="Both primary and fallback Doorloop services failed.")

@router.get("/tasks")
async def retrieve_doorloop_tasks() :
    """Retrieve DoorLoop communications data."""
    _require_api_key()
    try:
        resp = doorloop_api_client.retrieve_doorloop_tasks()
        return _unwrap_result(resp)
    except (ConnectionError, ValueError, TimeoutError) as e:
        logging.warning(f"Primary Doorloop API failed: {e}")
        logging.info("Trying fallback service...")
        # try:
        #     tasks = services.DoorloopClient() - >need to create get tasks in doorloop direct and doorloop service
        #     get_lease  = tasks
        #     if isinstance(get_lease, dict):
        #         return _unwrap_result(get_lease)
        # except HTTPException as e:
        #     logging.error(f"Fallback Connecteam service also failed: {e}")
        #     raise  HTTPException(status_code=500,detail="Both primary and fallback Doorloop services failed.")

@router.get("/lease-payments")
async def retrieve_doorloop_lease_payment()  :
    """Retrieve DoorLoop communications data."""
    _require_api_key()
    resp = doorloop_api_client.retrieve_doorloop_lease_payment()
    return _unwrap_result(resp)

@router.get("/expenses")
async def retrieve_doorloop_expenses()  :
    """Retrieve DoorLoop communications data."""
    _require_api_key()
    resp = doorloop_api_client.retrieve_doorloop_expenses() 
    return _unwrap_result(resp)

@router.get("/balance-sheet/report")
async def balance_sheet_report():
    """Generate DoorLoop balance sheet report with PDF."""
    _require_api_key()
    # This one might need MCP for report generation, keeping it for now
    svc = DoorloopClient()
    resp = await svc.generate_report()
    return _unwrap_result(resp)
