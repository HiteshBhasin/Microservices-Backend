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
    """Fetch and cache lease data. Returns cached data if available (1 hour TTL)."""
    from middle_layer.redis_layer import redis
    import json
    
    # Try to get from cache first
    if redis:
        try:
            cached = redis.get("lease_data:processed")
            if cached:
                logging.info("Cache HIT: Using cached lease data")
                return json.loads(cached)
        except Exception:
            logging.exception("Failed to retrieve cached lease data")
    
    # Fetch fresh lease data using pure HTTP API client
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
                        "id": lease.get("id"),
                        "totalBalanceDue": lease.get("totalBalanceDue", 0),
                        "overdueBalance": lease.get("overdueBalance", 0),
                        "currentBalance": lease.get("currentBalance", 0),
                        "totalRecurringRent": lease.get("totalRecurringRent", 0),
                    }
        logging.info("Fetched %d leases from API", len(tenant_lease_map))
        
        # Cache for 1 hour (3600 seconds)
        if redis:
            try:
                redis.setex("lease_data:processed", 3600, json.dumps(tenant_lease_map))
                logging.info("Cached lease data for 1 hour")
            except Exception:
                logging.exception("Failed to cache lease data")
    except Exception:
        logging.exception("Failed to fetch lease data from API")
    
    return tenant_lease_map


def get_doorloop_tenants(raw_data):
    """Parse tenant data and cache the results (30 min TTL). Uses cache-first approach.
    
    Returns:
        tuple: (parsed_tenants_list, lease_info_dict, property_details_list)
    """
    from middle_layer.redis_layer import redis
    import json
    
    if raw_data is None:
        logging.error("No raw_data provided to get_doorloop_tenants")
        return [], {}, []

    # Check Redis cache first (30 minute TTL)
    if redis:
        try:
            cached = redis.get("doorloop:tenants:parsed")
            if cached:
                logging.info("Cache HIT: Using cached parsed tenant data")
                parsed_tenants = json.loads(cached)
                lease_info = get_lease_data_cached()
                property_details = []  # Cached separately via property_info()
                return parsed_tenants, lease_info, property_details
        except Exception:
            logging.debug("Cache miss or retrieval error, fetching fresh")

    if isinstance(raw_data, tuple) and len(raw_data) > 0:
        payload = raw_data[0]
    elif isinstance(raw_data, dict):
        payload = raw_data
    else:
        logging.error("Unexpected raw_data type: %s", type(raw_data))
        return [], {}, []

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
    
    # Cache the parsed tenants to Redis (30 minute TTL)
    if redis:
        try:
            import json
            redis.setex("doorloop:tenants:parsed", 1800, json.dumps(parsed_obj))
            logging.info("Cached %d parsed tenants for 30 minutes", len(parsed_obj))
        except Exception:
            logging.exception("Failed to cache parsed tenants")
    
    # Also fetch lease and property data for the 3-tuple return
    lease_info = get_lease_data_cached()
    property_details = property_info(raw_data)
    
    logging.info("Returning parsed tenants with lease and property info")
    return parsed_obj, lease_info, property_details


def property_info(raw_data):
    """Fetch property details (address). Uses Redis cache (15 min TTL) to reduce API calls.
    
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
    
    for pid in property_ids:
        try:
            # Check cache first (15 min TTL)
            cache_key = f"doorloop:property:{pid}"
            if redis:
                try:
                    import json
                    cached_prop = redis.get(cache_key)
                    if cached_prop:
                        logging.debug(f"Cache HIT for property {pid}")
                        addressobj.append(json.loads(cached_prop))
                        continue
                except Exception:
                    logging.debug(f"Cache miss for property {pid}")
            
            # Fetch from API if not cached
            prop_data = doorloop_api.retrieve_properties_id(pid)
            
            if not isinstance(prop_data, dict):
                logging.warning("Property lookup did not return dict for id %s", pid)
                continue
            
            # Extract address and filter out unwanted keys
            address = prop_data.get("address") or {}
            filtered_address = {k: v for k, v in address.items() if k not in removed_keys}
            
            prop_obj = {
                "property_id": pid,
                "address": filtered_address
            }
            addressobj.append(prop_obj)
            
            # Cache for 15 minutes
            if redis:
                try:
                    import json
                    redis.setex(cache_key, 900, json.dumps(prop_obj))
                    logging.debug(f"Cached property {pid}")
                except Exception:
                    logging.debug("Failed to cache property")
                    
        except Exception:
            logging.exception("Failed to retrieve property info for id %s", pid)
            continue
    
    logging.info(f"Processed {len(addressobj)} properties")
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


def fetch_accumulative_info(prop_raw_data, tenant_raw_data, lease_raw_data):
    """Aggregate property, tenant, and lease data to compute summary metrics.
    
    Returns:
        tuple: (total_properties, active_tenants_list, total_rent_due, active_leases_list, month_list, rent_list)
    """
    total_properties = 0
    active_tenants_list = []
    total_rent_due = 0.0
    active_leases_list = []
    month_list = []
    rent_list = []
    
    try:
        # Count total properties
        if isinstance(prop_raw_data, dict) and "data" in prop_raw_data:
            properties = prop_raw_data.get("data", [])
            if isinstance(properties, list):
                total_properties = len(properties)
        
        # Extract active tenants
        if isinstance(tenant_raw_data, dict) and "data" in tenant_raw_data:
            tenants = tenant_raw_data.get("data", [])
            if isinstance(tenants, list):
                active_tenants_list = [t for t in tenants if t.get("portalInfo", {}).get("status") == "ACTIVE"]
        
        # Calculate total rent due and build month/rent lists
        if isinstance(lease_raw_data, dict) and "data" in lease_raw_data:
            leases = lease_raw_data.get("data", [])
            if isinstance(leases, list):
                active_leases_list = [l for l in leases if l.get("status") != "archived"]
                for lease in leases:
                    overdue = lease.get("overdueBalance", 0)
                    if overdue > 0:
                        total_rent_due += overdue
                    rent_list.append(lease.get("totalRecurringRent", 0))
        
        # Create month list (placeholder - can be enhanced)
        month_list = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        
        logging.info(f"Aggregated: {total_properties} properties, {len(active_tenants_list)} active tenants, ${total_rent_due:,.2f} rent due")
        
    except Exception:
        logging.exception("Failed to aggregate information")
    
    return total_properties, active_tenants_list, total_rent_due, active_leases_list, month_list, rent_list


def get_lease_info(raw_data):
    """Extract and process lease data from API response.
    
    Returns:
        tuple: (data_list, lease_status_dict)
    """
    data_list = []
    lease_status = {}
    
    try:
        if isinstance(raw_data, dict) and "data" in raw_data:
            leases = raw_data.get("data", [])
            if isinstance(leases, list):
                for lease in leases:
                    lease_item = {
                        "id": lease.get("id"),
                        "name": lease.get("name"),
                        "totalBalanceDue": lease.get("totalBalanceDue", 0),
                        "overdueBalance": lease.get("overdueBalance", 0),
                        "currentBalance": lease.get("currentBalance", 0),
                        "totalRecurringRent": lease.get("totalRecurringRent", 0),
                        "status": lease.get("status", "active"),
                    }
                    data_list.append(lease_item)
                    lease_status[lease.get("id")] = lease.get("status", "active")
        
        logging.info(f"Extracted {len(data_list)} leases from API response")
        
    except Exception:
        logging.exception("Failed to process lease data")
    
    return data_list, lease_status

                                
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
  
   