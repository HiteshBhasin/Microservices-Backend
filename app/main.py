import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Load environment from .env early so route modules see DOORLOOP_API_KEY, etc.
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # dotenv is optional; if not installed, require env vars to be exported externally
    pass

from contextlib import asynccontextmanager
from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from fastapi.middleware.cors import CORSMiddleware
from routes.connecteam import router as connecteam_router
from routes.doorloop import router as doorloop_router
import os
import logging

# Ensure the repository root is on sys.path so imports like `from routes...`
# work when running this module directly (python app/main.py).

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    logging.getLogger().setLevel(logging.INFO)
    missing = []
    # Use ROOT path since MCP server scripts are in project root, not app directory
    for path in ("mcp_server/connectteam_mcp_server.py", "mcp_server/doorloop_mcp_server.py"):
        full_path = ROOT / path
        if not full_path.exists():
            missing.append(str(full_path))
    if missing:
        logging.warning("Missing MCP server scripts: %s", missing)
    else:
        logging.info("All MCP server scripts present.")
    
    yield  # This is where the application runs
    
    # Shutdown code (optional)
    # Add any cleanup code here if needed
    logging.info("Shutting down...")

app = FastAPI(
    title="Microservices Backend API", 
    version="0.1.0",
    lifespan=lifespan  # Add lifespan here
)

# The rest of your code remains the same...
# Rate limiter (slowapi)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
try:
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
except Exception:
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
app.include_router(connecteam_router, prefix="/api/connecteam", tags=["connecteam"])
app.include_router(doorloop_router, prefix="/api/doorloop", tags=["doorloop"])

@app.get("/", tags=["meta"])
async def root():
    return {"ok": True, "service": "Microservices Backend", "version": app.version}

if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
    except Exception as exc:
        logging.error("Failed to start uvicorn: %s", exc)