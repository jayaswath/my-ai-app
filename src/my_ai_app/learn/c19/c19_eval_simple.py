import json
import sys
from datetime import datetime
from pathlib import Path

from pydantic import ValidationError

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "c11"))
import c11_extract
from c11_extract import extract_cart

c11_extract.SHOW_RAW = False

if len(sys.argv) > 1:                          # optional: a model name after the file name
    c11_extract.MODEL = sys.argv[1]

cases = json.loads((HERE / "c19_cases.json").read_text(encoding="utf-8"))
passed = 0
results = {}                                   # ticket id -> "PASS" / "FAIL"

for case in cases:
    try:
        cart = extract_cart(case["spoken"])
        got = [[l.item_id, l.qty, l.note] for l in cart.lines]
        ok = got == case.get("lines")              # exact match with the ticket
    except ValidationError:
        ok = case.get("rejects", False)            # refused: good only if the ticket says so
    status = "PASS" if ok else "FAIL"
    print(status, case["spoken"])
    passed += ok
    results[case["id"]] = status

print(passed, "/", len(cases), "passed   model:", c11_extract.MODEL)

# save this run's report card
(HERE / "results").mkdir(exist_ok=True)
out = HERE / "results" / f"run_{datetime.now():%Y%m%d_%H%M%S}.json"
out.write_text(json.dumps({"model": c11_extract.MODEL, "results": results}, indent=2), encoding="utf-8")
print("saved:", out.name)