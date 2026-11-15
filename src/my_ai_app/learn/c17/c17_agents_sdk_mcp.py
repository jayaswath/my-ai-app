import asyncio
import os
import sys
from pathlib import Path

from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
from agents.mcp import MCPServerStdio
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise SystemExit("GROQ_API_KEY is missing - check .env")

set_tracing_disabled(True)                    # tracing would try to upload to OpenAI - we don't use OpenAI

# ---------- the model: Groq, through the SDK's Chat Completions adapter ----------
groq = AsyncOpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
model = OpenAIChatCompletionsModel(model="openai/gpt-oss-120b", openai_client=groq)

SERVER_FILE = Path(__file__).parent / "c17_kitchen_server.py"


async def main():
    async with MCPServerStdio(                                     # start the server: command + args again
        name="kitchen",
        params={"command": sys.executable, "args": [str(SERVER_FILE)]},
        client_session_timeout_seconds=30,                         # give the server time to start on Windows
    ) as kitchen:
        agent = Agent(
            name="Kitchen assistant",
            instructions="Use the tools for every number. Never invent a number. Reply in 3 short lines.",
            model=model,
            mcp_servers=[kitchen],                                 # the agent gets ALL the server's tools
        )
        result = await Runner.run(
            agent,
            "Compare sales on 2026-10-23 and 2026-10-16, and check the stock of the main "
            "ingredient of the dish that dropped most.",
        )

        for item in result.new_items:                              # show what happened, step by step
            if item.type == "tool_call_item":
                print(f"[agent] asks {item.raw_item.name}({item.raw_item.arguments})")
            elif item.type == "tool_call_output_item":
                text = item.output["text"] if isinstance(item.output, dict) else item.output
                print(f"[tool]  -> {text}")
        print("\nDIGEST:\n" + result.final_output)


asyncio.run(main())