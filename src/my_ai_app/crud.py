from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from my_ai_app.models import Customer, Order


def create_customer(db: Session, name: str, phone: str | None = None) -> Customer:
    """Insert a new customer and return it with its generated ID."""
    customer = Customer(name=name, phone=phone)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def get_customer_by_name(db: Session, name: str) -> Customer | None:
    """Return the customer with this name, or None if not found."""
    stmt = select(Customer).where(Customer.name == name)
    return db.scalars(stmt).first()


def get_orders_by_city(db: Session, city: str) -> list[Order]:
    """Return all orders placed in a city, newest first."""
    stmt = select(Order).where(Order.city == city).order_by(Order.ordered_at.desc())
    return list(db.scalars(stmt).all())


def get_orders_with_customers(db: Session) -> list[Order]:
    """Return all orders with their customer preloaded (avoids N+1)."""
    stmt = select(Order).options(joinedload(Order.customer))
    return list(db.scalars(stmt).all())


def revenue_by_city(db: Session) -> list[tuple[str, Decimal]]:
    """Return total revenue per city, highest first."""
    stmt = (
        select(Order.city, func.sum(Order.amount).label("revenue"))
        .group_by(Order.city)
        .order_by(func.sum(Order.amount).desc())
    )
    return [(row.city, row.revenue) for row in db.execute(stmt)]


def get_or_create_customer(
    db: Session, name: str, phone: str | None = None
) -> Customer:
    """Return the existing customer with this name, or create one."""
    existing = get_customer_by_name(db, name)
    if existing is not None:
        return existing
    return create_customer(db, name, phone)
