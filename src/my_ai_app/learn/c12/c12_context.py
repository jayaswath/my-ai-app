"""
c12_context.py  —  the context window, and why doubling a prompt costs 4x in attention.
Chapter 12, item 25.  READ + RUN.  Nothing here to memorise.
"""
import time

import torch

from c12_minigpt import CharTokenizer, MiniGPT

saved = torch.load("data/c12_minigpt.pt")
tok = CharTokenizer("")
tok.chars = saved["chars"]
tok.stoi = {ch: i for i, ch in enumerate(tok.chars)}
model = MiniGPT(vocab_size=len(tok.chars))
model.load_state_dict(saved["model"])
model.eval()

# ── A. the window: 64 seats, no more ─────────────────────────────────────────
docket = "ORDER 1\n2 x Chicken Biryani\n1 x Filter Coffee [no sugar]\n3 x Chai\n1 x"
print(f"docket is {len(docket)} characters")

with torch.no_grad():
    ok = torch.tensor([tok.encode(docket[:64])])
    model(ok)
    print("64 characters  -> fine")
    try:
        too_long = torch.tensor([tok.encode(docket[:65])])
        model(too_long)
    except IndexError as e:
        print(f"65 characters  -> CRASH: {e}")

# ── B. the n x n grid: double the length, 4x the work ────────────────────────
print("\n  tokens      scores (n x n)    time")
torch.manual_seed(0)
prev = None
for n in (512, 1024, 2048, 4096):
    q = torch.randn(n, 64)
    k = torch.randn(n, 64)
    q @ k.T                                     # warm-up
    t0 = time.perf_counter()
    for _ in range(5):
        scores = q @ k.T                        # every token vs every token
    ms = (time.perf_counter() - t0) / 5 * 1000
    grow = f"  x{ms / prev:.1f}" if prev else ""
    print(f"{n:8,}  {scores.numel():16,}   {ms:7.1f} ms{grow}")
    prev = ms