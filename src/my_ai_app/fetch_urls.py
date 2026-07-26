import asyncio
import time

import httpx


async def fetch_status(client: httpx.AsyncClient, url: str) -> tuple[str, int]:
    """Return the URL and its HTTP status code."""
    response = await client.get(url, timeout=10.0)
    return url, response.status_code


async def main() -> None:
    """Check several URLs concurrently."""
    urls = [
        "https://postman-echo.com/delay/2",
        "https://postman-echo.com/delay/2",
        "https://postman-echo.com/delay/2",
    ]

    start = time.perf_counter()

    async with httpx.AsyncClient() as client:
        tasks = [fetch_status(client, url) for url in urls]
        results = await asyncio.gather(*tasks)

    for url, status in results:
        print(f"{status} — {url}")

    print(f"Total: {time.perf_counter() - start:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())
