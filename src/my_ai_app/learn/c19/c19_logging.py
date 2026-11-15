import json
import logging
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "c16"))
import c16_cost                                    # your ch.16 agent, unchanged

# ── where log lines go: the screen AND a file ──
(HERE / "logs").mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO, format="%(message)s",
                    handlers=[logging.StreamHandler(sys.stdout),
                              logging.FileHandler(HERE / "logs" / "agent.jsonl", encoding="utf-8")])
logging.getLogger("httpx").setLevel(logging.WARNING)   # hide the Groq library's own "HTTP Request" lines
log = logging.getLogger("kitchen")

RUN_ID = uuid.uuid4().hex[:8]                      # ONE id for this whole run


def log_event(event, data):
    line = {"time": datetime.now().isoformat(timespec="seconds"), "run_id": RUN_ID, "event": event}
    line.update(data)
    log.info(json.dumps(line))


# ── the same spy idea as item 6, but it LOGS each tool call ──
original_run_tool = c16_cost.run_tool

def logged_run_tool(name, arguments):
    start = time.perf_counter()
    result = original_run_tool(name, arguments)
    try:
        args = json.loads(arguments)
    except json.JSONDecodeError:
        args = arguments
    log_event("tool_call", {"tool": name, "args": args,
                            "ok": not result.startswith("ERROR"),
                            "ms": round((time.perf_counter() - start) * 1000)})
    return result

c16_cost.run_tool = logged_run_tool


log_event("run_start", {"agent": "digest", "outlet": "demo"})
digest = c16_cost.run_agent("Saturday 2026-10-24")
log_event("run_end", {"stopped": digest.startswith("STOPPED"), "digest_chars": len(digest)})