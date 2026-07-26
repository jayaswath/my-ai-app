from pydantic import BaseModel, Field


class DishRequest(BaseModel):
    """Incoming data for creating a dish."""

    name: str = Field(min_length=1, max_length=100)
    selling_price: float = Field(gt=0, description="Price in rupees")
    cost: float = Field(ge=0)


class DishResponse(BaseModel):
    """Dish data returned to the client."""

    name: str
    selling_price: float
    cost: float
    profit: float
    margin_percent: float


class GSTRequest(BaseModel):
    """Incoming amount for GST calculation."""

    amount: float = Field(ge=0, description="Order amount in rupees")


class GSTResponse(BaseModel):
    """GST breakdown for an order."""

    amount: float
    cgst: float
    sgst: float
    total: float
