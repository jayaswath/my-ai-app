import json
import os
import time

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise SystemExit("GROQ_API_KEY is missing - check .env")
client = Groq(api_key=api_key, timeout=20.0, max_retries=2)
MODEL = "openai/gpt-oss-120b"

# ---------- stopping conditions (the agent's limits) ----------
MAX_STEPS = 8                # rounds with the model
MAX_ERRORS_IN_A_ROW = 3      # tool errors one after another
TIME_LIMIT_S = 60            # seconds for the whole run

DB_DOWN = False             # test switch: True = the sales database "fails"

# ---------- fake kitchen data (stands in for KitchenOS tables) ----------
SALES = {
    "2026-10-23": {"Paneer Tikka": 0, "Chicken Biryani": 40, "Veg Biryani": 18},   # yesterday (Friday)
    "2026-10-16": {"Paneer Tikka": 22, "Chicken Biryani": 42, "Veg Biryani": 20},  # last Friday
}
STOCK = {
    "paneer": "paneer: 0 kg - ran out on 2026-10-23 at 2:10 pm",
    "chicken": "chicken: 6 kg",
    "rice": "rice: 18 kg",
}


# ---------- tools: my code runs these ----------
def get_sales(day):
    if DB_DOWN:
        raise ConnectionError("sales database is down")
    dishes = SALES.get(day)
    if dishes is None:
        return f"no sales recorded for {day}"
    lines = ", ".join(f"{dish} {plates}" for dish, plates in dishes.items())
    return f"{day}: {lines} - total {sum(dishes.values())} plates"


def get_stock(item):
    return STOCK.get(item.lower(), f"{item} is not in the inventory")


TOOLS = {"get_sales": get_sales, "get_stock": get_stock}


def run_tool(name, arguments):
    if name not in TOOLS:
        return f"ERROR: unknown tool '{name}'. Available tools: {', '.join(TOOLS)}"
    try:
        return TOOLS[name](**json.loads(arguments))
    except json.JSONDecodeError:
        return "ERROR: the arguments were not valid JSON"
    except TypeError as e:
        return f"ERROR: wrong arguments for {name}: {e}"
    except Exception as e:
        return f"ERROR: {name} failed: {e}"

tools = [
    {"type": "function", "function": {
        "name": "get_sales",
        "description": "Plates sold per dish on ONE day. Use it to see how a day went.",
        "parameters": {"type": "object",
                       "properties": {"day": {"type": "string", "description": "the day to check, as YYYY-MM-DD, e.g. 2026-10-23"}},
                       "required": ["day"]}}},
    {"type": "function", "function": {
        "name": "get_stock",
        "description": "Current stock of ONE ingredient, and when it ran out if it did.",
        "parameters": {"type": "object",
                       "properties": {"item": {"type": "string", "description": "ingredient, e.g. paneer"}},
                       "required": ["item"]}}},
]

# ---------- the goal: what makes it an agent ----------
GOAL = """You are the morning manager of a cloud kitchen. Nobody is chatting with you.
Goal: tell the owner what matters about yesterday.
1. Get yesterday's sales and the sales of the same weekday one week earlier.
2. If a dish dropped a lot, find out why with the tools (e.g. check the stock of its main ingredient).
3. Your final reply is ONLY the digest: at most 3 short lines, no headings, no markdown.
Use only numbers that came from the tools.
4. If a tool returns an ERROR you cannot fix, stop and say plainly what you could not check. Never invent a number."""


def run_agent(today):
    messages = [
        {"role": "system", "content": GOAL},
        {"role": "user", "content": f"Today is {today}. Run the morning check."},   # the trigger
    ]
    start = time.perf_counter()                          # stopwatch starts
    errors_in_a_row = 0
    seen_calls = set()                                   # every (tool, arguments) already run

    for step in range(1, MAX_STEPS + 1):
        if time.perf_counter() - start > TIME_LIMIT_S:   # STOP 1: out of time
            return f"STOPPED: time limit of {TIME_LIMIT_S}s reached before step {step}"

        msg = client.chat.completions.create(
            model=MODEL, messages=messages, tools=tools,
            reasoning_effort="low", max_tokens=800,
        ).choices[0].message

        think = getattr(msg, "reasoning", None)          # gpt-oss shows its thinking here
        if think:
            print(f"[step {step}] THINK {think[:120]}...")

        if not msg.tool_calls:                           # DONE: no more tools wanted -> goal reached
            return msg.content

        messages.append({"role": "assistant", "content": msg.content or "",
                         "tool_calls": [call.model_dump() for call in msg.tool_calls]})
        for call in msg.tool_calls:
            this_call = (call.function.name, call.function.arguments)
            if this_call in seen_calls:                  # no progress: the exact same call again
                result = "ERROR: you already made this exact call. Use its earlier result or do something else."
            else:
                seen_calls.add(this_call)
                result = run_tool(call.function.name, call.function.arguments)
            print(f"[step {step}] ACT   {call.function.name}({call.function.arguments})")
            print(f"[step {step}] CHECK {result}")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

            if result.startswith("ERROR"):
                errors_in_a_row += 1
            else:
                errors_in_a_row = 0                      # one success resets the count

        if errors_in_a_row >= MAX_ERRORS_IN_A_ROW:       # STOP 2: stuck on errors
            return f"STOPPED: {errors_in_a_row} tool errors in a row. Last one: {result}"

    return f"STOPPED: step limit of {MAX_STEPS} reached"   # STOP 3: out of steps


digest = run_agent("Saturday 2026-10-24")
print("\nDIGEST:\n" + digest)