import os
import sys
import json
import requests
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

#Try to ensure UTF-8 stdout when running as a script; ignore if unsupported.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

load_dotenv()
mcp = FastMCP("doorloop_server")

@mcp.tool()
def retrieve_tenants():
    """Retrieve tenant data from the DoorLoop API"""
    api_key = os.getenv("DOORLOOP_API_KEY")
    if not api_key:
        return {"error": "DOORLOOP_API_KEY not found in environment variables"}

    base_url = os.getenv("DOORLOOP_API_BASE", "https://app.doorloop.com")
    endpoint =f"{base_url.rstrip('/')}/api/tenants"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "accept": "application/json",
        "content-type": "application/json"
    }
    try: # If the response is JSON return that, otherwise include a short text body for debugging
        response = requests.get(endpoint, headers=headers, timeout=10)
        content_type = response.headers.get("Content-Type", "")
        if response.ok:
            if "application/json" in content_type:
                return response.json()  # Try to parse JSON even if header is missing
            try:
                return response.json()
            except Exception:
                return {"status": response.status_code, "body": response.text[:1000]}
        else:
            return {
                "error": "Failed to fetch tenants",
                "status": response.status_code,
                "response": response.json(),
            }
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}

@mcp.tool()
def retrieve_a_tenants(id):
    """Retrieve tenant data from the DoorLoop API"""
    api_key = os.getenv("DOORLOOP_API_KEY")
    if not api_key:
        return {"error": "DOORLOOP_API_KEY not found in environment variables"}

    base_url = os.getenv("DOORLOOP_API_BASE", "https://app.doorloop.com")
    endpoint =f"{base_url.rstrip('/')}/api/tenants/{id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "accept": "application/json",
        "content-type": "application/json"
    }
    try: # If the response is JSON return that, otherwise include a short text body for debugging
        response = requests.get(endpoint, headers=headers, timeout=10)
        content_type = response.headers.get("Content-Type", "")
        if response.ok:
            if "application/json" in content_type:
                return response.json()  # Try to parse JSON even if header is missing
            try:
                return response.json()
            except Exception:
                return {"status": response.status_code, "body": response.text[:1000]}
        else:
            return {
                "error": "Failed to fetch tenants",
                "status": response.status_code,
                "response": response.json,
            }
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}

@mcp.tool()
def retrieve_leases():
    """Retrieve tenant data from the DoorLoop API"""
    api_key = os.getenv("DOORLOOP_API_KEY")
    if not api_key:
        return {"error": "DOORLOOP_API_KEY not found in environment variables"}

    base_url = os.getenv("DOORLOOP_API_BASE", "https://app.doorloop.com")
    endpoint =f"{base_url.rstrip('/')}/api/leases"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "accept": "application/json",
        "content-type": "application/json"
    }
    try: # If the response is JSON return that, otherwise include a short text body for debugging
        response = requests.get(endpoint, headers=headers, timeout=10)
        content_type = response.headers.get("Content-Type", "")
        if response.ok:
            if "application/json" in content_type:
                return response.json()  # Try to parse JSON even if header is missing
            try:
                return response.json()
            except Exception:
                return {"status": response.status_code, "body": response.text[:1000]}
        else:
            return {
                "error": "Failed to fetch tenants",
                "status": response.status_code,
                "response": response.json(),
            }
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}



def id_retriever(name:str):
    guest_list_wrapper = retrieve_tenants() 
    tenant_list = guest_list_wrapper.get("data", [])  # default to empty list if missing
   
    for tenants in tenant_list:
       if not name:
           print(tenants.get("firstName"))
       else:
           if tenants.get("fullName")==name:
               return tenants.get("id")
    if name:
        print("no tenant found of this name")
            







# if __name__ == "__main__":
#     result = retrieve_tenants()
#     individiual_result = retrieve_a_tenants("65b16b77300d35d0d1a06be8")
#     lease_result = retrieve_leases()
#     try:
#         print(json.dumps(individiual_result, indent=2, ensure_ascii=False))
#     except Exception:
#         print(individiual_result)
