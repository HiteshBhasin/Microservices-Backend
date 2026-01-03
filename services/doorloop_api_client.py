"""
Pure DoorLoop API client - NO MCP, just direct HTTP requests.
Use this for in-process calls to avoid MCP stdio pipe issues.
"""
import os, logging
from typing import Any, cast
from pydantic import BaseModel, SecretStr
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
try:
    from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
except Exception:  # Fallback if fastapi-mail not installed
    FastMail = None
    MessageSchema = None
    ConnectionConfig = None
    MessageType = None

load_dotenv()

try:
    from services import doorloop_services as services
except Exception as e:
    logging.exception(" The Mcp service file never imported")
    
    
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
    
def retrieve_profit_loss() -> Dict[str, Any]:
    """Retrieve communications from DoorLoop API."""
    endpoint = f"{_get_base_url()}/api/reports/profit-and-loss-summary?filter_accountingMethod=CASH"
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


class EmailSchema(BaseModel):
    email: List[str]


def _is_valid_email(addr: str) -> bool:
    return isinstance(addr, str) and "@" in addr and "." in addr


# Mail configuration using environment variables; disable if invalid
_MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
_MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
_MAIL_FROM = os.getenv("MAIL_FROM", _MAIL_USERNAME)
_MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
_MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")

_MAIL_ENABLED = FastMail is not None and _is_valid_email(_MAIL_FROM)

if _MAIL_ENABLED and ConnectionConfig is not None:
    try:
        conf = ConnectionConfig(
            MAIL_USERNAME=_MAIL_USERNAME,
            MAIL_PASSWORD=SecretStr(_MAIL_PASSWORD),
            MAIL_FROM=_MAIL_FROM,
            MAIL_PORT=_MAIL_PORT,
            MAIL_SERVER=_MAIL_SERVER,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
        )
    except Exception:
        logging.warning("Mail configuration invalid; disabling email notifications")
        _MAIL_ENABLED = False
        conf = None
else:
    conf = None


def build_message(recipients: List[str], subject: str = " ", body: str = "") -> Optional[Any]:
    """Construct a MessageSchema; returns None if mail disabled or invalid recipients."""
    if not _MAIL_ENABLED or MessageSchema is None or MessageType is None:
        return None

    valid_recipients = [r for r in recipients if _is_valid_email(r)]
    if not valid_recipients:
        return None

    return MessageSchema(
        subject=subject,
        recipients=valid_recipients,  # type: ignore[arg-type]
        body=body,
        subtype=MessageType.html,
    )


async def create_tenant(
    first_name: str,
    last_name: str,
    middle_name: Optional[str] = None,
    gender: Optional[str] = None,
    additional_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a new tenant in DoorLoop API.
    
    Args:
        first_name: Tenant's first name (required)
        last_name: Tenant's last name (required)
        middle_name: Tenant's middle name (optional)
        gender: Gender - MALE, FEMALE, or PREFER_NOT_TO_SAY (optional)
        additional_data: Additional tenant fields as dict (optional)
        
    Returns:
        Dict containing the created tenant data or error information
    """
    endpoint = f"{_get_base_url()}/api/tenants"
    payload = {
        "firstName": first_name,
        "lastName": last_name,
    }
    
    if middle_name:
        payload["middleName"] = middle_name
    if gender:
        payload["gender"] = gender
    if additional_data:
        payload.update(additional_data)

    try:
        response = requests.post(endpoint, json=payload, headers=_get_headers(), timeout=10)
        if response.ok:
            print(response)
            if _MAIL_ENABLED and conf:
                template = f"""
                    <html>
                    <body>
                        <p>A new tenant was created: {payload}</p>
                    </body>
                    </html>
                """
                message = build_message(['bhasinsukh@gmail.com'], "New Tenant Created", template)
                if message:
                    fm = FastMail(cast(ConnectionConfig, conf))  # type: ignore[operator]
                    await fm.send_message(message=message)
                    print(message)

            return response.json()
        else:
            return {
                "error": "Failed to create tenant",
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
    "create_tenant",
]
