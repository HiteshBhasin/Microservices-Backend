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
      

        # Import reportlab lazily so missing optional deps don't break module import.
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Preformatted
        from reportlab.lib.units import inch

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

