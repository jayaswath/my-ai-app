import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# ---------- how to START the server: the same Python, the server file next to this one ----------
SERVER_FILE = Path(__file__).parent / "c17_kitchen_server.py"
server_params = StdioServerParameters(command=sys.executable, args=[str(SERVER_FILE)])


async def main():
    async with stdio_client(server_params) as (read, write):     # 1. start the server program; get its pipes
        async with ClientSession(read, write) as session:        # 2. a session on top of the pipes
            await session.initialize()                           # 3. the handshake
            print("connected to the kitchen server\n")

            tools = await session.list_tools()                   # 4. tools/list
            for tool in tools.tools:
                print(f"TOOL: {tool.name} - {tool.description}")

            result = await session.call_tool("get_stock", {"item": "paneer"})       # 5. tools/call
            print("\nget_stock(paneer) ->", result.content[0].text)

            result = await session.call_tool("get_sales", {"day": "2026-10-23"})
            print("get_sales(2026-10-23) ->", result.content[0].text)

            result = await session.call_tool("get_price", {"item": "paneer"})       # a tool that doesn't exist
            print("\nget_price(paneer) -> isError:", result.isError, "|", result.content[0].text)


asyncio.run(main())