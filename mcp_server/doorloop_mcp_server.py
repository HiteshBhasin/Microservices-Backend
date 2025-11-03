import os
import sys
import json
import requests
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from utils.Report_gen import DoorLoopReportGenerator
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
def generate_report():
    """Fetch DoorLoop balancesheet (safe, debuggable)."""
    import os, requests
    api_key = os.getenv("DOORLOOP_API_KEY")
    if not api_key:
        return {"error": "DOORLOOP_API_KEY not found in environment variables"}

    base_url = os.getenv("DOORLOOP_API_BASE", "https://app.doorloop.com")
    # NOTE: verify the exact report path and query parameter names with DoorLoop docs
    endpoint = f"{base_url.rstrip('/')}/api/reports/balance-sheet-summary?filter_accountingMethod=CASH"
    headers = {"Authorization": f"Bearer {api_key}", "accept": "application/json"}

    try:
        resp = requests.get(endpoint, headers=headers, timeout=15)
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}

    # Basic debug info
    result = {"status": resp.status_code, "content_type": resp.headers.get("Content-Type", "")}

    # Try parse JSON
    try:
        j = resp.json()
    except ValueError:
        # response not JSON
        result["body"] = resp.text[:2000]
        return result

    # If status not OK, return JSON body for debugging
    if not resp.ok:
        result["body_json"] = j
        return result

    # Try to normalize with pandas if available
    try:
        import pandas as pd
    except ModuleNotFoundError:
        # return raw JSON when pandas not installed
        return {"result": j, "note": "pandas not installed; install it to normalize"}

    # Choose the data payload we'll normalize (try likely keys)
    data = None
    if isinstance(j, dict):
        for candidate in ("rent_roll", "data", "items", "results", "tenants", "report", "rows"):
            if candidate in j and isinstance(j[candidate], (list, dict)):
                data = j[candidate]
                break
        if data is None:
            # pick first list value if any
            for v in j.values():
                if isinstance(v, list):
                    data = v
                    break
    else:
        data = j

    # Normalize safely
    try:
        if data is None:
            df = pd.DataFrame()  # empty
        else:
            df = pd.json_normalize(data)
            df = df.rename(columns={"undepositedFundsSplits.ePaymentsTotal":"undeposited ePayments",
                                    "undepositedFundsSplits.manualEntriesTotal":"undeposited manualEntries"})
            print(df.columns)
            # Fix: fillna needs to be assigned back or use inplace=True
            df = df.fillna(0)  # Returns new DataFrame with NaN replaced by 0
            # Alternative: df.fillna(0, inplace=True)  # Modifies original DataFrame
        return generate_pdf(df,"Doorloop-Balance-Sheet.pdf", "Doorloop Balance Sheet Report")
    except Exception as exc:
        return {"error": "Normalization failed", "exception": str(exc), "raw": j}

@mcp.tool()
def generate_pdf(report, name: str, title: str):
    """Generate PDF report from DataFrame data."""
    if hasattr(report, 'values') and hasattr(report, 'columns'):
        # Create report generator instance with extra wide columns
        generator = DoorLoopReportGenerator(
            col_width=4.5,           # Even wider columns
            row_height=1.0,          # Taller rows for better spacing
            font_size=11,            # Larger body text size
            header_font_size=12,     # Larger header text size
            max_text_width=40        # More characters before text wrapping
        )
        
        # Generate the PDF with Nest Host branding
        report_info = generator.generate_pdf(
            df=report, 
            filename=name,
            title=f"Nest Host - {title}"
        )
        return report_info
    else:
        return {"error": "Invalid report data - not a pandas DataFrame"}

if __name__ == "__main__":
    try:
        # Run the FastMCP server using stdio transport. This keeps the process
        # alive and exposes the defined @mcp.tool() functions to MCP clients.
        mcp.run(transport="stdio")
      
    except Exception as e:
        print(f"Error: {e}")