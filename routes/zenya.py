from fastapi import APIRouter, HTTPException
from typing import Any, Dict, List
import os , sys, logging
from services.doorloop_services import DoorloopClient
from services import zenya_api_client  # Pure HTTP API client (no MCP)
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

            
            
@router.get("/properties")
async def get_properties():
    _require_api_key()
    try:
        resp = zenya_api_client.retrieve_properties()
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
                       

