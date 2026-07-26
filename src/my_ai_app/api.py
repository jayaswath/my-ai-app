from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException

from my_ai_app.schemas import DishRequest, DishResponse, GSTRequest, GSTResponse

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
