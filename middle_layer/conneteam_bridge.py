import datetime
import logging
import sys
from pathlib import Path
from redis import Redis
from typing import Any
from middle_layer import connecteam_redit_layer

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

def _helper_normalize(raw_value):
    if raw_value is None:
        return []

    if isinstance(raw_value, list):
        return raw_value
    return [raw_value]

def get_users(user_id:int, get_user):
    # Check cache first
    cached_users = connecteam_redit_layer.retriev_connectam_user_info(f"users:{user_id}")
    if cached_users:
        logging.info(f"Returning cached users for user_id {user_id}")
        return cached_users
    
    resp = get_user(user_id=user_id)
    if not isinstance(resp,dict):
        return {"error": "Invalid Responce"}
    result = []
    user_data = resp.get("data",{})
    users = user_data.get("users",[])
    
    for user in users:
        fname = user.get("firstName")
        lname = user.get("lastName")
        items = ["Maintenance","Housekeeping","Inspections"]
        values = []
        for field in user.get("customFields",[]):
            raw_value = field.get("value")
            normalize = _helper_normalize(raw_value=raw_value)
       
            for item in normalize:
                if isinstance(item,dict):
                    user_item = item.get("value")
                    if user_item in items:
                        values.append(user_item)
                    
        result.append({"firstname":fname,"lastname":lname, "values":values})
    
    # Cache the result
    if result:
        cache_data = {f"users:{user_id}": result}
        connecteam_redit_layer.connectam_user_info(cache_data, ttl=1800)
    
    return result


def get_times(raw_dat, get_user=None, status=None, user_id=None, title=None, duedate=None):
    if not raw_dat or not isinstance(raw_dat, dict):
        logging.error("the data object is empty or not a dict server error possible!")
        return None
    
    # Check cache first
    cache_key = "times:all"
    cached_times = connecteam_redit_layer.retriev_connectam_user_info(cache_key)
    if cached_times:
        logging.info("Returning cached times data")
        # Apply filters to cached data if provided
        filters = _build_filters(status, user_id, title, duedate)
        if filters:
            return _apply_filters(cached_times, filters)
        return cached_times
    data = raw_dat.get("data")
    if not data:
        logging.error("No 'data' key found in raw_dat")
        logging.error(f"raw_dat keys: {list(raw_dat.keys()) if isinstance(raw_dat, dict) else 'not a dict'}")
        return None
    
    logging.debug(f"data extracted, type: {type(data)}")
    
    task_data = data.get("tasks") if isinstance(data, dict) else None
    
    if task_data is None:
        logging.error("No 'tasks' key found in data or data is not a dict")
        logging.error(f"data: {data}")
        return None
    
    logging.info(f"Task data type: {type(task_data)}, length: {len(task_data) if isinstance(task_data, (list, dict)) else 'N/A'}")
    
    if not isinstance(task_data, list):
        logging.error(f"task_data is not a list, got type: {type(task_data)}")
        return None
    
    logging.info(f"Processing {len(task_data)} tasks in get_times")
    
    if len(task_data) == 0:
        logging.warning("task_data is an empty list")
        return []
    
    user_info = task_info(task_data, get_user=get_user)
    logging.info(f"task_info returned {len(user_info) if user_info else 0} items")
    logging.debug(f"task_info returned: {user_info}")
    
    # Cache the result
    if user_info:
        cache_data = {cache_key: user_info}
        connecteam_redit_layer.connectam_user_info(cache_data, ttl=600)
        logging.info(f"Cached {len(user_info)} tasks")
    
    # Build filters dict from parameters
    filters = _build_filters(status, user_id, title, duedate)
    
    # Apply filters if provided
    if filters:
        user_info = _apply_filters(user_info, filters)
        logging.info(f"After filtering: {len(user_info) if user_info else 0} items")
    
    # Project final output to omit user_id
    projected = [
        {
            "user_name": item.get("user_name"),
            "status": item.get("status"),
            "title": item.get("title"),
            "date": item.get("date"),
        }
        for item in (user_info or [])
    ]
    
    logging.info(f"get_times returning {len(projected)} items")
    return projected


