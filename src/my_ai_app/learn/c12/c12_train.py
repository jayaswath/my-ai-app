"""
c12_train.py  —  train the mini-GPT on KitchenOS dockets, then save it.
Chapter 12, item 21.  RUN it; don't study it.
"""
import math
import time
from pathlib import Path

import torch

from c12_minigpt import CharTokenizer, MiniGPT, make_dockets

torch.manual_seed(42)

text = make_dockets()
tok  = CharTokenizer(text)
data = torch.tensor(tok.encode(text))

model = MiniGPT(vocab_size=len(tok.chars))
print(f"text: {len(text):,} characters   menu: {len(tok.chars)} characters")
print(f"model: {sum(p.numel() for p in model.parameters()):,} parameters")
print(f"pure guessing would be loss ln({len(tok.chars)}) = {math.log(len(tok.chars)):.2f}\n")


def get_batch(batch_size=32, T=64):
    starts = torch.randint(len(data) - T - 1, (batch_size,))
    x = torch.stack([data[s : s + T] for s in starts])
    y = torch.stack([data[s + 1 : s + T + 1] for s in starts])
    return x, y


optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
t0 = time.time()

for step in range(801):
    x, y = get_batch()
    _, loss = model(x, y)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    if step % 100 == 0:
        sure = math.exp(-loss.item())
        print(f"step {step:4}   loss {loss.item():.4f}   "
              f"~{sure:5.1%} sure of the next character   {time.time() - t0:5.0f}s")

Path("data").mkdir(exist_ok=True)
torch.save({"model": model.state_dict(), "chars": tok.chars}, "data/c12_minigpt.pt")
print("\nsaved to data/c12_minigpt.pt")