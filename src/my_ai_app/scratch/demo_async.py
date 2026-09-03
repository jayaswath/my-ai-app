import asyncio
import time


async def fetch_data(name: str, delay: float) -> str:
    """Simulate a slow API call without blocking."""
    print(f"Starting {name}...")
    await asyncio.sleep(delay)
    print(f"Finished {name}")
    return f"{name} result"


async def main() -> None:
    """Run three fake API calls concurrently."""
    start = time.perf_counter()

    results = await asyncio.gather(
        fetch_data("call-1", 2),
        fetch_data("call-2", 2),
        fetch_data("call-3", 2),
    )

    elapsed = time.perf_counter() - start
    print(f"Results: {results}")
    print(f"Total: {elapsed:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())
