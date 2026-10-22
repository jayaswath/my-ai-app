import torch

a = torch.tensor([1.0, 2.0, 3.0, 4.0])

print("a       =", a)
print("a.shape =", a.shape)
print("a.dtype =", a.dtype)

orders = torch.tensor([[18.0, 6.2, 3.0],
                       [ 4.0, 2.1, 9.0],
                       [22.0, 8.0, 2.0]])

print("orders =\n", orders)
print("shape       :", orders.shape)
print("rows, cols  :", orders.shape[0], orders.shape[1])
print("row 0       :", orders[0])
print("row 0, col 1:", orders[0][1])
print("all of col 0:", orders[:, 0])

flat = torch.tensor([1.0, 2.0, 3.0, 4.0])
row = flat.reshape(1, 4)
col = flat.reshape(4, 1)

for name, t in [("flat", flat), ("row ", row), ("col ", col)]:
    print(f"{name}  shape {str(tuple(t.shape)):8s}  {t.tolist()}")