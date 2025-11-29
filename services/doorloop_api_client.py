"""
Pure DoorLoop API client - NO MCP, just direct HTTP requests.
Use this for in-process calls to avoid MCP stdio pipe issues.
"""
import os
import requests
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()


def _get_headers() -> Dict[str, str]:
    """Get common headers for DoorLoop API requests."""
    api_key = os.getenv("DOORLOOP_API_KEY")
    if not api_key:
        raise ValueError("DOORLOOP_API_KEY not found in environment variables")
    
    return {
        "Authorization": f"Bearer {api_key}",
        "accept": "application/json",
        "content-type": "application/json"
    }


def _get_base_url() -> str:
    """Get base URL for DoorLoop API."""
    return os.getenv("DOORLOOP_API_BASE", "https://app.doorloop.com").rstrip('/')


def retrieve_tenants() -> Dict[str, Any]:
    """Retrieve all tenants from DoorLoop API."""
    endpoint = f"{_get_base_url()}/api/tenants"
    try:
        response = requests.get(endpoint, headers=_get_headers(), timeout=10)
        if response.ok:
            return response.json()
        else:
            return {
                "error": "Failed to fetch tenants",
                "status": response.status_code,
                "response": response.json() if response.headers.get("Content-Type", "").startswith("application/json") else response.text[:1000],
            }
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}


def retrieve_properties() -> Dict[str, Any]:
    """Retrieve all properties from DoorLoop API."""
    endpoint = f"{_get_base_url()}/api/properties"
    try:
        response = requests.get(endpoint, headers=_get_headers(), timeout=10)
        if response.ok:
            return response.json()
        else:
            return {
                "error": "Failed to fetch properties",
                "status": response.status_code,
                "response": response.json() if response.headers.get("Content-Type", "").startswith("application/json") else response.text[:1000],
            }
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}


def retrieve_properties_id(property_id: str) -> Dict[str, Any]:
    """Retrieve a single property by ID from DoorLoop API."""
    endpoint = f"{_get_base_url()}/api/properties/{property_id}"
    try:
        response = requests.get(endpoint, headers=_get_headers(), timeout=10)
        if response.ok:
            return response.json()
        else:
            return {
                "error": f"Failed to fetch property {property_id}",
                "status": response.status_code,
                "response": response.json() if response.headers.get("Content-Type", "").startswith("application/json") else response.text[:1000],
            }
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}


def retrieve_leases() -> Dict[str, Any]:
    """Retrieve all leases from DoorLoop API."""
    endpoint = f"{_get_base_url()}/api/leases"
    try:
        response = requests.get(endpoint, headers=_get_headers(), timeout=10)
        if response.ok:
            return response.json()
        else:
            return {
                "error": "Failed to fetch leases",
                "status": response.status_code,
                "response": response.json() if response.headers.get("Content-Type", "").startswith("application/json") else response.text[:1000],
            }
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}


def retrieve_a_tenants(tenant_id: str) -> Dict[str, Any]:
    """Retrieve a single tenant by ID from DoorLoop API."""
    endpoint = f"{_get_base_url()}/api/tenants/{tenant_id}"
    try:
        response = requests.get(endpoint, headers=_get_headers(), timeout=10)
        if response.ok:
            return response.json()
        else:
            return {
                "error": f"Failed to fetch tenant {tenant_id}",
                "status": response.status_code,
                "response": response.json() if response.headers.get("Content-Type", "").startswith("application/json") else response.text[:1000],
            }
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}


def retrieve_doorloop_communication() -> Dict[str, Any]:
    """Retrieve communications from DoorLoop API."""
    endpoint = f"{_get_base_url()}/api/communications"
    try:
        response = requests.get(endpoint, headers=_get_headers(), timeout=10)
        if response.ok:
            return response.json()
        else:
            return {
                "error": "Failed to fetch communications",
                "status": response.status_code,
                "response": response.json() if response.headers.get("Content-Type", "").startswith("application/json") else response.text[:1000],
            }
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}


def retrieve_doorloop_tasks() -> Dict[str, Any]:
    """Retrieve communications from DoorLoop API."""
    endpoint = f"{_get_base_url()}/api/tasks"
    try:
        response = requests.get(endpoint, headers=_get_headers(), timeout=10)
        if response.ok:
            return response.json()
        else:
            return {
                "error": "Failed to fetch communications",
                "status": response.status_code,
                "response": response.json() if response.headers.get("Content-Type", "").startswith("application/json") else response.text[:1000],
            }
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}

def retrieve_doorloop_lease_payment() -> Dict[str, Any]:
    """Retrieve communications from DoorLoop API."""
    endpoint = f"{_get_base_url()}/api/lease-payments"
    try:
        response = requests.get(endpoint, headers=_get_headers(), timeout=10)
        if response.ok:
            return response.json()
        else:
            return {
                "error": "Failed to fetch communications",
                "status": response.status_code,
                "response": response.json() if response.headers.get("Content-Type", "").startswith("application/json") else response.text[:1000],
            }
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}
    
def retrieve_doorloop_expenses() -> Dict[str, Any]:
    """Retrieve communications from DoorLoop API."""
    endpoint = f"{_get_base_url()}/api/expenses"
    try:
        response = requests.get(endpoint, headers=_get_headers(), timeout=10)
        if response.ok:
            return response.json()
        else:
            return {
                "error": "Failed to fetch communications",
                "status": response.status_code,
                "response": response.json() if response.headers.get("Content-Type", "").startswith("application/json") else response.text[:1000],
            }
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}
__all__ = [
    "retrieve_tenants",
    "retrieve_properties",
    "retrieve_properties_id",
    "retrieve_leases",
    "retrieve_a_tenants",
    "retrieve_doorloop_communication",
]
