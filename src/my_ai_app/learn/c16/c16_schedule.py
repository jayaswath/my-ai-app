import sqlite3
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from apscheduler.schedulers.blocking import BlockingScheduler

from c16_cost import run_agent          # the agent from item 4 - not copied, imported

IST = ZoneInfo("Asia/Kolkata")
DB_PATH = Path("data") / "agent_runs.db"
DEMO_DAY = "Saturday 2026-10-24"        # our fake data only has these dates
TEST_MODE = True                        # True = every 30 s, False = 7:00 am IST


# ---------- the run key: one digest per outlet per day ----------
def claim_run(run_date, outlet="demo"):
    """Return True if this run is new, False if today's digest was already claimed."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS digest_runs (
                            outlet   TEXT,
                            run_date TEXT,
                            digest   TEXT,
                            UNIQUE (outlet, run_date))""")
        cur = conn.execute(
            "INSERT INTO digest_runs (outlet, run_date) VALUES (?, ?) ON CONFLICT DO NOTHING",
            (outlet, run_date))
        return cur.rowcount == 1        # 1 row inserted = new; 0 = already there


def save_digest(run_date, digest, outlet="demo"):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE digest_runs SET digest = ? WHERE outlet = ? AND run_date = ?",
                     (digest, outlet, run_date))


# ---------- the job the scheduler calls ----------
def morning_job():
    today = datetime.now(IST).date().isoformat()          # the real date in India
    print(f"\n[{datetime.now(IST):%H:%M:%S}] bell rang for {today}")
    if not claim_run(today):
        print(f"{today}: digest already done - skipping")
        return
    digest = run_agent(DEMO_DAY)
    save_digest(today, digest)
    print(f"{today}: DIGEST\n{digest}")


scheduler = BlockingScheduler(timezone=IST)
if TEST_MODE:
    scheduler.add_job(morning_job, "interval", seconds=30, next_run_time=datetime.now(IST))
else:
    scheduler.add_job(morning_job, "cron", hour=7, minute=0, misfire_grace_time=3600)

print("Scheduler running. Ctrl+C to stop.")
try:
    scheduler.start()                    # blocks here: waits, rings, waits...
except (KeyboardInterrupt, SystemExit):
    print("Stopped.")