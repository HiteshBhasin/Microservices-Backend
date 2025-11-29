"""
Pure HTTP client for Connecteam API.
Eliminates MCP stdio pipe issues by making direct HTTP requests.
"""
import os
import requests
from typing import Any, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


def _get_headers() -> Dict[str, str]:
    """Build authorization headers for Connecteam API."""
    api_key = os.getenv("CONNECTTEAM_API_KEY")
    if not api_key:
        raise ValueError("CONNECTTEAM_API_KEY not found in environment variables")
    
    return {
        "x-api-key": api_key,
        "accept": "application/json",
        "content-type": "application/json",
    }


def _get_base_url() -> str:
    """Get base URL from environment."""
    return os.getenv("CONNECTTEAM_API_BASE", "https://api.connecteam.com")


def _get_taskboard_id() -> str:
    """Get taskboard ID from environment."""
    taskboard_id = os.getenv("CONNECTEAM_TASKBOARD_ID")
    if not taskboard_id:
        raise ValueError("CONNECTEAM_TASKBOARD_ID not found in environment variables")
    return taskboard_id


def retrieve_tenants() -> Dict[str, Any]:
    """Retrieve tenant/user data from Connecteam API."""
    base_url = os.getenv("CONNECTTEAM_API_BASE", "https://app.connecteam.com")
    endpoint = f"{base_url.rstrip('/')}/users/v1/users?limit=10&offset=0&order=asc&userStatus=active"
    headers = _get_headers()
    
    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}


def list_tasks(status: str = "all", limit: int = 10, offset: int = 0, taskboard_id: Optional[str] = None) -> Dict[str, Any]:
    """List tasks with pagination and status filter."""
    if not taskboard_id:
        taskboard_id = _get_taskboard_id()
    
    base_url = _get_base_url()
    endpoint = f"{base_url.rstrip('/')}/tasks/v1/taskboards/{taskboard_id}/tasks"
    params = {"status": status, "limit": limit, "offset": offset}
    headers = _get_headers()
    
    try:
        response = requests.get(endpoint, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}


def get_task(task_id: str) -> Dict[str, Any]:
    """Get a single task by ID."""
    base_url = _get_base_url()
    endpoint = f"{base_url.rstrip('/')}/tasks/v1/tasks/{task_id}"
    headers = _get_headers()
    
    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}


def create_task(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new task."""
    base_url = _get_base_url()
    endpoint = f"{base_url.rstrip('/')}/tasks/v1/tasks"
    headers = _get_headers()
    
    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}


def update_task(task_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing task."""
    base_url = _get_base_url()
    endpoint = f"{base_url.rstrip('/')}/tasks/v1/tasks/{task_id}"
    headers = _get_headers()
    
    try:
        response = requests.put(endpoint, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}


def delete_task(task_id: str) -> Dict[str, Any]:
    """Delete a task by ID."""
    base_url = _get_base_url()
    endpoint = f"{base_url.rstrip('/')}/tasks/v1/tasks/{task_id}"
    headers = _get_headers()
    
    try:
        response = requests.delete(endpoint, headers=headers, timeout=10)
        if response.status_code in (200, 204):
            return {"ok": True, "status": response.status_code}
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}


def list_taskboards() -> Dict[str, Any]:
    """List all available taskboards."""
    base_url = _get_base_url()
    endpoint = f"{base_url.rstrip('/')}/tasks/v1/taskboards"
    headers = _get_headers()
    
    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}
