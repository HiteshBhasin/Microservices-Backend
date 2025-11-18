from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client



class get_tools:
    def __init__(self, file_path:str):
        self.file_path = file_path
        
    async def get_tools(self):
        SERVER_COMMAND = ["python", self.file_path, "stdio"]
        SERVER_START = StdioServerParameters(command=SERVER_COMMAND[0], args=SERVER_COMMAND[1:], env=None)
        async with stdio_client(SERVER_START) as (read, write):
            async with ClientSession(read,write) as server:
                await server.initialize()   
                tools_list_result = await server.list_tools()
                tools_list = tools_list_result.tools
                return tools_list
            
            
            
# file_path = "mcp_server/connectteam_mcp_server.py"
# tools = get_tools(file_path=file_path)
# for i in asyncio.run(tools.get_tools()):
#     print(i.name)