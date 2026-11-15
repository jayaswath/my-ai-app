import asyncio
import os

from agent_framework import Agent, tool
from agent_framework.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise SystemExit("GROQ_API_KEY is missing - check .env")

# ---------- the model: Groq through the OpenAI-style client ----------
client = OpenAIChatCompletionClient(
    model="openai/gpt-oss-120b",
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key,
)

FACTS = """2026-10-23 vs 2026-10-16: total 58 vs 84 plates (-26)
Paneer Tikka: 0 vs 22 (-22)
Chicken Biryani: 40 vs 42 (-2)
Veg Biryani: 18 vs 20 (-2)"""

STOCK = {"paneer": "paneer: 0 kg - ran out on 2026-10-23 at 2:10 pm", "chicken": "chicken: 6 kg"}


# ---------- a TOOL: a plain function + @tool (like LangChain's @tool, ch.15) ----------
@tool
def get_stock(item: str) -> str:
    """Current stock of ONE ingredient, e.g. paneer."""
    print(f"   [get_stock] {item}")
    return STOCK.get(item.lower(), f"{item} is not in the inventory")


# ---------- WORKER agent: owns the stock tool ----------
stock_checker = Agent(
    client,
    instructions="You check ingredient stock with get_stock. Reply with the stock line only.",
    name="stock_checker",
    tools=[get_stock],
)

# ---------- SUPERVISOR agent: its only tool is the worker agent ----------
manager = Agent(
    client,
    instructions=(
        "You are the morning manager of a cloud kitchen. The sales facts are correct.\n"
        "For the dish with the biggest drop, ask stock_checker about its main ingredient.\n"
        "Then reply with EXACTLY 3 plain lines: totals, the biggest drop and its cause, one action.\n"
        "Use only numbers from the facts and from stock_checker."
    ),
    name="manager",
    tools=[stock_checker.as_tool(name="stock_checker",
                                 description="Ask the stock checker about one ingredient")],
)


async def main():
    result = await manager.run(f"Facts:\n{FACTS}")
    print("\nDIGEST:\n" + result.text)


asyncio.run(main())