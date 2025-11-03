import os
import sys
import json
import requests
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv



load_dotenv()

# FastMCP instance for Connecteam
mcp = FastMCP("connectteam_server")


@mcp.tool()
def retrieve_tenants():
    """Retrieve tenant data from the DoorLoop API"""
    api_key = os.getenv("CONNECTTEAM_API_KEY")
    if not api_key:
        return {"error": "connecteam not found in environment variables"}

    base_url = os.getenv("CONNECTEAM_API_BASE", "https://app.connecteam.com")
    endpoint = f"{base_url.rstrip('/')}/users/v1/users?limit=10&offset=0&order=asc&userStatus=active"
    headers = {
        "x-api-key": api_key,
        "accept": "application/json",
        "content-type": "application/json",
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
    
# --- Connecteam task CRUD MCP tools (append-only) ---------------------------------
@mcp.tool()
def list_tasks(status: str = "all", limit: int = 10, offset: int = 0, taskboard_id: str | None = None):
    """List tasks with simple pagination and status filter."""
    api_key = os.getenv("CONNECTTEAM_API_KEY")
    if not api_key:
        return {"error": "CONNECTTEAM_API_KEY not found in environment variables"}

    # Use provided taskboard_id or fallback to environment variable
    if not taskboard_id:
        taskboard_id = os.getenv("CONNECTEAM_TASKBOARD_ID")
    
    if not taskboard_id:
        return {"error": "taskboard_id is required. Provide it as parameter or set CONNECTEAM_TASKBOARD_ID environment variable"}

    base_url = os.getenv("CONNECTTEAM_API_BASE", "https://api.connecteam.com")
    # Correct URL format: https://api.connecteam.com/tasks/v1/taskboards/taskBoardId/tasks?status=all&limit=10&offset=0
    endpoint = f"{base_url.rstrip('/')}/tasks/v1/taskboards/{taskboard_id}/tasks"
    params = {"status": status, "limit": limit, "offset": offset}
    headers = {"x-api-key": api_key, "accept": "application/json"}
    try:
        resp = requests.get(endpoint, headers=headers, params=params, timeout=10)
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}

    try:
        return resp.json()
    except Exception:
        return {"status": resp.status_code, "body_snippet": resp.text[:1000]}


@mcp.tool()
def get_task(task_id: str):
    """Get a single task by id."""
    api_key = os.getenv("CONNECTTEAM_API_KEY")
    if not api_key:
        return {"error": "CONNECTTEAM_API_KEY not found in environment variables"}

    base_url = os.getenv("CONNECTTEAM_API_BASE", "https://api.connecteam.com")
    endpoint = f"{base_url.rstrip('/')}/tasks/v1/tasks/{task_id}"
    headers = {"x-api-key": api_key, "accept": "application/json"}
    try:
        resp = requests.get(endpoint, headers=headers, timeout=10)
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}

    try:
        return resp.json()
    except Exception:
        return {"status": resp.status_code, "body_snippet": resp.text[:1000]}


@mcp.tool()
def create_task(payload: dict):
    """Create a task. `payload` should be the task JSON body per Connecteam API."""
    api_key = os.getenv("CONNECTTEAM_API_KEY")
    if not api_key:
        return {"error": "CONNECTTEAM_API_KEY not found in environment variables"}

    base_url = os.getenv("CONNECTTEAM_API_BASE", "https://api.connecteam.com")
    endpoint = f"{base_url.rstrip('/')}/tasks/v1/tasks"
    headers = {"x-api-key": api_key, "accept": "application/json", "content-type": "application/json"}
    try:
        resp = requests.post(endpoint, headers=headers, json=payload, timeout=10)
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}

    try:
        return resp.json()
    except Exception:
        return {"status": resp.status_code, "body_snippet": resp.text[:1000]}


@mcp.tool()
def update_task(task_id: str, payload: dict):
    """Update a task. Uses PUT (if the API supports PATCH, change method accordingly)."""
    api_key = os.getenv("CONNECTTEAM_API_KEY")
    if not api_key:
        return {"error": "CONNECTTEAM_API_KEY not found in environment variables"}

    base_url = os.getenv("CONNECTTEAM_API_BASE", "https://api.connecteam.com")
    endpoint = f"{base_url.rstrip('/')}/tasks/v1/tasks/{task_id}"
    headers = {"x-api-key": api_key, "accept": "application/json", "content-type": "application/json"}
    try:
        resp = requests.put(endpoint, headers=headers, json=payload, timeout=10)
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}

    try:
        return resp.json()
    except Exception:
        return {"status": resp.status_code, "body_snippet": resp.text[:1000]}


@mcp.tool()
def delete_task(task_id: str):
    """Delete a task by id."""
    api_key = os.getenv("CONNECTTEAM_API_KEY")
    if not api_key:
        return {"error": "CONNECTTEAM_API_KEY not found in environment variables"}

    base_url = os.getenv("CONNECTTEAM_API_BASE", "https://api.connecteam.com")
    endpoint = f"{base_url.rstrip('/')}/tasks/v1/tasks/{task_id}"
    headers = {"x-api-key": api_key, "accept": "application/json"}
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


@mcp.tool()
def list_taskboards():
    """List all available taskboards to help discover taskboard IDs."""
    api_key = os.getenv("CONNECTTEAM_API_KEY")
    if not api_key:
        return {"error": "CONNECTTEAM_API_KEY not found in environment variables"}

    base_url = os.getenv("CONNECTTEAM_API_BASE", "https://api.connecteam.com")
    endpoint = f"{base_url.rstrip('/')}/tasks/v1/taskboards"
    headers = {"x-api-key": api_key, "accept": "application/json"}
    try:
        resp = requests.get(endpoint, headers=headers, timeout=10)
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}

    try:
        return resp.json()
    except Exception:
        return {"status": resp.status_code, "body_snippet": resp.text[:1000]}




if __name__ == "__main__":
    # Run the FastMCP server using stdio transport. This keeps the process
    # alive and exposes the defined @mcp.tool() functions to MCP clients.
    mcp.run(transport="stdio")
