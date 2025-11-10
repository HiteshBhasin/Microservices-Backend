from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio

SERVER_COMMAND = ["python", "connectteam_mcp", "stdio"]
async def get_tools():
    SERVER_START = StdioServerParameters(command=SERVER_COMMAND[0], args=SERVER_COMMAND[1:], env=None)
    async with stdio_client(SERVER_START) as (read, write):
        async with ClientSession(read,write) as server:
            await server.initialize()
            
            tools_list_result = await server.list_tools()
            tools_list = tools_list_result.tools