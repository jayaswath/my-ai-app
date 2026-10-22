import torch
import torch.nn as nn

X = torch.tensor([[10.0], [15.0], [18.0], [22.0], [8.0]])
y = torch.tensor([[ 8.0], [12.0], [14.4], [17.6], [ 6.4]])

model     = nn.Linear(1, 1)
loss_fn   = nn.MSELoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.001)

for epoch in range(2001):
    preds = model(X)            # 1. guess
    loss  = loss_fn(preds, y)   # 2. measure
    optimizer.zero_grad()       # 3. wipe
    loss.backward()             # 4. directions
    optimizer.step()            # 5. nudge

    if epoch % 400 == 0:
        print(f"epoch {epoch:4d}   loss {loss.item():9.5f}")

print("\nlearned weight:", round(model.weight.item(), 4), "   planted: 0.8")
print("learned bias  :", round(model.bias.item(), 4))