import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "c16"))
import c16_cost                                    # your ch.16 agent, unchanged

# ── the spy: write down every tool call, then run the real tool ──
calls = []
original_run_tool = c16_cost.run_tool

def spy_run_tool(name, arguments):
    try:
        args = json.loads(arguments)
    except json.JSONDecodeError:
        args = {}
    calls.append((name, args))
    return original_run_tool(name, arguments)

c16_cost.run_tool = spy_run_tool                   # the agent now calls the spy

# ── run the agent once ──
digest = c16_cost.run_agent("Saturday 2026-10-24")

print("\nTOOL CALLS:")
for name, args in calls:
    print("  ", name, args)
print("\nDIGEST:", digest)

# ── check what it DID, not only what it SAID ──
def called(tool, key, value):
    return any(n == tool and str(a.get(key)).lower() == value for n, a in calls)

drafts = [a for n, a in calls if n == "draft_purchase_order"]

checks = {
    "got yesterday's sales (2026-10-23)":   called("get_sales", "day", "2026-10-23"),
    "got last Friday's sales (2026-10-16)": called("get_sales", "day", "2026-10-16"),
    "checked paneer stock":                 called("get_stock", "item", "paneer"),
    "drafted a paneer order, 1-50 kg":      any(str(a.get("item")).lower() == "paneer"
                                                and 0 < a.get("kg", 0) <= 50 for a in drafts),
    "used 6 tool calls or fewer":           len(calls) <= 6,
    "digest mentions paneer":               "paneer" in digest.lower(),
}

print()
for name, ok in checks.items():
    print("PASS" if ok else "FAIL", name)
print(sum(checks.values()), "/", len(checks), "checks passed")