def _apply_filters(data, filters):
    """
    Apply filters to task data.
    
    Filters dict can contain:
    - status: filter by task status (str or list)
    - user_id: filter by user_id (list of user IDs)
    - title: filter by title (str, partial match)
    - duedate: filter by due date (str, exact match - ISO format YYYY-MM-DD)
    """
    if not data or not isinstance(data, list):
        return data
    
    filtered_data = data
    
    if not filters:
        return filtered_data
    
    # Filter by status
    if "status" in filters and filters["status"]:
        status_filter = filters["status"]
        status_list = status_filter if isinstance(status_filter, list) else [status_filter]
        filtered_data = [item for item in filtered_data if item.get("status") in status_list]
        logging.info(f"After status filter: {len(filtered_data)} items")
    
    # Filter by user_id (list)
    if "user_id" in filters and filters["user_id"]:
        user_id_filter = filters["user_id"]
        # Ensure it's a list
        user_id_list = user_id_filter if isinstance(user_id_filter, list) else [user_id_filter]
        filtered_data = [item for item in filtered_data if item.get("user_id") in user_id_list]
        logging.info(f"After user_id filter: {len(filtered_data)} items")
    
    # Filter by title (partial match)
    if "title" in filters and filters["title"]:
        title_filter = filters["title"].lower() if isinstance(filters["title"], str) else ""
        filtered_data = [item for item in filtered_data if title_filter in (item.get("title", "").lower())]
        logging.info(f"After title filter: {len(filtered_data)} items")
    
    # Filter by duedate (exact match)
    if "duedate" in filters and filters["duedate"]:
        duedate_filter = filters["duedate"]
        filtered_data = [item for item in filtered_data if item.get("date") == duedate_filter]
        logging.info(f"After duedate filter: {len(filtered_data)} items")
    
    return filtered_data


def _build_filters(status=None, user_id=None, title=None, duedate=None):
    """Build filters dict from individual parameters."""
    filters = {}
    
    if status is not None:
        filters["status"] = status
    
    if user_id is not None:
        # Parse comma-separated user_id list
        user_id_list = [int(uid.strip()) for uid in user_id.split(",") if uid.strip().isdigit()]
        if user_id_list:
            filters["user_id"] = user_id_list
    
    if title is not None:
        filters["title"] = title
    
    if duedate is not None:
        filters["duedate"] = duedate
    
    return filters if filters else None


def task_info(raw_data, get_user=None):
    logging.info(f"task_info called with raw_data type: {type(raw_data)}")
    
    if not isinstance(raw_data, list):
        logging.error(f"raw_data is not a list, got type: {type(raw_data)}")
        return []
    
    userdata = raw_data
    retur_data = []
    
    logging.info(f"task_info processing {len(userdata)} items")
    
    for idx, user in enumerate(userdata):
        try:
            logging.debug(f"Processing item {idx}: {user}")
            
            raw_user_ids = user.get("userIds") if isinstance(user, dict) else None
            if isinstance(raw_user_ids, list) and raw_user_ids:
                user_id = raw_user_ids[0]
            else:
                user_id = raw_user_ids
            status = user.get("status") if isinstance(user, dict) else None
            title = user.get("title") if isinstance(user, dict) else None
            due_date = user.get("dueDate") if isinstance(user, dict) else None
            
            logging.debug(f"Extracted - user_id: {user_id}, status: {status}, title: {title}, due_date: {due_date}")
            
            # Get user name from get_user function if provided
            user_name = None
            if get_user and user_id:
                try:
                    user_info = get_user(user_id=user_id)
                    if isinstance(user_info, dict):
                        user_data_resp = user_info.get("data", {})
                        users = user_data_resp.get("users", [])
                        if users:
                            first_user = users[0]
                            fname = first_user.get("firstName", "")
                            lname = first_user.get("lastName", "")
                            user_name = f"{fname} {lname}".strip()
                            logging.debug(f"Got user_name: {user_name}")
                except Exception as e:
                    logging.error(f"Error fetching user info for user_id {user_id}: {e}")
            
            if due_date is not None:
                try:
                    meaningful_date = datetime.datetime.fromtimestamp(due_date).date().isoformat()
                except Exception as e:
                    logging.error(f"Error converting due_date {due_date}: {e}")
                    meaningful_date = None
            else:
                meaningful_date = None
          
            user_data = {
                "user_id": user_id,
                "user_name": user_name,
                "status": status,
                "title": title, 
                "date": meaningful_date
            }
            logging.debug(f"Appending user_data: {user_data}")
            retur_data.append(user_data)

            
        except Exception as e:
            logging.error(f"Error processing task at index {idx}: {e}")
            continue
    
    logging.info(f"task_info returning {len(retur_data)} processed tasks")
    
    # Cache the result
    if retur_data:
        cache_data = {"tasks:all": retur_data}
        connecteam_redit_layer.connectam_user_info(cache_data, ttl=600)
        logging.info(f"Cached {len(retur_data)} tasks")
    
    return retur_data











            




    