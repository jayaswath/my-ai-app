import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

SERVER_URL = "http://127.0.0.1:8001/mcp"     # a URL instead of command + args


async def main():
    async with streamablehttp_client(SERVER_URL) as (read, write, _):    # connect over HTTP
        async with ClientSession(read, write) as session:                # the SAME session as item 8
            await session.initialize()
            print("connected to", SERVER_URL, "\n")

            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"TOOL: {tool.name} - {tool.description}")

            result = await session.call_tool("get_stock", {"item": "paneer"})
            print("\nget_stock(paneer) ->", result.content[0].text)


asyncio.run(main())