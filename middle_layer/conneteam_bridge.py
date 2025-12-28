import logging
import sys
from pathlib import Path
# from redis import Redis
from typing import Any

# Ensure the repository root is on sys.path so top-level packages import reliably
PROJECT_ROOT = Path(__file__).absolute().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    # Import pure API client (NO MCP - just direct HTTP requests)
    from services import connecteam_api_client as connecteam_api
except Exception as exc:
    raise ImportError(f"Failed to import connecteam_api_client. Ensure project root is correct: {PROJECT_ROOT}\nOriginal error: {exc}")

def retrieve_data(*args):
   try:
       # If a single object was passed, return it directly
       if len(args) == 1:
           return args[0]
       return args
   except Exception as e:
       logging.exception(f" An internal error has occur please check the server,{e}")
       return None

def get_job(raw_data):
    if len(raw_data)==0:
        logging.error(f"There is nothing in the data file please check the Server")
    try:
        data = raw_data.get("data")
        task_data = data.get("tasks")
        if isinstance(task_data, list):
            print(task_data[2]["title"])

    except Exception as e:
        logging.exception(f" An internal error has occur please check the server,{e}")
        return None
    
    