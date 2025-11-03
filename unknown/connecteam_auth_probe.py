import os
import json
import requests
from pathlib import Path


def load_dotenv_like(path: Path):
    try:
        from dotenv import load_dotenv

        load_dotenv(path.as_posix(), override=False)
        return
    except Exception:
        if not path.exists():
            return
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


# load .env from repo root
load_dotenv_like(Path(__file__).resolve().parent.parent / ".env")

API_KEY = os.environ.get("CONNECTTEAM_API_KEY")
if not API_KEY:
    print(json.dumps({"error": "CONNECTTEAM_API_KEY not set in env/.env"}, indent=2))
    raise SystemExit(1)

url = "https://api.connecteam.com/users/v1/users?limit=10&offset=0&order=asc&userStatus=active"
candidate_headers = [
    {"Authorization": f"Bearer {API_KEY}", "accept": "application/json"},
    {"Authorization": f"ApiKey {API_KEY}", "accept": "application/json"},
    {"Authorization": f"Token {API_KEY}", "accept": "application/json"},
    {"x-api-key": API_KEY, "accept": "application/json"},
    {"X-API-KEY": API_KEY, "accept": "application/json"},
    {"Api-Key": API_KEY, "accept": "application/json"},
    {"api_key": API_KEY, "accept": "application/json"},
]

results = []
for hdrs in candidate_headers:
    try:
        resp = requests.get(url, headers=hdrs, timeout=10, allow_redirects=True)
        results.append({
            "tried_header": hdrs,
            "status": resp.status_code,
            "ok": resp.ok,
            "content_type": resp.headers.get("Content-Type"),
            "body_snippet": (resp.text or "")[:600],
            "redirects": [r.status_code for r in resp.history] if resp.history else [],
        })
        # stop early on a good JSON response
        if resp.ok and resp.headers.get("Content-Type", "").startswith("application/json"):
            break
    except Exception as e:
        results.append({"tried_header": hdrs, "error": str(e)})

# Also try query param (only if header attempts fail)
if not any(r.get("ok") and r.get("content_type", "").startswith("application/json") for r in results):
    try:
        resp = requests.get(url + f"&api_key={API_KEY}", timeout=10)
        results.append({
            "tried": "query_param ?api_key=",
            "status": resp.status_code,
            "ok": resp.ok,
            "content_type": resp.headers.get("Content-Type"),
            "body_snippet": (resp.text or "")[:600],
            "redirects": [r.status_code for r in resp.history] if resp.history else [],
        })
    except Exception as e:
        results.append({"tried": "query_param", "error": str(e)})

print(json.dumps(results, indent=2))
