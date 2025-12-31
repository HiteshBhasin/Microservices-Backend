from redis import Redis
import os, logging, sys, threading, time

# Attempt to initialize Redis client using REDIS_URL from environment variables.
# If REDIS_URL is not set, the application will continue running without Redis.
try:
    _redis_url = os.getenv("REDIS_URL")
    if _redis_url:
        # Create Redis client with automatic string decoding
        redis = Redis.from_url(_redis_url, decode_responses=True)
    else:
        redis = None
        logging.warning(
            "REDIS_URL environment variable not set; running without Redis cache."
        )
except ModuleNotFoundError:
    # Redis package is not installed — disable Redis features gracefully
    Redis = None
    redis = None
    logging.warning(
        "redis package not installed — application will continue without Redis caching."
    )


def _redis_helper(prefix: str):
    """
    Retrieve all cached JSON values whose keys start with the given prefix.

    Args:
        prefix: Redis key prefix (e.g., 'tasks', 'users')

    Returns:
        List of cached objects, or an empty list if Redis is unavailable or an error occurs.
    """
    keys = []
    try:
        if redis:
            # Scan Redis for keys matching the prefix
            for key in redis.scan_iter(f"{prefix}:*"):
                keys.append(key)

            # Fetch JSON values for each matching key
            result = []
            for key in keys:
                item = redis.json().get(key)
                result.append(item)

            return result

        return []
    except Exception:
        logging.exception("Failed to retrieve cached data from Redis")
        return []


def connectam_user_info(data: dict, ttl: int = 60):
    """
    Cache Connecteam user data in Redis using RedisJSON with a TTL.

    Args:
        data: Dictionary of Redis keys mapped to user objects.
        ttl: Time-to-live for cached entries in seconds.

    Returns:
        True if caching succeeds or Redis is disabled, False otherwise.
    """
    if len(data) == 0 and not isinstance(redis, Redis):
        return False

    try:
        if redis:
            # Use pipeline for efficient batch writes
            pipeline = redis.pipeline()
            for key, value in data.items():
                pipeline.json().set(key, "$", value)
                pipeline.expire(key, ttl)

            pipeline.execute()
            logging.info("Cached %d user records to Redis", len(data))

        return True
    except Exception:
        logging.exception("Failed to cache user data to Redis")
        return False


def retriev_connectam_user_info(user_info_key: str):
    """
    Retrieve cached Connecteam user information from Redis.

    Args:
        user_info_key: Unique identifier for the cached user.

    Returns:
        Cached user object if found, otherwise None.
    """
    if not isinstance(redis, Redis):
        return None

    try:
        if redis:
            key = f"property:{user_info_key}"
            cached = redis.json().get(key)

            if cached:
                logging.debug("Cache hit for user %s", user_info_key)
                return cached

            logging.debug("Cache miss for user %s", user_info_key)
            return None
    except Exception:
        logging.exception("Failed to retrieve user data from Redis")
        return None


def background_refresh_tasks(data_fetch_fn, interval_minutes: int = 60):
    """
    Start a background thread that periodically refreshes cached tasks data.

    Args:
        data_fetch_fn: Callable that fetches fresh task data.
        interval_minutes: Refresh interval in minutes.

    Returns:
        The daemon thread responsible for background refresh.
    """
    def refresh_loop():
        while True:
            try:
                # Wait for the configured refresh interval
                time.sleep(interval_minutes * 60)

                logging.info("Background: Refreshing tasks cache...")
                fresh_data = data_fetch_fn()

                if fresh_data:
                    connectam_user_info(fresh_data, ttl=3600)
                    logging.info(
                        "Background: task cache refreshed with %d records",
                        len(fresh_data),
                    )
                else:
                    logging.warning(
                        "Background: No fresh task data returned from fetch function"
                    )
            except Exception:
                logging.exception("Background task refresh failed (will retry)")

    # Run as a daemon thread so it does not block application shutdown
    thread = threading.Thread(target=refresh_loop, daemon=True)
    thread.start()

    logging.info(
        "Started background task refresh thread (every %d minutes)",
        interval_minutes,
    )
    return thread


def start_background_refresh(task_fetch_fn, tasks_interval: int = 30):
    """
    Initialize background refresh thread(s) for task caching.

    Args:
        tasks_fetch_fn: Callable that fetches task data.
        task_interval: Refresh interval in minutes.

    Returns:
        The background refresh thread instance.
    """
    tasks_info_thread = background_refresh_tasks(
        task_fetch_fn, interval_minutes=tasks_interval
    )
    return tasks_info_thread
