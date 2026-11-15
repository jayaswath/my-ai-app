import json
import os
import sqlite3
import time
from pathlib import Path

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
MAX_COST_RS = 0.50           # rupees for the whole run

# ---------- cost (ch.13) ----------
PRICE_IN = 12.67             # Rs per 1M input tokens  (Groq pricing page, 19 Oct 2026)
PRICE_OUT = 50.70            # Rs per 1M output tokens (the thinking is billed here too)


def cost_rs(tokens_in, tokens_out):
    return tokens_in / 1_000_000 * PRICE_IN + tokens_out / 1_000_000 * PRICE_OUT


DB_DOWN = False              # test switch: True = the sales database "fails"
DB_PATH = Path("data") / "agent_runs.db"     # the register from item 5 - drafts go here too

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


# ---------- NEW: an ACTION tool - it only DRAFTS, it never orders ----------
def draft_purchase_order(item, kg, outlet="demo"):
    if not 0 < kg <= 50:
        return f"ERROR: kg must be more than 0 and at most 50, got {kg}"
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS pending_actions (
                            id     INTEGER PRIMARY KEY AUTOINCREMENT,
                            outlet TEXT,
                            item   TEXT,
                            kg     REAL,
                            status TEXT)""")
        cur = conn.execute(
            "INSERT INTO pending_actions (outlet, item, kg, status) VALUES (?, ?, ?, 'pending')",
            (outlet, item.lower(), kg))
    return f"DRAFTED order #{cur.lastrowid}: {kg} kg {item}. NOT placed - waiting for the owner's approval."


TOOLS = {"get_sales": get_sales, "get_stock": get_stock, "draft_purchase_order": draft_purchase_order}


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
    {"type": "function", "function": {
        "name": "draft_purchase_order",
        "description": "DRAFT a purchase order for ONE ingredient. It is NOT placed: the owner must approve it.",
        "parameters": {"type": "object",
                       "properties": {"item": {"type": "string", "description": "ingredient, e.g. paneer"},
                                      "kg": {"type": "number", "description": "kilograms to order, at most 50"}},
                       "required": ["item", "kg"]}}},
]

# ---------- the goal: what makes it an agent ----------
GOAL = """You are the morning manager of a cloud kitchen. Nobody is chatting with you.
Goal: tell the owner what matters about yesterday.
1. Get yesterday's sales and the sales of the same weekday one week earlier.
2. If a dish dropped a lot, find out why with the tools (e.g. check the stock of its main ingredient).
3. Your final reply is ONLY the digest: at most 3 short lines, no headings, no markdown.
Use only numbers that came from the tools.
4. If a tool returns an ERROR you cannot fix, stop and say plainly what you could not check. Never invent a number.
5. If earlier digests are given, say whether an earlier warning matters today.
6. If an ingredient has run out, you MUST call draft_purchase_order for it (a sensible amount,
at most 50 kg) BEFORE you write the digest. Only say an order was drafted if the tool replied "DRAFTED".
You can NOT place orders yourself; the owner approves them."""


def run_agent(today, memory="", goal=GOAL, facts=""):
    trigger = f"Today is {today}. Run the morning check."
    if facts:                                                                     # numbers computed by code
        trigger += f"\n\nFacts computed by code (correct - do not re-check them):\n{facts}"
    if memory:                                                                   # long-term memory, if any
        trigger += f"\n\nYour digests from earlier days:\n{memory}"
    messages = [
        {"role": "system", "content": goal},
        {"role": "user", "content": trigger},                                       # the trigger
    ]
    start = time.perf_counter()                          # stopwatch starts
    errors_in_a_row = 0
    seen_calls = set()                                   # every (tool, arguments) already run
    spent_rs = 0.0                                       # the meter starts at zero

    for step in range(1, MAX_STEPS + 1):
        if time.perf_counter() - start > TIME_LIMIT_S:   # STOP 1: out of time
            return f"STOPPED: time limit of {TIME_LIMIT_S}s reached before step {step}"

        resp = client.chat.completions.create(
            model=MODEL, messages=messages, tools=tools,
            reasoning_effort="low", max_tokens=800,
        )
        msg = resp.choices[0].message
        spent_rs += cost_rs(resp.usage.prompt_tokens, resp.usage.completion_tokens)
        print(f"[step {step}] COST  {resp.usage.prompt_tokens} in + {resp.usage.completion_tokens} out"
              f" -> Rs {spent_rs:.4f} so far")

        think = getattr(msg, "reasoning", None)          # gpt-oss shows its thinking here
        if think:
            print(f"[step {step}] THINK {think[:120]}...")

        if not msg.tool_calls:                           # DONE: no more tools wanted -> goal reached
            return msg.content

        if spent_rs > MAX_COST_RS:                       # STOP 4: over budget
            return f"STOPPED: cost ceiling of Rs {MAX_COST_RS} crossed (spent Rs {spent_rs:.4f})"

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


if __name__ == "__main__":
    digest = run_agent("Saturday 2026-10-24")
    print("\nDIGEST:\n" + digest)