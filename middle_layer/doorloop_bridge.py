import logging
import sys
from pathlib import Path
from redis import Redis


# Ensure the repository root is on sys.path so top-level packages import reliably
PROJECT_ROOT = Path(__file__).absolute().parent.parent

if str(PROJECT_ROOT) not in sys.path:
 	sys.path.insert(0, str(PROJECT_ROOT))


try:
	# Import after adjusting sys.path
    from middle_layer.redis_layer import (
        cache_tenants_to_redis, 
        cache_data_retireive, 
        start_background_refresh,
        redis
    )
except Exception as exc:
	raise ImportError(f"Failed to import redis_layer. Ensure project root is correct: {PROJECT_ROOT}\nOriginal error: {exc}")


try:
	# Import pure API client (NO MCP - just direct HTTP requests)
    from services import doorloop_api_client as doorloop_api
except Exception as exc:
	raise ImportError(f"Failed to import doorloop_api_client. Ensure project root is correct: {PROJECT_ROOT}\nOriginal error: {exc}")


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


def get_lease_data_cached():
    """Fetch and cache lease data. Returns cached data if available."""
    from middle_layer.redis_layer import redis
    import json
    
    # Try to get from cache first
    if redis:
        try:
            cached = redis.get("lease_data")
            if cached:
                logging.info("Using cached lease data")
                return json.loads(cached)
        except Exception:
            logging.exception("Failed to retrieve cached lease data")
    
    # Fetch fresh lease data using pure HTTP API client (no MCP, no async)
    tenant_lease_map = {}
    try:
        lease_data = doorloop_api.retrieve_leases()
        if isinstance(lease_data, dict) and "data" in lease_data:
            leases = lease_data["data"]
            # Create a mapping of tenant name to lease info
            for lease in leases:
                tenant_name = lease.get("name", "")
                if tenant_name:
                    tenant_lease_map[tenant_name] = {
                        "totalBalanceDue": lease.get("totalBalanceDue", 0),
                        "overdueBalance": lease.get("overdueBalance", 0),
                        "currentBalance": lease.get("currentBalance", 0),
                        "totalRecurringRent": lease.get("totalRecurringRent", 0),
                    }
        logging.info("Fetched %d leases from API", len(tenant_lease_map))
        
        # Cache for 1 hour (3600 seconds)
        if redis:
            try:
                redis.setex("lease_data", 3600, json.dumps(tenant_lease_map))
                logging.info("Cached lease data for 1 hour")
            except Exception:
                logging.exception("Failed to cache lease data")
    except Exception:
        logging.exception("Failed to fetch lease data for rent due information")
    
    return tenant_lease_map


def get_doorloop_tenants(raw_data):
    """Parse tenant data and cache the results. Uses cached results if available."""
    from middle_layer.redis_layer import redis
   
    
    if raw_data is None:
        logging.error("No raw_data provided to parser")
        return []

    # Check if we have cached parsed tenants (valid for 30 minutes)
    # We check cache_data_retireive since that's what we return at the end
    try:
        cached_result = cache_data_retireive('data')
        if cached_result and len(cached_result) > 0:
            logging.info("Using cached parsed tenant data from Redis")
            return cached_result
    except Exception:
        logging.debug("No cached data available, will fetch fresh")

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
    
    property_ids = get_propertys(raw_data)
    
    # Fetch property addresses inline to avoid circular dependency
    property_address_map = {}
    removed_keys = ["state", "zip", "country", "lat", "lng", "isValidAddress"]
    
    for pid in property_ids:
        try:
            # Use pure HTTP API client (no MCP, no async)
            prop_data = doorloop_api.retrieve_properties_id(pid)
            if isinstance(prop_data, dict):
                address = prop_data.get("address") or {}
                # Get street address (the field is called 'street1')
                street_address = address.get("street1", "N/A")
                property_address_map[pid] = street_address
        except Exception:
            logging.exception("Failed to fetch property %s", pid)
            continue
    
    # Get lease data from cache (refreshed every hour)
    tenant_lease_map = get_lease_data_cached()
    
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
           
            # Get the property address instead of just the ID
            prop_id = property_ids[idx] if idx < len(property_ids) else None
            prop_address = property_address_map.get(prop_id, "N/A") if prop_id else "N/A"
            
            # Get rent due information from lease data
            lease_info = tenant_lease_map.get(name, {})
            rent_due = lease_info.get("overdueBalance", 0)
            # total_balance = lease_info.get("totalBalanceDue", 0)
            # monthly_rent = lease_info.get("totalRecurringRent", 0)
           
            parsed_obj.append({
                # "id": tenant_id,
                "name": name,
                "Phone Number" : phone,
                "email": email_addr,
                "properties": prop_address,
                "rent_due": f"${rent_due:,.2f}" if rent_due > 0 else "$0.00",
                "status": status,
                # "monthly_rent": f"${monthly_rent:,.2f}" if monthly_rent else "N/A",
                # "total_balance_due": f"${total_balance:,.2f}" if total_balance > 0 else "$0.00",
            })
            
        except Exception:
            logging.exception("Failed to parse tenant at index %s")
            # continue parsing remaining tenants
            continue
    
    # Cache the parsed tenants to Redis (once after loop)
    # This caches with 30 minute TTL by default
    cache_tenants_to_redis(parsed_obj)
    
    # Retrieve what we just cached (ensures consistency)
    returned_ogj = cache_data_retireive('data')
        
    # Print/return full parsed list
    logging.info("Parsed %d tenants from fresh data", len(parsed_obj))
    return returned_ogj


def property_info(raw_data ):
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
            # Fetch property data from pure HTTP API client (no MCP)
            prop_data = doorloop_api.retrieve_properties_id(pid)
            
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


def fetch_fresh_tenants():
    """Fetch fresh tenant data for background refresh."""
    try:
        raw_data = doorloop_api.retrieve_tenants()
        if raw_data:
            return get_doorloop_tenants(raw_data)
    except Exception:
        logging.exception("Failed to fetch tenants for background refresh")
    return []


def fetch_property_ids():
    """Fetch property IDs for background refresh."""
    try:
        raw_data = doorloop_api.retrieve_tenants()
        if raw_data:
            return get_propertys(raw_data)
    except Exception:
        logging.exception("Failed to fetch property IDs for background refresh")
    return []


def fetch_property_by_id(prop_id):
    """Fetch property details by ID."""
    try:
        return doorloop_api.retrieve_properties_id(prop_id)
    except Exception:
        logging.exception("Failed to fetch property %s", prop_id)
    return None

                                
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Fetch data for testing using pure HTTP API client (no MCP)
    data = doorloop_api.retrieve_tenants()
    list_value = get_doorloop_tenants(raw_data=data)
    
    if list_value is not None and isinstance(list_value, list):
        for item in list_value:
            print(item)
    else:
        logging.warning("No tenant data returned or data is not a list: %s", type(list_value))
    
    # Start background refresh workers
    # if isinstance(redis, Redis):
    #     logging.info("Starting background refresh workers...")
    #     start_background_refresh(
    #         tenant_fetch_fn=fetch_fresh_tenants,
    #         property_ids_fn=fetch_property_ids,
    #         property_fetch_fn=fetch_property_by_id,
    #         tenant_interval=30,  # Refresh tenants every 30 minutes
    #         property_interval=60  # Refresh properties every 60 minutes
    #     )
    #     logging.info("Background workers started successfully")
        
        # Keep the script running to allow background workers to operate
        import time
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            logging.info("Shutting down background workers...")
    # else:
    #     logging.warning("Redis not available - background refresh disabled")
  
   