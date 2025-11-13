from google.adk.agents.llm_agent import Agent
import asyncio
from google.adk.models.lite_llm import LiteLlm
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters

root_agent = Agent(
    model='gemini-2.5-flash',
    name='Dashboard-Agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)

def get_mcp_sessions():
    