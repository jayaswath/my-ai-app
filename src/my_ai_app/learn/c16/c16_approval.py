import sqlite3
from pathlib import Path

DB_PATH = Path("data") / "agent_runs.db"


# ---------- the REAL action: only ever called after a yes ----------
def place_order(item, kg):
    print(f"   >>> ORDER SENT TO SUPPLIER: {kg} kg {item}")


# ---------- what is waiting for the owner ----------
def show_pending(outlet="demo"):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS pending_actions (
                            id     INTEGER PRIMARY KEY AUTOINCREMENT,
                            outlet TEXT,
                            item   TEXT,
                            kg     REAL,
                            status TEXT)""")
        return conn.execute(
            "SELECT id, item, kg FROM pending_actions WHERE outlet = ? AND status = 'pending'",
            (outlet,)).fetchall()


# ---------- the owner's yes / no ----------
def decide(action_id, approve, outlet="demo"):
    new_status = "approved" if approve else "rejected"
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "UPDATE pending_actions SET status = ? WHERE id = ? AND outlet = ? AND status = 'pending'",
            (new_status, action_id, outlet))
        if cur.rowcount == 0:                       # already decided, or not this outlet's
            return f"#{action_id}: nothing pending - not done again"
        item, kg = conn.execute(
            "SELECT item, kg FROM pending_actions WHERE id = ?", (action_id,)).fetchone()
    if approve:
        place_order(item, kg)
    return f"#{action_id}: {new_status}"


pending = show_pending()
if not pending:
    print("Nothing waiting for approval.")
for action_id, item, kg in pending:
    answer = input(f"Order #{action_id}: {kg} kg {item}. Approve? (y/n): ").strip().lower()
    print(decide(action_id, answer == "y"))