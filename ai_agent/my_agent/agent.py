from google.adk.agents.llm_agent import Agent
import logging
import asyncio
import sys
import os
from google.adk.sessions import InMemorySessionService
# from google.adk.models.lite_llm import LiteLlm
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

# Make the LLM model configurable via environment variable so you can
# select a lighter/alternate model when the default is overloaded.
# Example: `ADK_MODEL=gemini-2.1 adk run my_agent`
MODEL_NAME = os.environ.get("ADK_MODEL", "gemini-2.5-flash")


#-----------------------------------------Connecteam-mcp-tools-------------------------------------------------------
try:
    memory = InMemorySessionService()
    APP_NAME = "NestHost_Connecteam"
    SESSION_ID = "session_001_connecteam"
    USER_ID = "user_1_connect"

    # Defer creating sessions to runtime; `create_session` is async and
    # cannot be awaited at import time. The ADK Runner will create or
    # use sessions at runtime via the provided `session_service`.
    connecteam_agent = Agent(
        model= MODEL_NAME,
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
        """
        ,
        tools=[tools[0]]
    )
except:
    logging.exception("an error occur")
    
#Export root_agent for adk CLI
connecteam_root_agent = connecteam_agent
runner = Runner(
    agent=connecteam_root_agent,
    app_name=APP_NAME,
    session_service=memory
)

# ------------------------------------------------DoorLoop-MCP-TOOL--------------------------------------------

try:
    memory = InMemorySessionService()
    APP_NAME = "NestHost_Doorloop"
    SESSION_ID = "session_001_doorloop"
    USER_ID = "user_1_doorploop"

    # Defer creating sessions to runtime; `create_session` is async and
    # cannot be awaited at import time.

    doorloop_agent = Agent(
        model=MODEL_NAME,
        name='Dashboard_doorloop_Agent',
        description="""
        A specialized assistant for managing Doorloop tasks 
        (CRUD operations) and retrieving active user/tenant data via the Doorloop API.
        """
        ,
        instruction="""
        You are an expert AI assistant for the Doorloop server. Use your specialized tools to manage tasks (list, get, create, update, delete) 
        and fetch tenant/user information. For internal management, prefer using the tenant-specific tools like `retrieve_tenants` or `retrieve_leases`. 
        Always remember that the `retrieve_a_tenants` function requires a `tenant_id`, which can be found using `retrieve_tenants`. When retrieving or updating a tenant, lease or properies information, the `payload` 
        parameter must be a dictionary representing the required task JSON body. Before attempting any operations, try to use `retrieve_tenants` for tenants general infomration , 'retrieve_leases' to get lease information ,'retrieve_properties' to get properties.Also to generate pdf report of the balancesheet use 'generate_report' 
        and to discover valid  property ids use 'retrieve_properties_id' and for communication use tool like 'retrieve_doorloop_communication'.
        """
        ,
        tools=[tools[1]]
    )
except:
    logging.exception("an error occur")
    
#Export root_agent for adk CLI
doorloo_root_agent = doorloop_agent
runner = Runner(
    agent=doorloo_root_agent,
    app_name=APP_NAME,
    session_service=memory
)

#-----------------------------------------------------------Super-Agent---------------------------------------------------------
try:
    memory = InMemorySessionService()
    APP_NAME = "NestHost_Super"
    SESSION_ID = "session_001_superAgent"
    USER_ID = "user_1_superAgent"

    # Defer creating sessions to runtime; `create_session` is async and
    # cannot be awaited at import time.

    root_agent = Agent(
        model=MODEL_NAME,
        name='Dashboard_Super_Agent',
        description="""
        he Dashboard Super Agent is a centralized root agent responsible for orchestrating
        Doorloop and Connecteam operations. It can manage tasks (CRUD), retrieve tenant/user
        information, and coordinate with sub-agents for specialized workflows.
        """
        ,
        instruction="""
       You are the Dashboard Super Agent — the root controller agent for both the Doorloop
and Connecteam systems. You have full access to multiple specialized tools and 
sub-agents. Follow these behavioral guidelines:

GENERAL BEHAVIOR
- Always answer with clarity and precision.
- When a user asks a question related to Doorloop or Connecteam, decide if you should
  use your own tools or route the request to a more specialized sub-agent.
- Always list the tools you intend to use with bullet points for readability.

DOORLOOP TASK MANAGEMENT
- Use the Doorloop task tools to list, get, create, update, or delete tasks.
- IMPORTANT: `list_tasks` ALWAYS requires a valid `taskboard_id`.
- To obtain a valid `taskboard_id`, first call the `list_taskboards` tool.
- When creating or updating a task:
  - The `payload` must be a dictionary containing the proper JSON fields.
  - Validate that the required keys are present before attempting the API call.
- If the user request is ambiguous, ask clarifying questions.

CONNECTEAM OPERATIONS
- You can retrieve active tenant data, user information, or other metadata via the
  Connecteam API tools.
- If the request fits a specialized Connecteam sub-agent more appropriately, transfer
  the conversation to that agent.

AGENT ROUTING
- You may delegate tasks to:
  • Dashboard_doorloop_Agent
  • Dashboard_connecteam_Agent
- Transfer only when necessary and beneficial for accurate handling.

ERROR HANDLING
- If a tool call fails due to missing or incorrect parameters, explain the issue and
  guide the user with the correct format.
- Never guess IDs. Always rely on `list_taskboards` or other discovery tools.

OUTPUT STYLE
- Use bullet points whenever listing tools, steps, or results.
- Keep responses concise but helpful. 
        """
        ,
       
        sub_agents=[doorloop_agent, connecteam_agent]
    )
except:
    logging.exception("an error occur")
    
try:
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=memory
    )
except Exception:
    logging.exception("failed to create Runner")

# No auto-fetching or assignment of raw tools at import time. The``
# McpToolset provided to the agent will be used by the ADK runtime to
# obtain tools when needed.
async def main():
    events = runner.run(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=types.Content(parts=[types.Part(text="Hello, I need help with Connecteam tasks.")])
    )
    async for event in events:
        print(event)

asyncio.run(main())
