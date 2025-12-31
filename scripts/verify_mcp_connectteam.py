"""Quick verification script — starts/connects to the Connecteam MCP server
and prints the available tools. Uses the existing ServiceFactory and ConnecteamService
so it will spawn the server as a subprocess (stdio) by default.

Run: python scripts/verify_mcp_connectteam.py
"""
import asyncio
import json
import logging
from services.connecteam_service import ConnecteamService

logging.basicConfig(level=logging.INFO)


async def main():
    server_script = "mcp_server/connectteam_mcp_server.py"
    service = await ConnecteamService(server_script),
    # ServiceFactory returns a wrapper but here we want to start directly
    from services.base_mcp_client import ServiceFactory, ConnecteamService as CS
    svc = await ServiceFactory.get_service(CS, server_script)
    async with svc as s:
        tools = await s.list_tools()
        # tools may be a ListToolsResult or a list; try to print both
        try:
            if hasattr(tools, "tools"):
                out = tools.tools
            else:
                out = tools
        except Exception:
            out = tools

        print(json.dumps([{
            "name": getattr(t, "name", None) or t.get("name") if isinstance(t, dict) else str(t),
            "title": getattr(t, "title", None) or (t.get("title") if isinstance(t, dict) else None),
        } for t in out], indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
