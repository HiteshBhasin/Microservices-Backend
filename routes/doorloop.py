from fastapi import APIRouter, HTTPException, Body
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
        # Fetch all data
        tenants_data = doorloop_api_client.retrieve_tenants()
        property_data = doorloop_api_client.retrieve_properties()
        lease_data = doorloop_api_client.retrieve_leases()
           
        # Get aggregated overview information first
        total_properties, active_tenants_list, total_rent_due, active_leases_list, month_list, rent_list = doorloop_bridge.fetch_accumulative_info(
            prop_raw_data=property_data,
            tenant_raw_data=tenants_data,
            lease_raw_data=lease_data,
         
        )
        
        # Get filtered tenant info for the list
        tenant_list, _, _ = doorloop_bridge.get_doorloop_tenants(tenants_data)
        
        # Build combined response with overview data
        response = {
            "tenants": tenant_list if isinstance(tenant_list, list) else [],
            "total_properties": total_properties,
            "active_tenants_count": len(active_tenants_list) if isinstance(active_tenants_list, list) else 0,
            "total_rent_due": f"${total_rent_due:,.2f}",
            "active_leases_count": len(active_leases_list) if isinstance(active_leases_list, list) else 0,
            "vacant_units": 0,  # Calculate based on your business logic
            "outstanding_balance": total_rent_due,
            "month_list": month_list,
            "rent_list":rent_list,
            "profit": sum(rent_list)
        }
        
        return response
        
    except(ConnectionError, TimeoutError, ValueError) as e:
        logging.warning(f"Primary Doorloop API failed: {e}")
        logging.info("Trying fallback service...")
        try:
            tenants = services.DoorloopClient()
            tenants_info = await tenants.retrieve_tenants()  # Added await for async call
            if isinstance(tenants_info, dict):
                return _unwrap_result(tenants_info)
        except HTTPException as e:
            logging.exception("an error occur the retrieve_tenants server is down. check connecteam_service")
            raise HTTPException(status_code=500, detail="Both primary and fallback Doorloop services failed.")
            
            
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
            properties_info = await properties.retrieve_properties()  # Added await for async call
            if isinstance(properties_info, dict):
                return _unwrap_result(properties_info)
        except HTTPException as e:
            logging.error(f"Fallback Doorloop service also failed: {e}")
            raise HTTPException(status_code=500, detail="Both primary and fallback Doorloop services failed.")
                       


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
            tenant_info = await each__tenant.retrieve_a_tenant(tenant_id=tenant_id)  # Added await for async call
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
        data_list, lease_status = doorloop_bridge.get_lease_info(resp)
        return _unwrap_result(data_list)
    except (ConnectionError, ValueError, TimeoutError) as e:
        logging.warning(f"Primary Doorloop API failed: {e}")
        logging.info("Trying fallback service...")
        try:
            lease = services.DoorloopClient()
            get_lease = await lease.retrieve_leases()  # Added await for async call
            data_list, lease_status = doorloop_bridge.get_lease_info(get_lease)
            return _unwrap_result(data_list)
        except HTTPException as e:
            logging.error(f"Fallback Doorloop service also failed: {e}")
            raise HTTPException(status_code=500, detail="Both primary and fallback Doorloop services failed.")


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
            comms = services.DoorloopClient()
            get_comms = await comms.retrieve_doorloop_communication()
            if isinstance(get_comms, dict):
                return _unwrap_result(get_comms)
        except HTTPException as e:
            logging.error(f"Fallback Doorloop service also failed: {e}")
            raise HTTPException(status_code=500, detail="Both primary and fallback Doorloop services failed.")

@router.get("/tasks")
async def retrieve_doorloop_tasks():
    """Retrieve DoorLoop tasks data."""
    _require_api_key()
    try:
        resp = doorloop_api_client.retrieve_doorloop_tasks()
        return _unwrap_result(resp)
    except (ConnectionError, ValueError, TimeoutError) as e:
        logging.warning(f"Primary Doorloop API failed: {e}")
        logging.info("Trying fallback service...")
        try:
            tasks = services.DoorloopClient()
            get_tasks = await tasks.retrieve_doorloop_tasks()
            if isinstance(get_tasks, dict):
                return _unwrap_result(get_tasks)
        except HTTPException as e:
            logging.error(f"Fallback Doorloop service also failed: {e}")
            raise HTTPException(status_code=500, detail="Both primary and fallback Doorloop services failed.")

