import logging
import sys
from pathlib import Path


# Ensure the repository root is on sys.path so top-level packages import reliably
PROJECT_ROOT = Path(__file__).absolute().parent.parent

if str(PROJECT_ROOT) not in sys.path:
 	sys.path.insert(0, str(PROJECT_ROOT))

try:
	# Import after adjusting sys.path
	from mcp_server import doorloop_mcp_server
except Exception as exc:
	raise ImportError(f"Failed to import mcp_server. Ensure project root is correct: {PROJECT_ROOT}\nOriginal error: {exc}")


data = doorloop_mcp_server.retrieve_tenants()


def retrieve_data(*args):
   try:
       # If a single object was passed, return it directly
       if len(args) == 1:
           return args[0]
       return args
   except Exception as e:
       logging.exception(f" An internal error has occur please check the MCP server,{e}")
       return None

def get_propertys(raw_data):
    """Extract property id(s) from tenant prospectInfo entries."""
    if raw_data is None:
        logging.error("get_propertys: no raw_data provided")
        return []

    if isinstance(raw_data, tuple) and len(raw_data) > 0:
        payload = raw_data[0]
    elif isinstance(raw_data, dict):
        payload = raw_data
    else:
        logging.error("get_propertys: unexpected raw_data type %s", type(raw_data))
        return []

    tenants = payload.get("data", [])
    property_ids = []  

    for tenant in tenants:
        prospect = tenant.get("prospectInfo")
        if not prospect:
            continue

        prospect_list = prospect if isinstance(prospect, list) else [prospect]

        for p in prospect_list:
            interests = p.get("interests", [])
            for item in interests:
                prop_id = item.get("property")
                if prop_id:
                    property_ids.append(prop_id)

    return list(property_ids)


def get_doorloop_tenants(raw_data):
  
    if raw_data is None:
        logging.error("No raw_data provided to parser")
        return []

    if isinstance(raw_data, tuple) and len(raw_data) > 0:
        payload = raw_data[0]
        
    elif isinstance(raw_data, dict):
        payload = raw_data
    else:
        logging.error("Unexpected raw_data type: %s", type(raw_data))
        return []

    tenants = payload["data"]
    if not isinstance(tenants, list):
        logging.error("No tenant list found in payload")
        return []
    
    # property_id = get_propertys(raw_data)
    
    parsed_obj = []
    for idx, tenant in enumerate(tenants):
        try:
            # safe lookups with defaults
            tenant_id = tenant.get("id")
            name = tenant.get("fullName") or tenant.get("name") or ""

            # extract first email address if present
            email_addr , phone = None, None
            for e in tenant.get("emails", []) or []:
                if isinstance(e, dict) and e.get("address"):
                    email_addr = e.get("address")
                    break
                
            for e in tenant.get("phones",[]) or []:
                if isinstance(e, dict) and e.get("number"):
                    phone = e.get("number")
                    break
            # fallback to portal login email if available
            if not email_addr:
                portal = tenant.get("portalInfo") or {}
                email_addr = portal.get("loginEmail")

            status = (tenant.get("portalInfo") or {}).get("status") or tenant.get("status") or "UNKNOWN"
           
            parsed_obj.append({
                # "id": tenant_id,
                "name": name,
                "Phone Number" : phone,
                "email": email_addr,
                "properties": "",
                "status": status,
            })
    
        except Exception:
            logging.exception("Failed to parse tenant at index %s")
            # continue parsing remaining tenants
            continue

    # Print/return full parsed list
    logging.info("Parsed %d tenants", len(parsed_obj))
    return parsed_obj

def property_info(raw_data, ):
    """Fetch property details (address) for up to `limit` property ids.
    
    Uses Redis cache first; falls back to API if not cached.
    Returns a list of dicts: [{'property_id': id, 'address': {...}}, ...]
    """
    if raw_data is None:
        logging.error("property_info: no raw_data provided")
        return []
    
    try:
        property_ids = get_propertys(raw_data=raw_data)
    except Exception:
        logging.exception("Failed to extract property ids from raw_data")
        return []
    
    if not property_ids:
        logging.info("No property ids found")
        return []
    
    addressobj = []
    removed_keys = ["state", "zip", "country", "lat", "lng", "isValidAddress"]
    
    for pid in property_ids:  # Limit to first N property ids
        try:
            # Try Redis cache first (fast)
            # cached = get_cached_property(pid)
            if "cached":
                prop_data = "cached"
            else:
                # Fall back to API and cache result
                prop_data = doorloop_mcp_server.retrieve_properties_id(pid)
                if isinstance(prop_data, dict):
                    pass
                    # cache_properties_to_redis({pid: prop_data})
            
            if not isinstance(prop_data, dict):
                logging.warning("Property lookup did not return dict for id %s", pid)
                continue
            
            # Extract address and filter out unwanted keys
            address = prop_data.get("address") or {}
            filtered_address = {k: v for k, v in address.items() if k not in removed_keys}
            
            addressobj.append({
                "property_id": pid,
                "address": filtered_address
            })
        except Exception:
            logging.exception("Failed to retrieve property info for id %s", pid)
            continue
    
    return addressobj

                                
if __name__ == "__main__":
    pass
  
   