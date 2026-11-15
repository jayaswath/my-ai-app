import asyncio

from c17_kitchen_server import mcp            # import the server object - don't start it


async def main():
    tools = await mcp.list_tools()             # what tools/list would send
    for tool in tools:
        print(f"TOOL: {tool.name}")
        print(f"  description: {tool.description}")
        print(f"  inputSchema: {tool.inputSchema}")

    content, structured = await mcp.call_tool("get_stock", {"item": "paneer"})   # what tools/call would run
    print("\nCALL get_stock(paneer) ->", content[0].text)

    # ---------- NEW: resources ----------
    for resource in await mcp.list_resources():          # what resources/list would send
        print(f"\nRESOURCE: {resource.uri}  ({resource.description})")
    menu = await mcp.read_resource("kitchen://menu")      # what resources/read would return
    print(menu[0].content)

    # ---------- NEW: prompts ----------
    for prompt in await mcp.list_prompts():               # what prompts/list would send
        print(f"\nPROMPT: {prompt.name}  arguments: {[a.name for a in prompt.arguments]}")
    filled = await mcp.get_prompt("daily_digest", {"day": "2026-10-23"})   # what prompts/get returns
    print(filled.messages[0].content.text)


asyncio.run(main())