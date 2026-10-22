"""
c12_generate.py  —  let the trained mini-GPT write its own dockets.
Chapter 12, item 22.  The generate() loop is PRACTISE; the loading part is READ (item 24).
"""
import torch
import torch.nn.functional as F

from c12_minigpt import CharTokenizer, MiniGPT

torch.manual_seed(7)

# ── 1. load the trained model (READ — item 24 explains these lines) ──────────
saved = torch.load("data/c12_minigpt.pt")
tok = CharTokenizer("")
tok.chars = saved["chars"]
tok.stoi = {ch: i for i, ch in enumerate(tok.chars)}
tok.itos = {i: ch for i, ch in enumerate(tok.chars)}

model = MiniGPT(vocab_size=len(tok.chars))
model.load_state_dict(saved["model"])
model.eval()


# ── 2. peek: what does the model think comes next? ──────────────────────────
@torch.no_grad()
def show_next(prompt, k=5):
    idx = torch.tensor([tok.encode(prompt)])
    logits, _ = model(idx)
    probs = F.softmax(logits[0, -1], dim=-1)
    top = torch.topk(probs, k)
    shown = "  ".join(f"{tok.itos[i.item()]!r} {p.item():.0%}"
                      for p, i in zip(top.values, top.indices))
    print(f"{prompt!r:22} -> {shown}")


# ── 3. the generation loop (PRACTISE) ────────────────────────────────────────
@torch.no_grad()
def generate(idx, n_new):
    for _ in range(n_new):
        ctx = idx[:, -model.block_size:]          # keep only the last 64 characters
        logits, _ = model(ctx)                    # a score for every character, at every position
        logits = logits[:, -1, :]                 # we only need the LAST position's scores
        probs = F.softmax(logits, dim=-1)         # scores -> percentages that add to 100%
        nxt = torch.multinomial(probs, 1)         # roll the dice, weighted by those percentages
        idx = torch.cat([idx, nxt], dim=1)        # stick the new character on the end, go again
    return idx


print("── what comes next? ──")
show_next("ORDER 12")
show_next("2 x ")
show_next("2 x Chicken B")
show_next("1 x Filter Coffee [")

print("\n── the model writes dockets ──")
start = torch.tensor([tok.encode("ORDER ")])
print(tok.decode(generate(start, 200)[0].tolist()))