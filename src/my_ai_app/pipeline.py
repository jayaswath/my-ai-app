import asyncio
import logging
import time

import httpx
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from my_ai_app.database import SessionLocal
from my_ai_app.ingest import fetch_all_posts, fetch_users_concurrently
from my_ai_app.models import Author, Post
from my_ai_app.transform import authors_to_frame, posts_to_frame, save_snapshot

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

POST_COLUMNS = ["external_id", "user_id", "title", "body"]
AUTHOR_COLUMNS = ["external_id", "name", "username", "email", "company", "city"]


def upsert_authors(db: Session, rows: list[dict]) -> None:
    """Insert or update authors by external_id."""
    if not rows:
        return
    stmt = insert(Author).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["external_id"],
        set_={
            "name": stmt.excluded.name,
            "email": stmt.excluded.email,
            "company": stmt.excluded.company,
            "city": stmt.excluded.city,
        },
    )
    db.execute(stmt)
    db.commit()


def upsert_posts(db: Session, rows: list[dict]) -> None:
    """Insert or update posts by external_id."""
    if not rows:
        return
    stmt = insert(Post).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["external_id"],
        set_={
            "title": stmt.excluded.title,
            "body": stmt.excluded.body,
            "user_id": stmt.excluded.user_id,
        },
    )
    db.execute(stmt)
    db.commit()


def top_authors(db: Session, limit: int = 5) -> list[tuple[str, int, float]]:
    """Authors ranked by post count, with their average title length."""
    stmt = (
        select(
            Author.name,
            func.count(Post.id).label("posts"),
            func.round(func.avg(func.length(Post.title)), 1).label("avg_title_len"),
        )
        .join(Post, Post.user_id == Author.external_id)
        .group_by(Author.name)
        .order_by(func.count(Post.id).desc())
        .limit(limit)
    )
    return [(r.name, r.posts, float(r.avg_title_len)) for r in db.execute(stmt)]


async def run() -> None:
    """Fetch, transform, load, snapshot, and report."""
    start = time.perf_counter()

    logger.info("EXTRACT")
    async with httpx.AsyncClient() as client:
        posts = await fetch_all_posts(client)
        user_ids = sorted({p["userId"] for p in posts})
        users = await fetch_users_concurrently(client, user_ids)
    logger.info("  %s posts, %s authors", len(posts), len(users))

    logger.info("TRANSFORM")
    posts_df = posts_to_frame(posts)
    authors_df = authors_to_frame(users)
    logger.info(
        "  avg body words: %.1f | long posts: %s",
        posts_df["body_words"].mean(),
        int(posts_df["is_long"].sum()),
    )

    logger.info("LOAD")
    with SessionLocal() as db:
        before_posts = db.scalar(select(func.count(Post.id))) or 0
        before_authors = db.scalar(select(func.count(Author.id))) or 0

        upsert_authors(db, authors_df[AUTHOR_COLUMNS].to_dict("records"))
        upsert_posts(db, posts_df[POST_COLUMNS].to_dict("records"))

        after_posts = db.scalar(select(func.count(Post.id))) or 0
        after_authors = db.scalar(select(func.count(Author.id))) or 0

        logger.info(
            "  authors +%s (%s) | posts +%s (%s)",
            after_authors - before_authors,
            after_authors,
            after_posts - before_posts,
            after_posts,
        )

        logger.info("TOP AUTHORS")
        for name, count, avg_len in top_authors(db):
            logger.info("  %-20s %s posts  avg title %.1f chars", name, count, avg_len)

    p1 = save_snapshot(posts_df, "posts.parquet")
    p2 = save_snapshot(authors_df, "authors.parquet")
    logger.info("SNAPSHOT  %s, %s", p1, p2)

    logger.info("Done in %.2fs", time.perf_counter() - start)


if __name__ == "__main__":
    asyncio.run(run())
