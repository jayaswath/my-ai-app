import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import torch.nn as nn

train_data = datasets.MNIST(
    root="./data",
    train=True,
    download=True,
    transform=transforms.ToTensor(),
)

print("how many images:", len(train_data))

img, label = train_data[0]
print("one image shape:", img.shape)
print("its label      :", label)

for row in img[0]:
    print("".join("#" if v > 0.9 else ("+" if v > 0.01 else ".") for v in row))


#Training Batchwise
train_loader = DataLoader(train_data, batch_size=64, shuffle=True)

print("batches per epoch:", len(train_loader))

images, labels = next(iter(train_loader))
print("images:", images.shape)
print("labels:", labels.shape)
print("first 8 labels:", labels[:8])


#Training a simple CNN on MNIST
torch.manual_seed(42)

model = nn.Sequential(
    nn.Conv2d(1, 32, 3), nn.ReLU(), nn.MaxPool2d(2),
    nn.Conv2d(32, 64, 3), nn.ReLU(), nn.MaxPool2d(2),
    nn.Flatten(),
    nn.Linear(1600, 10),
)

loss_fn   = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

for epoch in range(1):
    for i, (images, labels) in enumerate(train_loader):
        preds = model(images)            # 1. guess
        loss  = loss_fn(preds, labels)   # 2. measure
        optimizer.zero_grad()            # 3. wipe
        loss.backward()                  # 4. directions
        optimizer.step()                 # 5. nudge

        if i % 100 == 0:
            print(f"batch {i:4d}   loss {loss.item():.4f}")

#Test the model on MNIST test set
test_data = datasets.MNIST(
    root="./data", train=False, download=True, transform=transforms.ToTensor()
)
test_loader = DataLoader(test_data, batch_size=256, shuffle=False)

model.eval()

correct = 0
total   = 0

with torch.no_grad():
    for images, labels in test_loader:
        preds = model(images)
        guess = preds.argmax(dim=1)
        correct += (guess == labels).sum().item()
        total   += labels.size(0)

print(f"correct : {correct} / {total}")
print(f"accuracy: {100 * correct / total:.2f}%")


w = model[0].weight.detach()
print("filter bank shape:", w.shape)

for k in range(8):
    f = w[k, 0]
    vert = (f[:, 0].sum() - f[:, 2].sum()).item()
    horz = (f[0, :].sum() - f[2, :].sum()).item()
    print(f"filter {k}:   vertical {vert:+.3f}    horizontal {horz:+.3f}")