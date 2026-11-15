import json
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise SystemExit("GROQ_API_KEY missing - put it in .env")
client = Groq(api_key=api_key, timeout=20.0, max_retries=2)

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

for question in ["How much paneer do we have left?", "What is paneer made from?"]:
    resp = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": question}],
        tools=tools,
        reasoning_effort="low",
        max_tokens=400,
    )
    choice = resp.choices[0]
    print("Q:", question)
    print("   finish_reason:", choice.finish_reason)
    for call in choice.message.tool_calls or []:
        print("   tool asked for:", call.function.name)
        print("   arguments (text):", call.function.arguments)
        print("   arguments (dict):", json.loads(call.function.arguments))
    print("   text reply:", choice.message.content)
    print()