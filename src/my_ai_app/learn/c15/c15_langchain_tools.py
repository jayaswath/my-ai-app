import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain_openai import ChatOpenAI

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise SystemExit("GROQ_API_KEY missing - put it in .env")

STOCK = {"paneer": 2.5, "onion": 12, "tomato": 8}
SALES_TODAY = {"paneer tikka": 14, "dal makhani": 9, "veg biryani": 21}


@tool(parse_docstring=True)
def get_stock(item: str) -> str:
    """Get the current stock of ONE inventory item. Use it when the user asks how much of an item is left.

    Args:
        item: inventory item name, e.g. paneer
    """
    qty = STOCK.get(item.lower())
    if qty is None:
        return f"{item} is not in the inventory"
    return f"{qty} kg"


@tool(parse_docstring=True)
def get_sales(dish: str) -> str:
    """Get how many plates of ONE dish were sold today.

    Args:
        dish: dish name, e.g. paneer tikka
    """
    plates = SALES_TODAY.get(dish.lower())
    if plates is None:
        return f"no sales recorded today for {dish}"
    return f"{plates} plates sold today"


# the schema LangChain built from the function (compare with your hand-written one)
print(convert_to_openai_tool(get_stock))
print()

llm = ChatOpenAI(
    model="openai/gpt-oss-120b",
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1",
    temperature=0.2,
    reasoning_effort="low",
    max_tokens=400,
)

agent = create_agent(
    model=llm,
    tools=[get_stock, get_sales],
    system_prompt="You are the KitchenOS assistant. Use tools for stock and sales questions. Answer in one short line.",
)

for question in ["How much paneer do we have?", "How many paneer tikka did we sell today, and how much paneer is left?"]:
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    print("Q:", question)
    for m in result["messages"]:
        for call in getattr(m, "tool_calls", None) or []:
            print(f"   [tool] {call['name']}({call['args']})")
    print("A:", result["messages"][-1].content)
    print()