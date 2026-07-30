import asyncio
import logging
import time

import httpx
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from my_ai_app.database import SessionLocal
from my_ai_app.models import Post

logging.basicConfig(level=logging.INFO, format="%(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

BASE_URL = "https://jsonplaceholder.typicode.com"
PAGE_SIZE = 20
MAX_PAGES = 20
CONCURRENCY = 5


@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1, min=1, max=20),
    retry=retry_if_exception_type(
        (httpx.TimeoutException, httpx.HTTPStatusError, httpx.ConnectError)
    ),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
async def fetch_page(client: httpx.AsyncClient, page: int) -> list[dict]:
    """Fetch one page of posts, retrying on network or server errors."""
    response = await client.get(
        f"{BASE_URL}/posts",
        params={"_page": page, "_limit": PAGE_SIZE},
        timeout=10.0,
    )

    if response.status_code == 429:
        wait = int(response.headers.get("Retry-After", 30))
        logger.warning("Rate limited. Waiting %ss", wait)
        await asyncio.sleep(wait)

    response.raise_for_status()
    return response.json()


async def fetch_all_posts(client: httpx.AsyncClient) -> list[dict]:
    """Walk through every page until an empty one comes back."""
    all_posts: list[dict] = []
    page = 1

    while page <= MAX_PAGES:
        posts = await fetch_page(client, page)

        if not posts:
            logger.info("Page %s empty - done", page)
            break

        all_posts.extend(posts)
        logger.info("  page %s: %s items", page, len(posts))
        page += 1

    return all_posts


async def fetch_users_concurrently(
    client: httpx.AsyncClient, user_ids: list[int]
) -> list[dict]:
    """Fetch several users at once, capped at CONCURRENCY in flight."""
    semaphore = asyncio.Semaphore(CONCURRENCY)

    async def fetch_one(user_id: int) -> dict:
        async with semaphore:
            response = await client.get(f"{BASE_URL}/users/{user_id}", timeout=10.0)
            response.raise_for_status()
            return response.json()

    results = await asyncio.gather(
        *[fetch_one(uid) for uid in user_ids], return_exceptions=True
    )

    good = [r for r in results if not isinstance(r, Exception)]
    failed = len(results) - len(good)
    if failed:
        logger.warning("%s user fetches failed", failed)
    return good


def upsert_posts(db: Session, posts: list[dict]) -> int:
    """Insert posts, updating any that already exist. Safe to re-run."""
    if not posts:
        return 0

    rows = [
        {
            "external_id": p["id"],
            "user_id": p["userId"],
            "title": p["title"],
            "body": p["body"],
        }
        for p in posts
    ]

    stmt = insert(Post).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["external_id"],
        set_={
            "title": stmt.excluded.title,
            "body": stmt.excluded.body,
            "user_id": stmt.excluded.user_id,
        },
    )

    result = db.execute(stmt)
    db.commit()
    return result.rowcount


async def run_pipeline() -> None:
    """Fetch posts and users, then load into Postgres."""
    start = time.perf_counter()

    async with httpx.AsyncClient() as client:
        logger.info("Fetching posts...")
        posts = await fetch_all_posts(client)
        logger.info("Fetched %s posts", len(posts))

        user_ids = sorted({p["userId"] for p in posts})
        logger.info(
            "Fetching %s users, max %s at a time...", len(user_ids), CONCURRENCY
        )
        users = await fetch_users_concurrently(client, user_ids)
        logger.info("Fetched %s users", len(users))

    with SessionLocal() as db:
        before = db.query(Post).count()
        upsert_posts(db, posts)
        after = db.query(Post).count()
        logger.info("New posts: %s | Total: %s", after - before, after)

    logger.info("Done in %.2fs", time.perf_counter() - start)


if __name__ == "__main__":
    asyncio.run(run_pipeline())
