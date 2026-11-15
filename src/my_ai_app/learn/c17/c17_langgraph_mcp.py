import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise SystemExit("GROQ_API_KEY is missing - check .env")

# ---------- the model: Groq through LangChain's OpenAI connector (ch.15) ----------
llm = ChatOpenAI(
    model="openai/gpt-oss-120b",
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key,
    reasoning_effort="low",
)

# ---------- which MCP servers to use: the same command + args as before ----------
SERVER_FILE = Path(__file__).parent / "c17_kitchen_server.py"
mcp_client = MultiServerMCPClient({
    "kitchen": {"command": sys.executable, "args": [str(SERVER_FILE)], "transport": "stdio"},
})


async def main():
    tools = await mcp_client.get_tools()             # connect, tools/list, turn each into a LangChain tool
    print("tools from the server:", [tool.name for tool in tools])

    agent = create_agent(                            # a LangGraph graph: agent <-> tools (ch.15 / ch.16 item 14)
        model=llm,
        tools=tools,
        system_prompt="You are a kitchen assistant. Use the tools for every number. Never invent a number.",
    )

    result = await agent.ainvoke(
        {"messages": [{"role": "user",
                       "content": "Compare sales on 2026-10-23 and 2026-10-16, and check the stock "
                                  "of the main ingredient of the dish that dropped most. Reply in 3 lines."}]}
    )

    for message in result["messages"]:               # show what happened, step by step
        if getattr(message, "tool_calls", None):
            for call in message.tool_calls:
                print(f"[agent] asks {call['name']}({call['args']})")
        elif message.type == "tool":
            print(f"[tool]  {message.name} -> {message.text}")
    print("\nDIGEST:\n" + result["messages"][-1].text)


asyncio.run(main())