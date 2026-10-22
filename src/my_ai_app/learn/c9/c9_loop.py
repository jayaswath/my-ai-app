import torch

loads  = torch.tensor([10.0, 15.0, 18.0, 22.0, 8.0])
truths = torch.tensor([ 8.0, 12.0, 14.4, 17.6, 6.4])

w = torch.tensor(0.8, requires_grad=True)
lr = 0.001

for epoch in range(201):
    preds = w * loads                        # 1. guess
    loss = ((preds - truths) ** 2).mean()    # 2. measure

    if w.grad is not None:
        w.grad.zero_()                       # 3. wipe the pad
    loss.backward()                          # 4. get directions
    with torch.no_grad():
        w -= lr * w.grad                     # 5. nudge

    if epoch % 40 == 0:
        print(f"epoch {epoch:3d}   w {w.item():.4f}   loss {loss.item():8.4f}")

print("\nlearned w :", round(w.item(), 4))
print("planted w : 0.8")