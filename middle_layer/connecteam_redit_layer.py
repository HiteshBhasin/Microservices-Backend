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
