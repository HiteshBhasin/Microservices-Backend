import os
import sys
import json
import requests
from mcp.server.fastmcp import FastMCP

#Try to ensure UTF-8 stdout when running as a script; ignore if unsupported.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

def _load_dotenv_if_present(env_path: str | None = None) -> None:
    """Load environment variables from a .env file.

    Prefer the python-dotenv package if available; otherwise fall back to a small
    parser that sets missing keys from a .env in the repository root.
    """
    try:
        try:
            from dotenv import load_dotenv

            target = env_path
            if target is None:
                here = os.path.dirname(os.path.abspath(__file__))
                target = os.path.join(os.path.abspath(os.path.join(here, "..")), ".env")
            load_dotenv(target, override=False)
            return
        except Exception:
            # dotenv not installed — fall back
            pass

        if env_path is None:
            here = os.path.dirname(os.path.abspath(__file__))
            candidate = os.path.join(os.path.abspath(os.path.join(here, "..")), ".env")
        else:
            candidate = env_path

        if not os.path.exists(candidate):
            return

        with open(candidate, "r", encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = val
    except Exception:
        # silent fallback
        return


# Try loading a .env from the repo root to pick up DOORLOOP_API_KEY during dev
_load_dotenv_if_present()

mcp = FastMCP("doorloop_server")

@mcp.tool()
def retrieve_tenants():
    """Retrieve tenant data from the DoorLoop API"""
    api_key = os.getenv("DOORLOOP_API_KEY")
    if not api_key:
        return {"error": "DOORLOOP_API_KEY not found in environment variables"}

    # Allow overriding the base URL via env var for testing or future changes
    # Default to the app domain and the /api/tenants path which returns JSON for tenant lists
    base_url = os.getenv("DOORLOOP_API_BASE", "https://app.doorloop.com")
    # Default tenants endpoint is /api/tenants (matches DoorLoop examples)
    endpoint = os.getenv("DOORLOOP_TENANTS_ENDPOINT") or f"{base_url.rstrip('/')}/api/tenants"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "accept": "application/json",
        "content-type": "application/json"
    }
    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        # If the response is JSON return that, otherwise include a short text body for debugging
        content_type = response.headers.get("Content-Type", "")
        if response.ok:
            if "application/json" in content_type:
                return response.json()
            # Try to parse JSON even if header is missing
            try:
                return response.json()
            except Exception:
                return {"status": response.status_code, "body": response.text[:1000]}
        else:
            # Non-2xx responses
            body = None
            if "application/json" in content_type:
                try:
                    body = response.json()
                except Exception:
                    body = response.text[:1000]
            else:
                body = response.text[:1000]
            return {
                "error": "Failed to fetch tenants",
                "status": response.status_code,
                "response": body,
            }
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}


if __name__ == "__main__":
    result = retrieve_tenants()
    try:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception:
        print(result)
