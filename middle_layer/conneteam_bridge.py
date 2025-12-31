import datetime
import logging
import sys
from pathlib import Path
from redis import Redis
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

def _helper_normalize(raw_value):
    if raw_value is None:
        return []

    if isinstance(raw_value, list):
        return raw_value
    return [raw_value]

def get_users(user_id:int, get_user):
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
    return result


def get_times(raw_dat):
    if not raw_dat or not isinstance(raw_dat, dict):
        logging.error("the data object is empty server error possible!")
        return None
    
    data = raw_dat.get("data", {})
    task_data = data.get("tasks", [])
    if isinstance(task_data,list):
        user_info = task_info(task_data)
    
    return user_info


def task_info(raw_data):
    # raw_data 
    userdata = raw_data
    user_data = {}
    retur_data = []
    if isinstance(userdata, list):
        for user in userdata:
            
            user_id = user.get("userIds")
            status = user.get("status")
            title = user.get("title") 
            due_date = user.get("dueDate")
            
            if due_date is not None:
                meaningful_date = datetime.datetime.fromtimestamp(due_date).date().isoformat()
          
            user_data = {"user_id": user_id,"status":status,  "title":title, "date":meaningful_date}
            retur_data.append(user_data)
    return retur_data











            




    