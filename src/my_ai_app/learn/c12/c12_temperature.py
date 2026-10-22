"""
c12_temperature.py  —  the two knobs you will set in every API call: temperature and top-p.
Chapter 12, item 23.  READ + RUN.  Only the 3 marked lines are worth knowing.
"""
import torch
import torch.nn.functional as F

from c12_minigpt import CharTokenizer, MiniGPT

# ── load the trained model (same as c12_generate.py) ─────────────────────────
saved = torch.load("data/c12_minigpt.pt")
tok = CharTokenizer("")
tok.chars = saved["chars"]
tok.stoi = {ch: i for i, ch in enumerate(tok.chars)}
tok.itos = {i: ch for i, ch in enumerate(tok.chars)}
model = MiniGPT(vocab_size=len(tok.chars))
model.load_state_dict(saved["model"])
model.eval()


def apply_knobs(logits, temperature=1.0, top_p=1.0):
    logits = logits / temperature                              # KNOW: temperature
    probs = F.softmax(logits, dim=-1)
    if top_p < 1.0:
        sorted_p, order = torch.sort(probs, descending=True)
        keep = torch.cumsum(sorted_p, dim=-1) - sorted_p < top_p   # KNOW: top-p keeps the top until p is reached
        mask = torch.zeros_like(probs, dtype=torch.bool)
        mask[order[keep]] = True
        probs = torch.where(mask, probs, torch.zeros_like(probs))
        probs = probs / probs.sum()                            # KNOW: share out the 100% again
    return probs


@torch.no_grad()
def show(prompt, temperature=1.0, top_p=1.0, k=6):
    logits, _ = model(torch.tensor([tok.encode(prompt)]))
    probs = apply_knobs(logits[0, -1], temperature, top_p)
    top = torch.topk(probs, k)
    shown = "  ".join(f"{tok.itos[i.item()]!r} {p.item():4.0%}"
                      for p, i in zip(top.values, top.indices))
    print(f"T={temperature:<4} top_p={top_p:<4} -> {shown}")


@torch.no_grad()
def generate(prompt, n_new, temperature=1.0, top_p=1.0):
    idx = torch.tensor([tok.encode(prompt)])
    for _ in range(n_new):
        logits, _ = model(idx[:, -model.block_size:])
        probs = apply_knobs(logits[0, -1], temperature, top_p)
        nxt = torch.multinomial(probs, 1).view(1, 1)
        idx = torch.cat([idx, nxt], dim=1)
    return tok.decode(idx[0].tolist())


print("── one list, four knob settings:  '2 x ' → ? ──")
show("2 x ", temperature=1.0)
show("2 x ", temperature=0.3)
show("2 x ", temperature=2.0)
show("2 x ", temperature=1.0, top_p=0.7)

for t in (0.3, 1.0, 3.0):
    torch.manual_seed(7)
    print(f"\n── dockets at temperature {t} ──")
    print(generate("ORDER ", 120, temperature=t))