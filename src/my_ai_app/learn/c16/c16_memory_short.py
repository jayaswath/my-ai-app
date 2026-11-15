# Short-term memory = the messages list. No API calls in this file.

# ---------- a finished agent run, as the messages list looked at the end ----------
messages = [
    {"role": "system", "content": "You are the morning manager... (GOAL)"},
    {"role": "user", "content": "Today is Saturday 2026-10-24. Run the morning check."},
    {"role": "assistant", "content": "", "tool_calls": [{"id": "c1", "function": {"name": "get_sales"}}]},
    {"role": "tool", "tool_call_id": "c1", "content": "2026-10-23: Paneer Tikka 0, Chicken Biryani 40 ... total 58"},
    {"role": "assistant", "content": "", "tool_calls": [{"id": "c2", "function": {"name": "get_sales"}}]},
    {"role": "tool", "tool_call_id": "c2", "content": "2026-10-16: Paneer Tikka 22, Chicken Biryani 42 ... total 84"},
    {"role": "assistant", "content": "", "tool_calls": [{"id": "c3", "function": {"name": "get_stock"}}]},
    {"role": "tool", "tool_call_id": "c3", "content": "paneer: 0 kg - ran out on 2026-10-23 at 2:10 pm"},
]


def show(title, msgs):
    print(f"\n{title}  ({len(msgs)} messages)")
    for m in msgs:
        print(f"  {m['role']:9} {m.get('tool_call_id', '')} {m['content'][:45]}")


# ---------- 1. the naive cut: keep the last 3 ----------
naive = messages[:2] + messages[-3:]
show("NAIVE: first 2 + last 3", naive)


# ---------- 2. the safe cut ----------
def trim(msgs, keep_last=3):
    pinned = msgs[:2]                      # GOAL + trigger: never cut
    recent = msgs[2:][-keep_last:]         # the newest few
    while recent and recent[0]["role"] == "tool":
        recent = recent[1:]                # drop answers whose slip was cut off
    return pinned + recent


show("SAFE: trim(messages, keep_last=3)", trim(messages))