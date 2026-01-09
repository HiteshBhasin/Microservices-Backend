"""
Google Analytics MCP Server
Provides Model Context Protocol interface for Google Analytics data
"""

import json
import sys
import os
from typing import Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

from services.google_analytics import (
    get_active_users,
    get_analytics_by_country,
    get_analytics_by_country_nestHost,
    get_analytics_by_country_firstClass,
    get_total_summary,
    user_engagement_by_month,
    user_by_month,
    user_engagement_by_month_sessions
)

# Initialize MCP server
server = Server("google-analytics-server")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List all available Google Analytics tools."""
    return [
        types.Tool(
            name="get_analytics_summary",
            description="Get overall summary of Google Analytics metrics for the last 60 days including active users, new users, engaged sessions, engagement rate, event count, conversions, and total revenue",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        types.Tool(
            name="get_daily_analytics",
            description="Get daily Google Analytics data for the last 60 days. Returns date-wise breakdown of all key metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Optional limit on number of most recent days to return (1-365)",
                        "minimum": 1,
                        "maximum": 365
                    }
                },
                "required": []
            },
        ),
        types.Tool(
            name="get_analytics_by_country",
            description="Get Google Analytics data grouped by country (top 10 countries by active users)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        types.Tool(
            name="get_analytics_by_country_nest_host",
            description="Get Google Analytics data grouped by country with nest/host information",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        types.Tool(
            name="get_analytics_by_country_first_class",
            description="Get Google Analytics data grouped by country with first-class user metrics",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        types.Tool(
            name="get_monthly_active_users",
            description="Get Monthly Active Users (MAU) data showing year-month and active user counts",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        types.Tool(
            name="get_monthly_engagement",
            description="Get monthly engagement metrics including engaged sessions, engagement rate, and new users",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        types.Tool(
            name="get_monthly_sessions",
            description="Get monthly session engagement data",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution requests."""
    
    try:
        if name == "get_analytics_summary":
            result = get_total_summary()
            if not result:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"error": "No summary data available"})
                )]
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "get_daily_analytics":
            limit = arguments.get("limit") if arguments else None
            data = get_active_users()
            if limit:
                data = data[-limit:]
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "count": len(data),
                    "data": data
                }, indent=2)
            )]
        
        elif name == "get_analytics_by_country":
            data = get_analytics_by_country()
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "count": len(data),
                    "data": data
                }, indent=2)
            )]
        
        elif name == "get_analytics_by_country_nest_host":
            data = get_analytics_by_country_nestHost()
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "count": len(data),
                    "data": data
                }, indent=2)
            )]
        
        elif name == "get_analytics_by_country_first_class":
            data = get_analytics_by_country_firstClass()
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "count": len(data),
                    "data": data
                }, indent=2)
            )]
        
        elif name == "get_monthly_active_users":
            data = user_by_month()
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "count": len(data),
                    "data": data
                }, indent=2)
            )]
        
        elif name == "get_monthly_engagement":
            data = user_engagement_by_month()
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "count": len(data),
                    "data": data
                }, indent=2)
            )]
        
        elif name == "get_monthly_sessions":
            data = user_engagement_by_month_sessions()
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "count": len(data),
                    "data": data
                }, indent=2)
            )]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=json.dumps({"error": str(e)})
        )]


async def main():
    """Run the Google Analytics MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="google-analytics-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
