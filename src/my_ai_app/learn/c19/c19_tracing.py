import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "c16"))
import c16_cost                                    # your ch.16 agent, unchanged

spans = []                                         # the timeline: (what, milliseconds)

# ── spy 1: time every LLM call ──
original_create = c16_cost.client.chat.completions.create

def traced_create(**kwargs):
    start = time.perf_counter()
    response = original_create(**kwargs)
    spans.append(("LLM call", round((time.perf_counter() - start) * 1000)))
    return response

c16_cost.client.chat.completions.create = traced_create

# ── spy 2: time every tool call (same trick as items 6 and 7) ──
original_run_tool = c16_cost.run_tool

def traced_run_tool(name, arguments):
    start = time.perf_counter()
    result = original_run_tool(name, arguments)
    spans.append((f"tool {name}", round((time.perf_counter() - start) * 1000)))
    return result

c16_cost.run_tool = traced_run_tool

# ── the whole run = the trace ──
start = time.perf_counter()
digest = c16_cost.run_agent("Saturday 2026-10-24")
total = round((time.perf_counter() - start) * 1000)

print("\nTRACE (one run)")
print(f"run_agent                      {total:6} ms")
for what, ms in spans:
    print(f"   {what:27} {ms:6} ms")

llm_ms = sum(ms for what, ms in spans if what == "LLM call")
print(f"\nLLM calls took {llm_ms} of {total} ms ({llm_ms * 100 // max(total, 1)}%)")