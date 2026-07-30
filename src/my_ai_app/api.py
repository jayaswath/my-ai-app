from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from my_ai_app.database import get_db
from my_ai_app.models import Author, Post
from my_ai_app.schemas import (
    AuthorOut,
    DishRequest,
    DishResponse,
    GSTRequest,
    GSTResponse,
    PostOut,
    StatsOut,
)

app = FastAPI(
    title="My AI App",
    description="Learning production Python",
    version="0.1.0",
)

DISHES: dict[int, str] = {1: "Biryani", 2: "Dosa"}

GST_RATE = 0.025


@app.get("/health")
async def health() -> dict[str, str]:
    """Return service status."""
    return {"status": "ok"}


@app.get("/dishes")
async def list_dishes() -> dict[int, str]:
    """Return all dishes."""
    return DISHES


@app.get("/dishes/{dish_id}")
async def get_dish(dish_id: int) -> dict[str, str]:
    """Return a dish by ID."""
    if dish_id not in DISHES:
        raise HTTPException(status_code=404, detail=f"Dish {dish_id} not found")
    return {"name": DISHES[dish_id]}


@app.post("/dishes", response_model=DishResponse, status_code=201)
async def create_dish(dish: DishRequest) -> DishResponse:
    """Calculate profit and margin for a dish."""
    profit = dish.selling_price - dish.cost
    margin = (profit / dish.selling_price) * 100

    return DishResponse(
        name=dish.name,
        selling_price=dish.selling_price,
        cost=dish.cost,
        profit=round(profit, 2),
        margin_percent=round(margin, 2),
    )


@app.post("/gst", response_model=GSTResponse)
async def calculate_gst(request: GSTRequest) -> GSTResponse:
    """Split an order amount into CGST and SGST at 2.5% each."""
    cgst = round(request.amount * GST_RATE, 2)
    sgst = round(request.amount * GST_RATE, 2)

    return GSTResponse(
        amount=request.amount,
        cgst=cgst,
        sgst=sgst,
        total=round(request.amount + cgst + sgst, 2),
    )


async def verify_token(x_api_key: Annotated[str, Header()]) -> str:
    """Reject requests without a valid API key."""
    if x_api_key != "secret-dev-key":
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


@app.get("/protected")
async def protected_route(
    token: Annotated[str, Depends(verify_token)],
) -> dict[str, str]:
    """An endpoint requiring authentication."""
    return {"message": "You're in"}


DbSession = Annotated[Session, Depends(get_db)]


@app.get("/posts", response_model=list[PostOut])
async def list_posts(
    db: DbSession,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    author_id: int | None = None,
) -> list[Post]:
    """Serve items off the shelf, at most `limit` per order.

    The customer cannot demand the entire warehouse - `le=100` is the
    house rule. `offset` is how they ask for the next tray.
    """
    stmt = select(Post).order_by(Post.external_id)

    if author_id is not None:
        stmt = stmt.where(Post.user_id == author_id)

    stmt = stmt.limit(limit).offset(offset)
    return list(db.scalars(stmt).all())


@app.get("/authors", response_model=list[AuthorOut])
async def list_authors(db: DbSession) -> list[Author]:
    """Show the supplier book."""
    stmt = select(Author).order_by(Author.name)
    return list(db.scalars(stmt).all())


@app.get("/authors/{external_id}", response_model=AuthorOut)
async def get_author(external_id: int, db: DbSession) -> Author:
    """Look up one supplier by their ID.

    Not in the book? Say so plainly - don't hand back an empty page
    and pretend it worked.
    """
    stmt = select(Author).where(Author.external_id == external_id)
    author = db.scalars(stmt).first()

    if author is None:
        raise HTTPException(status_code=404, detail=f"Author {external_id} not found")

    return author


@app.get("/stats", response_model=StatsOut)
async def get_stats(db: DbSession) -> StatsOut:
    """The summary board: what's on the shelves right now."""
    total_posts = db.scalar(select(func.count(Post.id))) or 0
    total_authors = db.scalar(select(func.count(Author.id))) or 0
    avg_len = db.scalar(select(func.avg(func.length(Post.title)))) or 0

    return StatsOut(
        total_posts=total_posts,
        total_authors=total_authors,
        avg_title_length=round(float(avg_len), 1),
    )
