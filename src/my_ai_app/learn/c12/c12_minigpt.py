"""
c12_minigpt.py  —  the shared pieces: data, tokeniser, model.
Chapter 12, items 19–20.  Imported by c12_train.py and c12_generate.py.
"""
import random

import torch
import torch.nn as nn
import torch.nn.functional as F


# ── the training text: 1,500 made-up KitchenOS dockets ─────────────
def make_dockets(n_orders=1500, seed=42):
    rng = random.Random(seed)
    menu  = ["Chicken Biryani", "Mutton Biryani", "Veg Biryani", "Filter Coffee",
             "Masala Dosa", "Butter Naan", "Vanilla Ice Cream", "Paneer Tikka", "Chai"]
    notes = ["no onion", "extra spicy", "less sugar", "no sugar", "without raita"]
    lines = []
    for n in range(1, n_orders + 1):
        lines.append(f"ORDER {n}")
        for _ in range(rng.randint(1, 4)):
            item = rng.choice(menu)
            qty  = rng.randint(1, 4)
            note = rng.choice(notes) if rng.random() < 0.3 else ""
            lines.append(f"{qty} x {item}" + (f" [{note}]" if note else ""))
        lines.append("")
    return "\n".join(lines)


# ── item 19: the tokeniser ──────────────────────────────────────────
class CharTokenizer:
    def __init__(self, text):
        self.chars = sorted(set(text))
        self.stoi  = {ch: i for i, ch in enumerate(self.chars)}
        self.itos  = {i: ch for i, ch in enumerate(self.chars)}

    def encode(self, s):
        return [self.stoi[c] for c in s]

    def decode(self, ids):
        return "".join(self.itos[i] for i in ids)


# ── item 15: one block ──────────────────────────────────────────────
class Block(nn.Module):
    def __init__(self, d, n_heads):
        super().__init__()
        self.ln1  = nn.LayerNorm(d)
        self.attn = nn.MultiheadAttention(d, n_heads, batch_first=True)
        self.ln2  = nn.LayerNorm(d)
        self.ff   = nn.Sequential(nn.Linear(d, 4 * d), nn.GELU(), nn.Linear(4 * d, d))

    def forward(self, x):
        n    = x.size(1)
        mask = torch.triu(torch.ones(n, n, dtype=torch.bool, device=x.device), diagonal=1)
        h    = self.ln1(x)
        a, _ = self.attn(h, h, h, attn_mask=mask, need_weights=False)
        x    = x + a
        x    = x + self.ff(self.ln2(x))
        return x


# ── item 20: the whole model ────────────────────────────────────────
class MiniGPT(nn.Module):
    def __init__(self, vocab_size, d=64, n_heads=4, n_layers=4, block_size=64):
        super().__init__()
        self.block_size = block_size
        self.tok_emb = nn.Embedding(vocab_size, d)
        self.pos_emb = nn.Embedding(block_size, d)
        self.blocks  = nn.Sequential(*[Block(d, n_heads) for _ in range(n_layers)])
        self.ln_f    = nn.LayerNorm(d)
        self.head    = nn.Linear(d, vocab_size)

    def forward(self, idx, targets=None):
        B, T   = idx.shape
        pos    = torch.arange(T, device=idx.device)
        x      = self.tok_emb(idx) + self.pos_emb(pos)
        x      = self.blocks(x)
        x      = self.ln_f(x)
        logits = self.head(x)

        loss = None
        if targets is not None:
            loss = F.cross_entropy(logits.view(B * T, -1), targets.view(B * T))
        return logits, loss