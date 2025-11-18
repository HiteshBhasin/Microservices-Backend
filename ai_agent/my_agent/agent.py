from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import Getools
sys.path.append(str(Path(__file__).parent.parent))
from Getools import get_tools

CONNECTTEAM_PATH = "mcp_server/connectteam_mcp_server.py"
DOORLOOP_PATH = "mcp_server/doorloop_mcp_server.py"
# Use absolute path to MCP server from workspace root

def fetch_tools(path:str):
    tools = get_tools(path)
    fetched_tools = asyncio.run(tools.get_tools())
    returned_tools=[tools for tools in fetched_tools]
    return returned_tools
    

connecttools = fetch_tools(CONNECTTEAM_PATH)
root_agent = Agent(
    model='gemini-2.5-flash',
    name='Dashboard_Agent',
    description="""
    A specialized assistant for managing Connecteam tasks 
    (CRUD operations) and retrieving active user/tenant data via the Connecteam API.
    """
    ,
    instruction="""
    You are an expert AI assistant for the Connecteam server. Use your specialized tools to manage tasks (list, get, create, update, delete) 
    and fetch tenant/user information. For task management, prefer using the task-specific tools like `list_tasks` or `get_task`. 
    Always remember that the `list_tasks` function requires a `taskboard_id`, which can be found using `list_taskboards`. When creating or updating a task, the `payload` 
    parameter must be a dictionary representing the required task JSON body. Before attempting task operations, try to use `list_taskboards` to discover valid board IDs
    """
    ,
    tools=[connecttools]
)
    