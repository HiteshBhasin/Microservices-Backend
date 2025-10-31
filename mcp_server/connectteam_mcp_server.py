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
mcp.tool()
def list_tasks(limit: int = 10, offset: int = 0, status: str = "active"):
    """List tasks with simple pagination and status filter."""
    api_key = os.getenv("CONNECTTEAM_API_KEY")
    if not api_key:
        return {"error": "CONNECTTEAM_API_KEY not found in environment variables"}

    base_url = os.getenv("CONNECTTEAM_API_BASE", "https://api.connecteam.com")
    endpoint = f"{base_url.rstrip('/')}/tasks/v1/tasks"
    params = {"limit": limit, "offset": offset, "status": status}
    headers = {"x-api-key": api_key, "accept": "application/json"}
    try:
        resp = requests.get(endpoint, headers=headers, params=params, timeout=10)
    except requests.exceptions.RequestException as exc:
        return {"error": "Request failed", "exception": str(exc)}

    try:
        return resp.json()
    except Exception:
        return {"status": resp.status_code, "body_snippet": resp.text[:1000]}


mcp.tool()
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


mcp.tool()
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


mcp.tool()
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


mcp.tool()
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
def generate_tasks_report(limit: int = 100):
    """Generate a simple tasks report from Connecteam.

    The report includes total count, counts by status, and top assignees.
    """
    # Fetch tasks (single page up to `limit`)
    raw = list_tasks(limit=limit, offset=0)

    # Try to normalize the task list from common response shapes
    tasks = []
    if isinstance(raw, dict):
        # common shapes: {'data': {'tasks': [...]}} or {'data': [...]}
        if "data" in raw:
            data = raw["data"]
            if isinstance(data, dict) and "tasks" in data:
                tasks = data["tasks"]
            elif isinstance(data, list):
                tasks = data
            else:
                # unknown, try to find the first list inside
                for v in data.values() if isinstance(data, dict) else []:
                    if isinstance(v, list):
                        tasks = v
                        break
        elif "tasks" in raw and isinstance(raw["tasks"], list):
            tasks = raw["tasks"]
    elif isinstance(raw, list):
        tasks = raw

    report = {"total": len(tasks), "by_status": {}, "by_assignee": {}, "sample": tasks[:5]}

    for t in tasks:
        # status
        st = t.get("status") or t.get("taskStatus") or "unknown"
        report["by_status"][st] = report["by_status"].get(st, 0) + 1

        # assignees: could be 'assignedTo' (single) or 'assignees' (list)
        assignees = []
        if "assignedTo" in t and t.get("assignedTo"):
            assignees = [t.get("assignedTo")]
        elif "assignees" in t and isinstance(t.get("assignees"), list):
            # items may be dicts or ids
            for a in t.get("assignees", []):
                if isinstance(a, dict):
                    assignees.append(a.get("userId") or a.get("id") or a.get("email") or str(a))
                else:
                    assignees.append(str(a))
        for a in assignees:
            report["by_assignee"][a] = report["by_assignee"].get(a, 0) + 1

    # Sort top assignees
    top_assignees = sorted(report["by_assignee"].items(), key=lambda x: -x[1])[:10]
    report["top_assignees"] = top_assignees
    return report


def _write_pdf_from_text(text: str, out_path: str) -> None:
    """Write a simple PDF containing `text`.

    Tries reportlab, then fpdf, then falls back to creating a blank PDF with the
    JSON/text attached using pypdf (if available).
    """
    # Prefer reportlab
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

    # Try fpdf
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
def generate_tasks_report_pdf(limit: int = 100, out_path: str = "connecteam_tasks_report.pdf"):
    """Generate tasks report and write a PDF to `out_path`. Returns the report dict
    with an added `pdf_path` key on success.
    """
    report = generate_tasks_report(limit=limit)
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
    mcp.run(transport="stdio")
