import logging
import sys
from pathlib import Path
from typing import Dict
from redis import Redis
# Ensure the repository root is on sys.path so top-level packages import reliably
PROJECT_ROOT = Path(__file__).absolute().parent.parent

if str(PROJECT_ROOT) not in sys.path:
 	sys.path.insert(0, str(PROJECT_ROOT))

try:
	# Import after adjusting sys.path
	from mcp_server import doorloop_mcp_server
except Exception as exc:
	raise ImportError(f"Failed to import mcp_server. Ensure project root is correct: {PROJECT_ROOT}\nOriginal error: {exc}")

try:
    if Redis:
        r_connection  = Redis(host='localhost', port=6379 , decode_responses=True)
    
except Exception as e:
    logging.exception(f"an error has occur , {e}")

    
def retrieve_data(*args):
   try:
       # If a single object was passed, return it directly
       if len(args) == 1:
           return args[0]
       return args
   except Exception as e:
       logging.exception(f" An internal error has occur please check the MCP server,{e}")
       return None
       

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
    
   
    property_id = get_propertys(raw_data)
   
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
    for t in parsed_obj:
        print(t)
    return parsed_obj

def get_propertys(raw_data):
    """Extract property id(s) from tenant prospectInfo entries."""
    if raw_data is None:
        logging.error("get_propertys: no raw_data provided")
        return []

    # Normalize payload
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

        # Normalize to list
        prospect_list = prospect if isinstance(prospect, list) else [prospect]

        for p in prospect_list:
            interests = p.get("interests", [])
            for item in interests:
                prop_id = item.get("property")
                if prop_id:
                    property_ids.append(prop_id)

    # Convert back to list or dict
    return list(property_ids)

def property_info(raw_data):
    if not isinstance(raw_data, dict)  or len(raw_data)==0:
        raise ValueError("There is not Data, Please chck the MCP server and fix the doorloop mcp server")
    
    try:
        property_id = get_propertys(raw_data=raw_data)
        
    except Exception:
        logging.exception("the data didnt get fetch in from the server")
        
    addressobj = []
    
    for pid in property_id:
    
        property_info = doorloop_mcp_server.retrieve_properties_id(pid)
        property_info = property_info.get("address")
        print(property_info)
        removed_info = ["state","zip","country","lat","lng", "isValidAddress"]
        if isinstance(property_info, dict) and len(property_info)==0:
            addresses = {k:v for k, v in property_info.items() if k not in removed_info}
            print(addresses)
            addressobj.append(addresses)
    return addressobj
        
                         
       

if __name__ == "__main__":
  
    try:
        from mcp_server import doorloop_mcp_server
    except Exception as exc:
        raise ImportError(f"Failed to import mcp_server. Ensure project root is correct: {PROJECT_ROOT}\nOriginal error: {exc}")
    doorloop_server = doorloop_mcp_server.retrieve_tenants()
    # print("Raw response from doorloop_mcp_server.retrieve_tenants():", doorloop_server)
    raw_data = retrieve_data(doorloop_server)
    print(raw_data)
    # Pass the raw_data into the parser and capture returned structure
    # get_doorloop_tenants(raw_data=raw_data)
    # get_propertys(raw_data=raw_data)
    data = property_info(raw_data=raw_data)
    print(data)
   
    




#  property_info = doorloop_mcp_server.retrieve_properties_id(property_id[i])
#         # if isinstance(property_info, dict) and len(property_info)>0:
#         prop_add = property_info.get("address")
#         return prop_add
#             #
                        
#             #             print(addobj) 
    
