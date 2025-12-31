from redis import Redis
import os , logging , sys , threading, time

try:
    _redis_url = os.getenv("REDIS_URL")
    if _redis_url:
        redis = Redis.from_url(_redis_url, decode_responses=True)
    else:
        redis = None
        logging.warning("REDIS_URL environment variable not set; continuing without Redis connection.")
except ModuleNotFoundError:
    Redis = None
    redis = None
    logging.warning("redis package not installed in the active Python environment — bridge.py will continue without Redis. Install 'redis' into your environment to enable Redis features.")

def _redis_helper(prefix:str):
    keys = []
    try:
        if redis:
            for key in redis.scan_iter(f"{prefix}:*"):
                keys.append(key)
            result = []
            for key in keys:
                item = redis.json().get(key)
                result.append(item)
        return result
    except Exception as e:
        logging.exception("Failed to retrieve cached data")
        return []

def connectam_user_info(data:dict ,  ttl:int=60):
    if len(data)==0 and not isinstance(redis,Redis):
        return False
    try:
        if redis:
            pipeline = redis.pipeline()
            for key, value in data.items():
                pipeline.json().set(key,"$", value)
                pipeline.expire(key,ttl)
            
            pipeline.execute()
            logging.info("Cached %d properties to Redis", len(data))
        return True
    except Exception as e:
        logging.exception("Failed to retrieve cached data")
        return []
                
def retriev_connectam_user_info(user_info_key:str):
    """Retrieve cached user_ifo data from Redis (1 lookup instead of API call)."""
    if not isinstance(redis,Redis):
        return None
    
    try:
        if redis:
            key = f"property:{user_info_key}"
            cached = redis.json().get(key)
        if cached:
            logging.debug("Cache hit for property %s", user_info_key)
            return cached
        logging.debug("Cache miss for property %s", user_info_key)
        return None
    except Exception:
        logging.exception("Failed to retrieve property from Redis")
        return None

def background_refresh_tenants(data_fetch_fn, interval_minutes: int = 60):
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
                    connectam_user_info(fresh_data, ttl=3600)
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