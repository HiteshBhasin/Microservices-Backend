import os
import json
import requests
from pathlib import Path


def load_dotenv_like(candidate: Path):
    try:
        from dotenv import load_dotenv

        load_dotenv(candidate.as_posix(), override=False)
        return
    except Exception:
        if not candidate.exists():
            return
        with candidate.open("r", encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = val


# load .env from repo root
here = Path(__file__).resolve().parent
repo_root = here.parent
load_dotenv_like(repo_root / ".env")

API_KEY = os.environ.get("DOORLOOP_API_KEY")
if not API_KEY:
    print(json.dumps({"error": "DOORLOOP_API_KEY not found in environment (or .env)"}, indent=2))
    raise SystemExit(1)

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "accept": "application/json",
    "content-type": "application/json",
}

endpoints = [
    "https://api.doorloop.com/tenants",
    "https://api.doorloop.com/v1/tenants",
    "https://app.doorloop.com/api/tenants",
    "https://app.doorloop.com/v1/tenants",
    "https://app.doorloop.com/tenants",
]

methods = ["GET", "POST"]

results = []
for url in endpoints:
    for method in methods:
        try:
            if method == "GET":
                resp = requests.get(url, headers=headers, timeout=10)
            else:
                # try POST with an empty json body
                resp = requests.post(url, headers=headers, json={}, timeout=10)

            ctype = resp.headers.get("Content-Type", "")
            snippet = (resp.text or "")[:1000]
            results.append(
                {
                    "url": url,
                    "method": method,
                    "status": resp.status_code,
                    "ok": resp.ok,
                    "content_type": ctype,
                    "body_snippet": snippet,
                }
            )
        except Exception as e:
            results.append({"url": url, "method": method, "error": str(e)})

print(json.dumps(results, indent=2))
