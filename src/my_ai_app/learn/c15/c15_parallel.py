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
SALES_TODAY = {"paneer tikka": 14, "dal makhani": 9, "veg biryani": 21}


def get_stock(item):
    qty = STOCK.get(item.lower())
    if qty is None:
        return f"{item} is not in the inventory"
    return f"{qty} kg"


def get_sales(dish):
    plates = SALES_TODAY.get(dish.lower())
    if plates is None:
        return f"no sales recorded today for {dish}"
    return f"{plates} plates sold today"


TOOLS = {"get_stock": get_stock, "get_sales": get_sales}

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
    },
    {
        "type": "function",
        "function": {
            "name": "get_sales",
            "description": "Get how many plates of ONE dish were sold today. Use it for questions about today's sales of a dish.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dish": {"type": "string", "description": "dish name, e.g. paneer tikka"},
                },
                "required": ["dish"],
            },
        },
    },
]


def ask(question):
    messages = [
        {"role": "system", "content": "You are the KitchenOS assistant. Use tools for stock and sales questions. Answer in one short line."},
        {"role": "user", "content": question},
    ]
    for step in range(5): #ask the model again if it doesn't answer the question in one go(tool calls upto 5 times)
        resp = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=messages,
            tools=tools,
            parallel_tool_calls=True,
            max_tokens=400,
        )
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return msg.content
        print(f"   round {step + 1}: {len(msg.tool_calls)} tool call(s) requested")
        messages.append({    #storing the LLM response and any tool calls it made
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [call.model_dump() for call in msg.tool_calls],
        })
        #RUN the Tools..
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)
            result = TOOLS[call.function.name](**args)
            print(f"   [tool] {call.function.name}({args}) -> {result}")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result}) # Recording the answer from the tool in the conversation history
    return "Sorry, I could not finish that."


for question in [
    "How much paneer, onion and tomato do we have?",
    "How many paneer tikka did we sell today, and how much paneer is left?",
]:
    print("Q:", question)
    print("A:", ask(question))
    print()