import json
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise SystemExit("GROQ_API_KEY missing - put it in .env")
client = Groq(api_key=api_key, timeout=20.0, max_retries=2)

# a fake inventory (in KitchenOS this would be a database query)
STOCK = {"paneer": 2.5, "onion": 12, "tomato": 8}


def get_stock(item):
    qty = STOCK.get(item.lower())
    if qty is None:
        return f"{item} is not in the inventory"
    return f"{qty} kg"


TOOLS = {"get_stock": get_stock}

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
        {"role": "system", "content": "You are the KitchenOS assistant. Use tools for stock questions. Answer in one short line."},
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
            args = json.loads(call.function.arguments)
            result = TOOLS[call.function.name](**args)
            print(f"   [tool] {call.function.name}({args}) -> {result}")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    return "Sorry, I could not finish that."


for question in ["How much paneer do we have left?", "Do we have any saffron?", "Hi!"]:
    print("Q:", question)
    print("A:", ask(question))
    print()