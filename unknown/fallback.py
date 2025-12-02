from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

connection_params = StdioServerParameters(command="python", args=["mcp_server//doorloop_mcp_server.py", "stdio"])

# Create a session and call a tool properly
async def test_mcp_connection():
	async with stdio_client(connection_params) as (read, write):
		async with ClientSession(read, write) as session:
			# Initialize the session
			await session.initialize()
			
			# List available tools
			tools = await session.list_tools()
			print("Available tools:", tools)
			
			# Call a specific tool (replace 'tool_name' with an actual tool name from the list)
			# result = await session.call_tool(name="tool_name", arguments={})
			# print("Result:", result)
			
	print( tools)

# Run the async function
import asyncio
asyncio.run(test_mcp_connection())