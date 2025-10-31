import asyncio
import os
import pytest
from fastapi.testclient import TestClient

from app.main import app
from services.doorloop_services import DoorloopClient


def test_get_tenants(monkeypatch):
    async def fake_retrieve_tenants(self):
        return {"result": [{"id": "tenant_1", "name": "T1"}]}

    monkeypatch.setattr(DoorloopClient, "retrieve_tenants", fake_retrieve_tenants)

    client = TestClient(app)
    r = client.get("/api/doorloop/tenants")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list) or (isinstance(data, dict) and "result" in data)


def test_properties_report_pdf(monkeypatch, tmp_path):
    sample_pdf = tmp_path / "sample.pdf"
    # minimal pdf header so FileResponse can open it
    sample_pdf.write_bytes(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

    async def fake_generate_pdf(self, out_path: str = "out.pdf"):
        return {"pdf_path": str(sample_pdf)}

    monkeypatch.setattr(DoorloopClient, "generate_properties_report_pdf", fake_generate_pdf)

    client = TestClient(app)
    r = client.get("/api/doorloop/properties/report/pdf")

    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
