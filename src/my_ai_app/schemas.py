from pydantic import BaseModel, ConfigDict, Field


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


class AuthorOut(BaseModel):
    """What we show a customer about a supplier.

    The supplier's full paperwork stays in the back office - the customer
    only sees name, company and city. Nothing else leaves the kitchen.
    """

    model_config = ConfigDict(from_attributes=True)

    external_id: int
    name: str
    username: str
    email: str
    company: str | None
    city: str | None


class PostOut(BaseModel):
    """One item off the shelf, as handed to a customer."""

    model_config = ConfigDict(from_attributes=True)

    external_id: int
    user_id: int
    title: str
    body: str


class StatsOut(BaseModel):
    """The end-of-day summary board."""

    total_posts: int
    total_authors: int
    avg_title_length: float
