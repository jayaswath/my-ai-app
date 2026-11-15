import sqlite3
from datetime import date, timedelta
from pathlib import Path

from c16_cost import MODEL, SALES, client, run_agent

DB_PATH = Path("data") / "agent_runs.db"
RUN_DAY = date(2026, 10, 24)          # demo: the morning we pretend it is

DIGEST_GOAL = """You are the morning manager of a cloud kitchen. Nobody is chatting with you.
The sales facts in the message were computed by code and are correct. Do NOT call get_sales.
Your job: find out WHY the biggest drop happened, and act on it.
1. For the dish with the biggest drop, check the stock of its main ingredient with get_stock.
2. If that ingredient has run out, you MUST call draft_purchase_order (a sensible amount, at most 50 kg).
3. If a tool returns an ERROR, say what you could not check. Never invent a number.
4. Reply with EXACTLY 3 lines, plain text, no markdown, no headings:
Line 1: total plates yesterday vs last week, with the change.
Line 2: the biggest drop and its cause.
Line 3: the action taken, or "No action needed"."""


# ---------- 1. a stand-in for KitchenOS's sales table ----------
def load_sales_table():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS daily_sales (day TEXT, dish TEXT, plates INTEGER)")
        conn.execute("DELETE FROM daily_sales")                 # reload cleanly every run (ch.14)
        for day, dishes in SALES.items():
            for dish, plates in dishes.items():
                conn.execute("INSERT INTO daily_sales VALUES (?, ?, ?)", (day, dish, plates))


# ---------- 2. the WORKFLOW part: dates and numbers done by code ----------
def sales_facts(run_day):
    yesterday = run_day - timedelta(days=1)
    last_week = yesterday - timedelta(days=7)
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            """SELECT t.dish, t.plates, COALESCE(w.plates, 0) AS before,
                      t.plates - COALESCE(w.plates, 0) AS change
               FROM daily_sales t
               LEFT JOIN daily_sales w ON w.dish = t.dish AND w.day = ?
               WHERE t.day = ?
               ORDER BY change""",
            (last_week.isoformat(), yesterday.isoformat())).fetchall()
    total_now = sum(row[1] for row in rows)
    total_before = sum(row[2] for row in rows)
    lines = [f"{yesterday} vs {last_week}: total {total_now} vs {total_before} plates ({total_now - total_before:+d})"]
    for dish, now, before, change in rows:
        lines.append(f"{dish}: {now} vs {before} ({change:+d})")
    return "\n".join(lines)


# ---------- 3. NEW: check the digest's format in code ----------
def clean(text):
    lines = [line.replace("*", "").replace("#", "").strip() for line in text.splitlines()]
    return [line for line in lines if line]                  # drop empty lines


def check_format(text):
    lines = clean(text)
    if len(lines) != 3:
        return None, f"expected exactly 3 lines, got {len(lines)}"
    return "\n".join(lines), ""


def reformat(text, problem):                                 # the re-ask: one small call, no tools
    resp = client.chat.completions.create(
        model=MODEL, reasoning_effort="low", max_tokens=300,
        messages=[
            {"role": "system", "content": "Rewrite the text as EXACTLY 3 short plain lines: "
                                          "1) totals 2) biggest drop and its cause 3) the action. "
                                          "Keep every number. No markdown, no headings."},
            {"role": "user", "content": f"Problem: {problem}\n\nText:\n{text}"},
        ],
    )
    return resp.choices[0].message.content or ""


def final_digest(raw, facts):
    if raw.startswith("STOPPED"):                            # a hard stop passes straight through
        return raw
    good, problem = check_format(raw)
    if good:
        return good
    print(f"[check] {problem} -> asking once more")
    good, problem = check_format(reformat(raw, problem))
    if good:
        return good
    print(f"[check] still wrong ({problem}) -> sending the code's facts instead")
    return "Digest could not be written. Sales facts:\n" + facts


# ---------- 4. NEW (10c): the orders line is written by CODE, from the DB ----------
def pending_orders_line(outlet="demo"):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS pending_actions (
                            id     INTEGER PRIMARY KEY AUTOINCREMENT,
                            outlet TEXT,
                            item   TEXT,
                            kg     REAL,
                            status TEXT)""")
        rows = conn.execute(
            "SELECT id, item, kg FROM pending_actions WHERE outlet = ? AND status = 'pending'",
            (outlet,)).fetchall()
    if not rows:
        return "No orders waiting for your approval."
    return "Waiting for your approval: " + ", ".join(f"#{action_id} {kg:g} kg {item}" for action_id, item, kg in rows)


# ---------- 5. run it: facts (code) -> agent -> format check (code) ----------
if __name__ == "__main__":
    load_sales_table()
    facts = sales_facts(RUN_DAY)
    print("FACTS (computed by code):\n" + facts + "\n")

    raw = run_agent(RUN_DAY.strftime("%A %Y-%m-%d"), goal=DIGEST_GOAL, facts=facts)
    digest = final_digest(raw or "", facts)

    lines = digest.splitlines()
    if len(lines) == 3:                        # a normal digest: code replaces the model's action line
        lines[2] = pending_orders_line()
    else:                                      # a STOPPED or fallback digest: code adds the line at the end
        lines.append(pending_orders_line())
    digest = "\n".join(lines)
    print("\nDIGEST:\n" + digest)