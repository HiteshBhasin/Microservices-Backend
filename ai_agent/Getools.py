from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset

class get_tools:

    """Compatibility helper for MCP tool discovery.
     `get_tools(file_path).get_tools()` remains available (async) and
      returns a raw list of MCP tool descriptors (backwards compatible).
     `get_tools(file_path).to_mcp_toolset()` returns an ADK
      `McpToolset` configured to run the MCP server using the given file
      path. This is useful to pass directly into an `Agent(..., tools=[...])`.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        
    async def get_tools(self):
        SERVER_COMMAND = ["python", self.file_path, "stdio"]
        SERVER_START = StdioServerParameters(command=SERVER_COMMAND[0], args=SERVER_COMMAND[1:], env=None)
        async with stdio_client(SERVER_START) as (read, write):
            async with ClientSession(read, write) as server:
                await server.initialize()
                tools_list_result = await server.list_tools()
                tools_list = tools_list_result.tools
                return tools_list
    
    def to_mcp_toolset(self):

        """Return an ADK McpToolset configured to run the MCP server
        for the provided file path. The returned McpToolset will lazily
        create MCP sessions when its `get_tools` is called by the ADK
        runtime.
        """
        # Use StdioServerParameters so McpToolset will spawn the server
        # using the local python executable.
        connection_params = StdioServerParameters(command="python", args=[self.file_path, "stdio"])
        return McpToolset(connection_params=connection_params)

 