@router.get("/lease-payments")
async def retrieve_doorloop_lease_payment():
    """Retrieve DoorLoop lease payments data."""
    _require_api_key()
    try:
        resp = doorloop_api_client.retrieve_doorloop_lease_payment()
        return _unwrap_result(resp)
    except (ConnectionError, ValueError, TimeoutError) as e:
        logging.warning(f"Primary Doorloop API failed: {e}")
        logging.info("Trying fallback service...")
        try:
            payments = services.DoorloopClient()
            get_payments = await payments.retrieve_doorloop_lease_payment()
            if isinstance(get_payments, dict):
                return _unwrap_result(get_payments)
        except HTTPException as e:
            logging.error(f"Fallback Doorloop service also failed: {e}")
            raise HTTPException(status_code=500, detail="Both primary and fallback Doorloop services failed.")

@router.get("/expenses")
async def retrieve_doorloop_expenses():
    """Retrieve DoorLoop expenses data."""
    _require_api_key()
    try:
        resp = doorloop_api_client.retrieve_doorloop_expenses()
        return _unwrap_result(resp)
    except (ConnectionError, ValueError, TimeoutError) as e:
        logging.warning(f"Primary Doorloop API failed: {e}")
        logging.info("Trying fallback service...")
        try:
            expenses = services.DoorloopClient()
            get_expenses = await expenses.retrieve_doorloop_expenses()
            if isinstance(get_expenses, dict):
                return _unwrap_result(get_expenses)
        except HTTPException as e:
            logging.error(f"Fallback Doorloop service also failed: {e}")
            raise HTTPException(status_code=500, detail="Both primary and fallback Doorloop services failed.")

@router.get("/balance-sheet/report")
async def balance_sheet_report():
    """Generate DoorLoop balance sheet report with PDF."""
    _require_api_key()
    # This one might need MCP for report generation, keeping it for now
    svc = DoorloopClient()
    resp = await svc.generate_report()
    return _unwrap_result(resp)


# @router.post("/accounts")
# async def create_account(
#     active: bool = Body(True, description="Whether the account is active"),
#     account_type: str = Body("ASSET_ACCOUNTS_RECEIVABLE", alias="type", description="Type of account to create")
# ):
#     """Create a new account in DoorLoop.
    
#     Args:
#         active: Whether the account should be active (default: True)
#         account_type: Account type (default: "ASSET_ACCOUNTS_RECEIVABLE")
        
#     Returns:
#         The created account data
#     """
#     _require_api_key()
#     try:
#         resp = doorloop_api_client.create_account(active=active, account_type=account_type)
#         return _unwrap_result(resp)
#     except (ConnectionError, ValueError, TimeoutError) as e:
#         logging.error(f"Failed to create account: {e}")
#         raise HTTPException(status_code=500, detail=f"Failed to create account: {str(e)}")


@router.post("/tenants")
async def create_tenant(
    firstName: str = Body(..., description="Tenant's first name"),
    lastName: str = Body(..., description="Tenant's last name"),
    middleName: str = Body(None, description="Tenant's middle name (optional)"),
    gender: str = Body(None, description="Gender: MALE, FEMALE, or PREFER_NOT_TO_SAY (optional)"),
):
    """Create a new tenant in DoorLoop.
    
    Args:
        firstName: Tenant's first name (required)
        lastName: Tenant's last name (required)
        middleName: Tenant's middle name (optional)
        gender: Gender enum value (optional)
        
    Returns:
        The created tenant data with ID
    """
    _require_api_key()
    try:
        resp = await doorloop_api_client.create_tenant(
            first_name=firstName,
            last_name=lastName,
            middle_name=middleName,
            gender=gender
        )
        return _unwrap_result(resp)
    except (ConnectionError, ValueError, TimeoutError) as e:
        logging.warning(f"Primary Doorloop API failed: {e}")
        logging.info("Trying fallback MCP service...")
        try:
            tenant_service = services.DoorloopClient()
            tenant_info = await tenant_service.create_tenant(
                firstName=firstName,
                lastName=lastName,
                middleName=middleName,
                gender=gender
            )
            if isinstance(tenant_info, dict):
                return _unwrap_result(tenant_info)
        except HTTPException as e:
            logging.error(f"Fallback Doorloop service also failed: {e}")
            raise HTTPException(status_code=500, detail="Both primary and fallback Doorloop services failed.")



