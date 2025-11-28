from redis import Redis
from dotenv import load_dotenv
import os , logging , sys , threading, time
from pathlib import Path

load_dotenv()
try:
    redis = Redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)
except ModuleNotFoundError:
    Redis = None
    logging.warning("redis package not installed in the active Python environment — bridge.py will continue without Redis. Install 'redis' into your environment to enable Redis features.")
    

def cache_tenants_to_redis(data, ttl: int = 3600):
    """Batch cache tenant data to Redis with TTL (fast write).
    
    Uses Redis pipeline for fast bulk writes.
    ttl: time-to-live in seconds (default 1 hour).
    """
    if not data:
        logging.warning("Cannot cache: data is empty or Redis unavailable")
        return False
    
    try:
        pipe = redis.pipeline()
        for i, tenant in enumerate(data):
            key = f"tenant:{i}"
            pipe.json().set(key, "$", tenant)
            pipe.expire(key, ttl)
        
        results = pipe.execute()
        logging.info("Cached %d tenants to Redis", len(data))
        return results
    except Exception:
        logging.exception("Failed to cache tenants to Redis")
        return None


def get_cached_tenants(start: int = 0, end: int =0):
    """Retrieve cached tenants from Redis (fast read).
    Returns list of tenants from Redis cache.
    """

    try:
        # Get all tenant keys
        keys = redis.keys("tenants:*")
        if not keys:
            logging.info("No cached tenants found in Redis")
            return []
        
        # Batch fetch (MGET for fast reads)
        tenants = redis.mget(keys) if keys else []
        logging.info("Retrieved %d tenants from Redis cache", len(tenants))
        return [t for t in tenants if t]
    except Exception:
        logging.exception("Failed to retrieve tenants from Redis")
        return []


def cache_properties_to_redis(property_data: dict, ttl: int = 3600):
    """Cache property details to Redis by property_id (fast lookups).
    
    ttl: time-to-live in seconds.
    """
    if not property_data or not isinstance(redis, Redis):
        return False
    
    try:
        pipe = redis.pipeline()
        for prop_id, prop_info in property_data.items():
            key = f"property:{prop_id}"
            pipe.json().set(key, "$", prop_info)
            pipe.expire(key, ttl)
        
        pipe.execute()
        logging.info("Cached %d properties to Redis", len(property_data))
        return True
    except Exception:
        logging.exception("Failed to cache properties to Redis")
        return False


def get_cached_property(property_id: str):
    """Retrieve cached property data from Redis (1 lookup instead of API call)."""
    if not isinstance(redis,Redis):
        return None
    
    try:
        key = f"property:{property_id}"
        cached = redis.json().get(key)
        if cached:
            logging.debug("Cache hit for property %s", property_id)
            return cached
        logging.debug("Cache miss for property %s", property_id)
        return None
    except Exception:
        logging.exception("Failed to retrieve property from Redis")
        return None


# Background refresh functions

def background_refresh_tenants(data_fetch_fn, interval_minutes: int = 30):
    """Background thread that auto-refreshes tenant cache every N minutes.
    
    Args:
        data_fetch_fn: Function to call to fetch fresh tenant data (e.g., get_doorloop_tenants).
        interval_minutes: How often to refresh (default 30 minutes).
    """
    def refresh_loop():
        while True:
            try:
                time.sleep(interval_minutes * 60)  # Wait N minutes
                logging.info("Background: Refreshing tenant cache...")
                fresh_data = data_fetch_fn()
                if fresh_data:
                    cache_tenants_to_redis(fresh_data, ttl=3600)
                    logging.info("Background: Tenant cache refreshed with %d items", len(fresh_data))
                else:
                    logging.warning("Background: No fresh data returned from fetch function")
            except Exception:
                logging.exception("Background refresh failed (will retry)")
    
    # Start as daemon thread so it doesn't block app shutdown
    thread = threading.Thread(target=refresh_loop, daemon=True)
    thread.start()
    logging.info("Started background tenant refresh every %d minutes", interval_minutes)
    return thread


def background_refresh_properties(property_ids_fetch_fn, data_fetch_fn, interval_minutes: int = 30):
    """Background thread that auto-refreshes property cache every N minutes.
    
    Args:
        property_ids_fetch_fn: Function to call to get list of property IDs.
        data_fetch_fn: Function to call to fetch property data by ID (e.g., retrieve_properties_id).
        interval_minutes: How often to refresh (default 30 minutes).
    """
    def refresh_loop():
        while True:
            try:
                time.sleep(interval_minutes * 60)  # Wait N minutes
                logging.info("Background: Refreshing property cache...")
                property_ids = property_ids_fetch_fn()[:10]  # Limit to top 10 to avoid overload
                
                property_data = {}
                for pid in property_ids:
                    try:
                        prop_info = data_fetch_fn(pid)
                        if prop_info:
                            property_data[pid] = prop_info
                    except Exception:
                        logging.exception("Failed to fetch property %s in background", pid)
                        continue
                
                if property_data:
                    cache_properties_to_redis(property_data, ttl=3600)
                    logging.info("Background: Property cache refreshed with %d items", len(property_data))
                else:
                    logging.warning("Background: No property data to cache")
            except Exception:
                logging.exception("Background property refresh failed (will retry)")
    
    # Start as daemon thread
    thread = threading.Thread(target=refresh_loop, daemon=True)
    thread.start()
    logging.info("Started background property refresh every %d minutes", interval_minutes)
    return thread


def start_background_refresh(tenant_fetch_fn, property_ids_fn, property_fetch_fn, 
                             tenant_interval: int = 30, property_interval: int = 60):
    """Start both background refresh threads.
    
    Args:
        tenant_fetch_fn: Function to fetch fresh tenants.
        property_ids_fn: Function to get property IDs.
        property_fetch_fn: Function to fetch property data by ID.
        tenant_interval: Minutes between tenant cache refreshes.
        property_interval: Minutes between property cache refreshes.
    
    Returns:
        Tuple of (tenant_thread, property_thread) so you can manage them if needed.
    """
    tenant_thread = background_refresh_tenants(tenant_fetch_fn, interval_minutes=tenant_interval)
    property_thread = background_refresh_properties(property_ids_fn, property_fetch_fn, 
                                                     interval_minutes=property_interval)
    return tenant_thread, property_thread



