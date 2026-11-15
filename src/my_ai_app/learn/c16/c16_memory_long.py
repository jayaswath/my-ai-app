import sqlite3
from pathlib import Path

from c16_cost import run_agent

DB_PATH = Path("data") / "agent_runs.db"        # the same register as item 5


# ---------- READ: the last few digests before a date ----------
def recent_digests(before_date, limit=3, outlet="demo"):
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            """SELECT run_date, digest FROM digest_runs
               WHERE outlet = ? AND run_date < ? AND digest IS NOT NULL
               ORDER BY run_date DESC
               LIMIT ?""",
            (outlet, before_date, limit)).fetchall()
    return "\n".join(f"{run_date}: {digest}" for run_date, digest in rows)


# ---------- a past digest, as if the agent ran on Friday morning ----------
with sqlite3.connect(DB_PATH) as conn:
    conn.execute(
        "INSERT INTO digest_runs (outlet, run_date, digest) VALUES (?, ?, ?) ON CONFLICT DO NOTHING",
        ("demo", "2026-10-23", "Paneer down to 2 kg - reorder now  or  Paneer Tikka stops tomorrow."))

# ---------- Saturday's run, now WITH memory ----------
memory = recent_digests("2026-10-24")
print("MEMORY READ FROM THE DB:\n" + (memory or "(nothing)") + "\n")

digest = run_agent("Saturday 2026-10-24", memory)
print("\nDIGEST WITH MEMORY:\n" + digest)