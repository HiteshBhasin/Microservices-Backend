import sys
from pathlib import Path

# Ensure the repository root is on sys.path so imports like `from routes...`
# work when running this module directly (python app/main.py).
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
	sys.path.insert(0, str(ROOT))

from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from fastapi.middleware.cors import CORSMiddleware
from routes.connecteam import router as connectam_router
from routes.doorloop import router as doorloop_router
import os
import logging


app = FastAPI(title="Microservices Backend API", version="0.1.0")

# Rate limiter (slowapi)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
try:
	# slowapi exposes a Starlette-compatible handler; mypy/pyright sometimes
	# complain about the handler signature. Ignore the static type check here.
	app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
except Exception:
	# If adding the handler fails for any runtime reason, continue without it.
	logging.info("Could not register rate limit exception handler; continuing without it.")

# CORS - development defaults, tighten in production
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


# Mount routers
app.include_router(connectam_router, prefix="/api/connecteam", tags=["connecteam"])
app.include_router(doorloop_router, prefix="/api/doorloop", tags=["doorloop"])


@app.get("/", tags=["meta"])
async def root():
	return {"ok": True, "service": "Microservices Backend", "version": app.version}


@app.on_event("startup")
async def startup_checks():
	"""Run lightweight startup checks (file presence, basic env hints)."""
	logging.getLogger().setLevel(logging.INFO)
	missing = []
	for path in ("mcp_server/connectteam_mcp_server.py", "mcp_server/doorloop_mcp_server.py"):
		if not os.path.exists(path):
			missing.append(path)
	if missing:
		logging.warning("Missing MCP server scripts: %s", missing)
	else:
		logging.info("All MCP server scripts present.")


if __name__ == "__main__":
	# Allow running this module directly for local development.
	try:
		import uvicorn

		uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
	except Exception as exc:  # pragma: no cover - runtime helper
		logging.error("Failed to start uvicorn: %s", exc)

