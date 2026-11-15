import json
import sys
import time
from pathlib import Path

from pydantic import ValidationError

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "c11"))
import c11_extract
from c11_extract import extract_cart

c11_extract.SHOW_RAW = False

PRICE_IN = 12.67           # Rs per 1M input tokens  (same numbers as ch.16, gpt-oss-120b)
PRICE_OUT = 50.70          # Rs per 1M output tokens
SLOW_MS = 2000             # warn if p95 is slower than this
MAX_RS_PER_ORDER = 0.05    # warn if one order costs more than this

calls = []                 # one (milliseconds, rupees) per LLM call

# ── spy on the Groq call: measure time and cost ──
original_create = c11_extract.client.chat.completions.create

def measured_create(**kwargs):
    start = time.perf_counter()
    response = original_create(**kwargs)
    ms = round((time.perf_counter() - start) * 1000)
    rs = (response.usage.prompt_tokens / 1_000_000 * PRICE_IN
          + response.usage.completion_tokens / 1_000_000 * PRICE_OUT)
    calls.append((ms, rs))
    return response

c11_extract.client.chat.completions.create = measured_create

# ── run the 12 tickets: here we only MEASURE, not mark right or wrong ──
cases = json.loads((HERE / "c19_cases.json").read_text(encoding="utf-8"))
for case in cases:
    try:
        extract_cart(case["spoken"])
    except ValidationError:
        pass                                   # attack tickets get refused; still measured

# ── the numbers ──
times = sorted(ms for ms, rs in calls)

def percentile(p):
    return times[min(len(times) - 1, len(times) * p // 100)]

p50, p95 = percentile(50), percentile(95)
total_rs = sum(rs for ms, rs in calls)
per_order = total_rs / len(calls)

print(f"{len(calls)} LLM calls, model {c11_extract.MODEL}")
print(f"latency : p50 {p50} ms    p95 {p95} ms    slowest {times[-1]} ms")
print(f"cost    : total Rs {total_rs:.4f}    per order Rs {per_order:.5f}")
print(f"example : 300 orders a day for 30 days = Rs {per_order * 300 * 30:.0f} a month")

if p95 > SLOW_MS:
    print(f"WARNING: p95 is {p95} ms, slower than {SLOW_MS} ms")
if per_order > MAX_RS_PER_ORDER:
    print(f"WARNING: one order costs Rs {per_order:.4f}, more than Rs {MAX_RS_PER_ORDER}")