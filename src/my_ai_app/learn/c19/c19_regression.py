import json
from pathlib import Path

RESULTS = Path(__file__).parent / "results"

baseline = json.loads((RESULTS / "baseline.json").read_text(encoding="utf-8"))
latest_file = sorted(RESULTS.glob("run_*.json"))[-1]          # the newest run
latest = json.loads(latest_file.read_text(encoding="utf-8"))

broke = 0
for ticket_id, old in baseline["results"].items():
    new = latest["results"].get(ticket_id)
    if old == "PASS" and new != "PASS":
        print("BROKE ticket", ticket_id)
        broke += 1

print("baseline:", baseline["model"], "   latest:", latest["model"], latest_file.name)
print("REGRESSION: don't ship" if broke else "no regressions: safe to ship")