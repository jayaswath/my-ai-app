import asyncio
import time

async def cook(dish):
    print("start", dish)
    await asyncio.sleep(1)
    print("done ", dish)

async def main():
    await asyncio.gather(cook("Biryani"), cook("Dosa"), cook("Chai"))

start = time.perf_counter()
asyncio.run(main())
print(f"total: {time.perf_counter() - start:.1f}s")