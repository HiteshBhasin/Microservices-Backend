import pytest
from fastapi.testclient import TestClient

from app.main import app
from services.connecteam_service import ConnecteamClient


def test_get_tasks(monkeypatch):
    async def fake_list_tasks(self, limit=10, offset=0, status="active"):
        return {"result": [{"id": "task_1", "title": "Task 1"}]}

    monkeypatch.setattr(ConnecteamClient, "list_tasks", fake_list_tasks)

    client = TestClient(app)
    r = client.get("/api/connecteam/tasks")

    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list) or (isinstance(data, dict) and "result" in data)


def test_tasks_report_pdf(monkeypatch, tmp_path):
    sample_pdf = tmp_path / "sample_connecteam.pdf"
    sample_pdf.write_bytes(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

    async def fake_generate_pdf(self, limit=100):
        return {"pdf_path": str(sample_pdf)}

    monkeypatch.setattr(ConnecteamClient, "generate_tasks_report_pdf", fake_generate_pdf)

    client = TestClient(app)
    r = client.get("/api/connecteam/tasks/report/pdf")

    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
