import sys
from pathlib import Path

PARENT_ROUTE = Path("mcp_server\\doorloop_mcp_server.py").resolve().parent.parent
sys.path.append(str(PARENT_ROUTE))
print(PARENT_ROUTE)
