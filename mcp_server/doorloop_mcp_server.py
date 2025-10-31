import os
import sys
import json
import requests
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Preformatted
from reportlab.lib.units import inch

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


@mcp.tool()
def generate_properties_report():
    """Generate a simple report for DoorLoop properties.

    The report includes total properties, counts by class/type, average active units and a sample.
    """
    raw = retrieve_properties()

    # normalize list
    props = []
    if isinstance(raw, dict):
        if "data" in raw and isinstance(raw["data"], list):
            props = raw["data"]
        else:
            # try to find the first list in the dict
            for v in raw.values():
                if isinstance(v, list):
                    props = v
                    break
    elif isinstance(raw, list):
        props = raw

    total = len(props)
    by_class = {}
    by_city = {}
    total_units = 0
    counted_units = 0

    for p in props:
        cls = p.get("class") or p.get("type") or "unknown"
        by_class[cls] = by_class.get(cls, 0) + 1

        addr = p.get("address", {}) if isinstance(p.get("address", {}), dict) else {}
        city = addr.get("city") or "unknown"
        by_city[city] = by_city.get(city, 0) + 1

        units = p.get("numActiveUnits")
        if isinstance(units, (int, float)):
            total_units += units
            counted_units += 1

    avg_units = (total_units / counted_units) if counted_units else 0

    report = {
        "total_properties": total,
        "by_class": by_class,
        "by_city": by_city,
        "avg_active_units": avg_units,
        "sample": props[:5],
    }
    return report


def _write_pdf_from_text(text: str, out_path: str) -> None:
    """Write a simple PDF containing `text`.

    Tries reportlab, then fpdf, then falls back to creating a blank PDF with the
    JSON/text attached using pypdf (if available).
    """
    try:
        # Use Platypus Preformatted so JSON/plain-text is wrapped and paginated nicely.
      

        doc = SimpleDocTemplate(
            out_path,
            pagesize=letter,
            leftMargin=0.5 * inch,
            rightMargin=0.5 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
        )
        styles = getSampleStyleSheet()
        pre_style = ParagraphStyle(
            "Preformatted",
            parent=styles["Normal"],
            fontName="Courier",
            fontSize=9,
            leading=11,
        )
        pre = Preformatted(text, pre_style)
        doc.build([pre])
        return
    except Exception:
        pass

    try:
        from fpdf import FPDF

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Courier", size=10)
        for line in text.splitlines():
            pdf.multi_cell(0, 5, line)
        pdf.output(out_path)
        return
    except Exception:
        pass

    # No pypdf fallback any more — require reportlab or fpdf to be installed.
    raise RuntimeError("No PDF generator available: install reportlab or fpdf")


@mcp.tool()
def generate_properties_report_pdf(out_path: str = "doorloop_properties_report.pdf"):
    """Generate properties report and write a PDF to `out_path`. Returns the report dict
    with an added `pdf_path` key on success.
    """
    report = generate_properties_report()
    text = json.dumps(report, indent=2, ensure_ascii=False)
    try:
        _write_pdf_from_text(text, out_path)
    except Exception as exc:
        return {"error": "Failed to write PDF", "exception": str(exc), "report": report}
    report["pdf_path"] = out_path
    return report


if __name__ == "__main__":
    # Run the FastMCP server using stdio transport. This keeps the process
    # alive and exposes the defined @mcp.tool() functions to MCP clients.
    # Previously this script executed helper functions at import which caused
    # the process to exit immediately when spawned by the service launcher.
    mcp.run(transport="stdio")