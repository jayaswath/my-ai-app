import torch

w = torch.tensor(0.5, requires_grad=True)
load, truth = 18.0, 15.0

pred = w * load
error = (pred - truth) ** 2

print("w          :", w.item())
print("prediction :", pred.item())
print("truth      :", truth)
print("error      :", error.item())
print("w.grad before backward:", w.grad)

error.backward()
print("w.grad after backward :", w.grad.item())

lr = 0.001

with torch.no_grad():
    w -= lr * w.grad

print("new w         :", w.item())
print("new prediction:", (w * load).item())

v = torch.tensor(2.0, requires_grad=True)

for i in range(1, 4):
    if v.grad is not None:
        v.grad.zero_()          # wipe the pad
    out = v * 3
    out.backward()
    print(f"after backward #{i}: v.grad = {v.grad.item()}")