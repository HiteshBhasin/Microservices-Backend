
from google.adk.agents.llm_agent import Agent
import logging
import asyncio
import sys
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.genai import types
from pathlib import Path


# Use helper get_tools.to_mcp_toolset() to obtain a configured McpToolset

# Add parent directory to path to import Getools
sys.path.append(str(Path(__file__).parent.parent))

from Getools import get_tools

# Use absolute paths to MCP servers from workspace root
workspace_root = Path(__file__).parent.parent.parent
CONNECTTEAM_PATH = str(workspace_root / "mcp_server" / "connectteam_mcp_server.py")
DOORLOOP_PATH = str(workspace_root / "mcp_server" / "doorloop_mcp_server.py")

# Create an McpToolset using the compatibility helper in Getools.py.
# This returns a configured McpToolset that will start the MCP server
# when the ADK runtime requests tools.
connect_tool_factory = get_tools(CONNECTTEAM_PATH)
connect_mcp_toolset = connect_tool_factory.to_mcp_toolset()
doorloop_tool_factory = get_tools(DOORLOOP_PATH)
doorloop_mcp_toolset = doorloop_tool_factory.to_mcp_toolset()


tools = [connect_mcp_toolset,doorloop_mcp_toolset]



#-----------------------------------------Connecteam-mcp-tools-------------------------------------------------------
try:
    memory = InMemorySessionService()
    APP_NAME = "NestHost_Connecteam"
    SESSION_ID = "session_001_connecteam"
    USER_ID = "user_1_connect"
    
    session =  memory.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID
)
    connecteam_agent = Agent(
        model=LiteLlm(model = 'gemini-2.5-flash'),
        name='Dashboard_connectean_Agent',
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
        """,
        tools=[tools[0]]
    )
except:
    logging.exception("an error occur")

# Export root_agent for adk CLI
# connecteam_root_agent = connecteam_agent
# runner = Runner(
#     agent=connecteam_root_agent,
#     app_name=APP_NAME,
#     session_service=memory
# )

# ------------------------------------------------DoorLoop-MCP-TOOL--------------------------------------------

try:
    memory = InMemorySessionService()
    APP_NAME = "NestHost_Doorloop"
    SESSION_ID = "session_001_doorloop"
    USER_ID = "user_1_doorploop"

    session = memory.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID
    )

    doorloop_agent = Agent(
        model=LiteLlm(model = 'gemini-2.5-flash'),
        name='Dashboard_doorloop_Agent',
        description="""
        A specialized assistant for managing Doorloop tasks
        (CRUD operations) and retrieving active user/tenant data via the Connecteam API.
        """,
        instruction="""
        You are an expert AI assistant for the Doorloop server. Use your specialized tools to manage tasks (list, get, create, update, delete)
        and fetch tenant/user information. For task management, prefer using the task-specific tools like `list_tasks` or `get_task`.
        Always remember that the `list_tasks` function requires a `taskboard_id`, which can be found using `list_taskboards`. When creating or updating a task, the `payload`
        parameter must be a dictionary representing the required task JSON body. Before attempting task operations, try to use `list_taskboards` to discover valid board IDs
        """ ,
        tools=[tools[1]]
 )

except:
    logging.exception("an error occur")

# Export root_agent for adk CLI
# doorloo_root_agent = doorloop_agent
# runner = Runner(
#     agent=doorloo_root_agent,
#     app_name=APP_NAME,
#     session_service=memory
# )

 

#-----------------------------------------------------------Super-Agent---------------------------------------------------------

try:
    memory = InMemorySessionService()
    APP_NAME = "NestHost_Super"
    SESSION_ID = "session_001_superAgent"
    USER_ID = "user_1_superAgent"

    session = memory.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID
    )

    super_agent = Agent(
        model=LiteLlm(model = 'gemini-2.5-flash'),
        name='Dashboard_Super_Agent',
        description="""
        A specialized assistant for managing Doorloop tasks
        (CRUD operations) and retrieving active user/tenant data via the Connecteam API.
        """
        ,
        instruction="""
        You are an expert AI assistant for the Doorloop server. Use your specialized tools to manage tasks (list, get, create, update, delete)
        and fetch tenant/user information. For task management, prefer using the task-specific tools like `list_tasks` or `get_task`.
        Always remember that the `list_tasks` function requires a `taskboard_id`, which can be found using `list_taskboards`. When creating or updating a task, the `payload`
        parameter must be a dictionary representing the required task JSON body. Before attempting task operations, try to use `list_taskboards` to discover valid board IDs
        """ ,
        sub_agents=[doorloop_agent, connecteam_agent]
    )
except:
    logging.exception("an error occur")

# Export root_agent for adk CLI
super_root_agent = super_agent
runner = Runner(
    agent=super_root_agent,
    app_name=APP_NAME,
    session_service=memory
)

# No auto-fetching or assignment of raw tools at import time. The
# McpToolset provided to the agent will be used by the ADK runtime to
# obtain tools when needed.
# async def main():
#     events = runner.run(
#         user_id=USER_ID,
#         session_id=SESSION_ID,
#         new_message=types.Content(parts=[types.Part(text="Hello, I need help with Connecteam tasks.")])
#     )
#     async for event in events:
#         print(event)
# asyncio.run(main())