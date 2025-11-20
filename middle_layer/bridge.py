import logging
import sys
from pathlib import Path
from typing import Dict

# Ensure the repository root is on sys.path so top-level packages import reliably
PROJECT_ROOT = Path(__file__).absolute().parent.parent

if str(PROJECT_ROOT) not in sys.path:
 	sys.path.insert(0, str(PROJECT_ROOT))


try:
	# Import after adjusting sys.path
	from mcp_server import doorloop_mcp_server
except Exception as exc:
	raise ImportError(f"Failed to import mcp_server. Ensure project root is correct: {PROJECT_ROOT}\nOriginal error: {exc}")

def get_doorloop_tenants():
    try:
        respobj = doorloop_mcp_server.retrieve_tenants()
        data = respobj['data']
        newobj = {}
        for i in range(len(data)):
            newobj["fistname"]=data[i]['firstName']
            newobj["lastname"]=data[i]['firstName']
            print(newobj)
    
    except:
        logging.error(" an error occir please resolve first")


if __name__ == "__main__":
	get_doorloop_tenants()

