import os
import sys
import json
import requests
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
# PDF libraries are imported dynamically inside the writer function so the module
# can be imported even if reportlab/fpdf are not installed in the environment.

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
            try:
                resp_json = response.json()
            except Exception:
                resp_json = None
            return {
                "error": "Failed to fetch tenants",
                "status": response.status_code,
                "response": resp_json,
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
            try:
                resp_json = response.json()
            except Exception:
                resp_json = None
            return {
                "error": "Failed to fetch tenants",
                "status": response.status_code,
                "response": resp_json,
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
            try:
                resp_json = response.json()
            except Exception:
                resp_json = None
            return {
                "error": "Failed to fetch tenants",
                "status": response.status_code,
                "response": resp_json,
            }
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}
    
@mcp.tool()
def retrieve_properties():
    """Retrieve tenant data from the DoorLoop API"""
    api_key = os.getenv("DOORLOOP_API_KEY")
    if not api_key:
        return {"error": "DOORLOOP_API_KEY not found in environment variables"}

    base_url = os.getenv("DOORLOOP_API_BASE", "https://app.doorloop.com")
    endpoint =f"{base_url.rstrip('/')}/api/properties"
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
def retrieve_properties_id(id:str):
    """Retrieve tenant data from the DoorLoop API"""
    api_key = os.getenv("DOORLOOP_API_KEY")
    if not api_key:
        return {"error": "DOORLOOP_API_KEY not found in environment variables"}

    base_url = os.getenv("DOORLOOP_API_BASE", "https://app.doorloop.com")
    endpoint =f"{base_url.rstrip('/')}/api/properties/{id}"
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
def id_retriever_prop(name:str):# this return id full name required
    """ this function retrive the full id from the first name"""
    guest_list_wrapper = retrieve_tenants() 
    tenant_list = guest_list_wrapper.get("data", [])  # default to empty list if missing
    

    for tenant in tenant_list:
        if tenant.get("name") == name:
            tenant_id = tenant.get("id")
            # Extract property IDs from prospectInfo
            interests = tenant.get("prospectInfo", {}).get("interests", [])
            property_ids = [interest.get("property") for interest in interests if "property" in interest]
            
            return {
                "tenant_id": retrieve_a_tenants(tenant_id),
                "property_ids": retrieve_properties_id(property_ids[0])
            }


# --- DoorLoop properties CRUD MCP tools (appended) -------------------------------
@mcp.tool()
def create_property(payload: dict):
    """Create a DoorLoop property. `payload` should be a dict matching the DoorLoop API."""
    api_key = os.getenv("DOORLOOP_API_KEY")
    if not api_key:
        return {"error": "DOORLOOP_API_KEY not found in environment variables"}

    base_url = os.getenv("DOORLOOP_API_BASE", "https://app.doorloop.com")
    endpoint = f"{base_url.rstrip('/')}/api/properties"
    headers = {"Authorization": f"Bearer {api_key}", "accept": "application/json", "content-type": "application/json"}
    try:
        resp = requests.post(endpoint, headers=headers, json=payload, timeout=10)
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}

    try:
        return resp.json()
    except Exception:
        return {"status": resp.status_code, "body_snippet": resp.text[:1000]}


@mcp.tool()
def update_property(prop_id: str, payload: dict):
    """Update a DoorLoop property by id."""
    api_key = os.getenv("DOORLOOP_API_KEY")
    if not api_key:
        return {"error": "DOORLOOP_API_KEY not found in environment variables"}

    base_url = os.getenv("DOORLOOP_API_BASE", "https://app.doorloop.com")
    endpoint = f"{base_url.rstrip('/')}/api/properties/{prop_id}"
    headers = {"Authorization": f"Bearer {api_key}", "accept": "application/json", "content-type": "application/json"}
    try:
        resp = requests.put(endpoint, headers=headers, json=payload, timeout=10)
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}

    try:
        return resp.json()
    except Exception:
        return {"status": resp.status_code, "body_snippet": resp.text[:1000]}

@mcp.tool()
def delete_property(prop_id: str):
    """Delete a DoorLoop property by id."""
    api_key = os.getenv("DOORLOOP_API_KEY")
    if not api_key:
        return {"error": "DOORLOOP_API_KEY not found in environment variables"}

    base_url = os.getenv("DOORLOOP_API_BASE", "https://app.doorloop.com")
    endpoint = f"{base_url.rstrip('/')}/api/properties/{prop_id}"
    headers = {"Authorization": f"Bearer {api_key}", "accept": "application/json"}
    try:
        resp = requests.delete(endpoint, headers=headers, timeout=10)
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}

    if resp.status_code in (200, 204):
        return {"ok": True, "status": resp.status_code}
    try:
        return resp.json()
    except Exception:
        return {"status": resp.status_code, "body_snippet": resp.text[:1000]}



if __name__ == "__main__":
    try:
        
        # Run the FastMCP server using stdio transport. This keeps the process
        # alive and exposes the defined @mcp.tool() functions to MCP clients.
        mcp.run(transport="stdio")
      
    except Exception as e:
        print(f"Error: {e}")