import json
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise SystemExit("GROQ_API_KEY missing - put it in .env")
client = Groq(api_key=api_key, timeout=20.0, max_retries=2)

STOCK = {"paneer": 2.5, "onion": 12, "tomato": 8}


def get_stock(item):
    if item.lower() == "milk":
        raise ConnectionError("dairy database is not reachable")  # pretend the DB is down
    qty = STOCK.get(item.lower())
    if qty is None:
        return f"{item} is not in the inventory"
    return f"{qty} kg"


TOOLS = {"get_stock": get_stock}


def run_tool(name, arguments):
    if name not in TOOLS:
        return f"ERROR: unknown tool '{name}'. Available tools: {', '.join(TOOLS)}"
    try:
        args = json.loads(arguments)
        return TOOLS[name](**args)
    except json.JSONDecodeError:
        return "ERROR: the arguments were not valid JSON"
    except TypeError as e:
        return f"ERROR: wrong arguments for {name}: {e}"
    except Exception as e:
        return f"ERROR: {name} failed: {e}"


# ---- part 1: test run_tool by hand, no LLM ----
print(run_tool("get_stock", '{"item": "paneer"}'))
print(run_tool("order_onions", '{"kg": 10}'))
print(run_tool("get_stock", '{"item": paneer}'))
print(run_tool("get_stock", '{"dish": "paneer"}'))
print(run_tool("get_stock", '{"item": "milk"}'))
print()

# ---- part 2: the same loop as before, now using run_tool ----
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_stock",
            "description": "Get the current stock of ONE inventory item. Use it when the user asks how much of an item is left.",
            "parameters": {
                "type": "object",
                "properties": {
                    "item": {"type": "string", "description": "inventory item name, e.g. paneer"},
                },
                "required": ["item"],
            },
        },
    }
]


def ask(question):
    messages = [
        {"role": "system", "content": "You are the KitchenOS assistant. Use tools for stock questions. "
                                      "If a tool returns an ERROR, tell the user plainly; never invent a number. "
                                      "Answer in one short line."},
        {"role": "user", "content": question},
    ]
    for step in range(5):
        resp = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=tools,
            reasoning_effort="low",
            max_tokens=400,
        )
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return msg.content

        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [call.model_dump() for call in msg.tool_calls],
        })
        for call in msg.tool_calls:
            result = run_tool(call.function.name, call.function.arguments)
            print(f"   [tool] {call.function.name}({call.function.arguments}) -> {result}")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    return "Sorry, I could not finish that."


for question in ["How much paneer do we have?", "How much milk is left?"]:
    print("Q:", question)
    print("A:", ask(question))
    print()