import torch

img = torch.tensor([
    [10., 10., 0., 0., 0.],
    [10., 10., 0., 0., 0.],
    [10., 10., 0., 0., 0.],
    [10., 10., 0., 0., 0.],
    [10., 10., 0., 0., 0.],
])

print("the image:")
print(img)
print("image shape :", img.shape)

x = img.reshape(1, 1, 5, 5)
print("ready shape :", x.shape)

import torch.nn as nn

conv = nn.Conv2d(in_channels=1, out_channels=1, kernel_size=3, bias=False)

edge = torch.tensor([[ 1., 0., -1.],
                     [ 1., 0., -1.],
                     [ 1., 0., -1.]])

with torch.no_grad():
    conv.weight.copy_(edge.reshape(1, 1, 3, 3))

out = conv(x)
print("output shape:", out.shape)
print(out)

img2 = torch.tensor([
    [10., 10., 10., 10., 10.],
    [10., 10., 10., 10., 10.],
    [ 0.,  0.,  0.,  0.,  0.],
    [ 0.,  0.,  0.,  0.,  0.],
    [ 0.,  0.,  0.,  0.,  0.],
])

x2 = img2.reshape(1, 1, 5, 5)
print(conv(x2))

#Max pooling
pool = nn.MaxPool2d(2)

fmap = torch.tensor([
    [30., 28.,  0.,  2.],
    [26., 30.,  3.,  0.],
    [ 0.,  4., 18., 20.],
    [ 2.,  1., 22., 19.],
]).reshape(1, 1, 4, 4)

print("before:", fmap.shape)
print(pool(fmap))
print("after :", pool(fmap).shape)

model = nn.Sequential(
    nn.Conv2d(1, 32, 3),
    nn.ReLU(),
    nn.MaxPool2d(2),

    nn.Conv2d(32, 64, 3),
    nn.ReLU(),
    nn.MaxPool2d(2),

    nn.Flatten(),
    nn.Linear(1600, 10),
)

photo = torch.randn(1, 1, 28, 28)      # a fake 28×28 greyscale image

out = photo
for layer in model:
    out = layer(out)
    print(f"{layer.__class__.__name__:<12} {tuple(out.shape)}")