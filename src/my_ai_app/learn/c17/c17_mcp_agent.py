import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from groq import AsyncGroq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise SystemExit("GROQ_API_KEY is missing - check .env")
client = AsyncGroq(api_key=api_key, timeout=20.0, max_retries=2)
MODEL = "openai/gpt-oss-120b"

SERVER_FILE = Path(__file__).parent / "c17_kitchen_server.py"
server_params = StdioServerParameters(command=sys.executable, args=[str(SERVER_FILE)])

SYSTEM = "You are a kitchen assistant. Use the tools for every number. Never invent a number."


# ---------- the GLUE: MCP tool → Groq tool schema ----------
def to_groq_tool(tool):
    return {"type": "function", "function": {
        "name": tool.name,
        "description": tool.description,
        "parameters": tool.inputSchema,           # MCP calls it inputSchema; Groq calls it parameters
    }}


# ---------- run_tool, MCP version: the SERVER runs the tool ----------
async def run_mcp_tool(session, name, arguments):
    try:
        result = await session.call_tool(name, json.loads(arguments))
    except json.JSONDecodeError:
        return "ERROR: the arguments were not valid JSON"
    except Exception as e:
        return f"ERROR: {name} failed: {e}"
    text = result.content[0].text if result.content else ""
    return f"ERROR: {text}" if result.isError else text


async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            mcp_tools = (await session.list_tools()).tools                 # tools come FROM THE SERVER
            tools = [to_groq_tool(tool) for tool in mcp_tools]
            print("tools from the server:", [tool.name for tool in mcp_tools])

            prompt = await session.get_prompt("daily_digest", {"day": "2026-10-23"})   # the server's prompt
            question = prompt.messages[0].content.text

            messages = [{"role": "system", "content": SYSTEM},
                        {"role": "user", "content": question}]

            for step in range(1, 9):                                         # your ch.16 loop
                resp = await client.chat.completions.create(
                    model=MODEL, messages=messages, tools=tools,
                    reasoning_effort="low", max_tokens=800,
                )
                msg = resp.choices[0].message
                if not msg.tool_calls:
                    print("\nDIGEST:\n" + (msg.content or ""))
                    return

                messages.append({"role": "assistant", "content": msg.content or "",
                                 "tool_calls": [call.model_dump() for call in msg.tool_calls]})
                for call in msg.tool_calls:
                    result = await run_mcp_tool(session, call.function.name, call.function.arguments)
                    print(f"[step {step}] ACT   {call.function.name}({call.function.arguments})")
                    print(f"[step {step}] CHECK {result}")
                    messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

            print("STOPPED: step limit reached")


asyncio.run(main())