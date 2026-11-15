from c17_kitchen_server import mcp            # the SAME server object: same tools, resource, prompt

mcp.settings.host = "127.0.0.1"               # only this laptop can reach it (no login yet!)
mcp.settings.port = 8001                      # 8000 is taken by Docker on your machine

if __name__ == "__main__":
    print("kitchen MCP server on http://127.0.0.1:8001/mcp  (Ctrl+C to stop)")
    mcp.run(transport="streamable-http")      # HTTP instead of stdio: wait for web requests