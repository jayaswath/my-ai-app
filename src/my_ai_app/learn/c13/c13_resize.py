from pathlib import Path

from PIL import Image

src = Path("data") / "sample_bill.jpg"
dst = Path("data") / "sample_bill_small.jpg"

img = Image.open(src)
print("before:", img.size, src.stat().st_size // 1024, "KB")

img.thumbnail((600, 600))
img.save(dst, quality=80)

print("after: ", img.size, dst.stat().st_size // 1024, "KB")