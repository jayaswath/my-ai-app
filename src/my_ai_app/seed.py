from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select

from my_ai_app.database import SessionLocal
from my_ai_app.models import Customer, Order


def seed() -> None:
    """Insert sample customers and orders. Safe to run repeatedly."""
    with SessionLocal() as db:
        if db.scalars(select(Customer)).first() is not None:
            print("Already seeded — skipping.")
            return

        try:
            ravi = Customer(name="Ravi", phone="9840011111")
            priya = Customer(name="Priya", phone="9840022222")
            anand = Customer(name="Anand", phone="9840033333")

            db.add_all(
                [
                    Order(
                        customer=ravi,
                        city="Chennai",
                        dish="Biryani",
                        amount=Decimal("250.00"),
                        ordered_at=datetime(2026, 7, 1, 12, 30, tzinfo=UTC),
                    ),
                    Order(
                        customer=priya,
                        city="Bengaluru",
                        dish="Dosa",
                        amount=Decimal("120.00"),
                        ordered_at=datetime(2026, 7, 1, 13, 15, tzinfo=UTC),
                    ),
                    Order(
                        customer=ravi,
                        city="Chennai",
                        dish="Dosa",
                        amount=Decimal("120.00"),
                        ordered_at=datetime(2026, 7, 2, 19, 0, tzinfo=UTC),
                    ),
                    Order(
                        customer=anand,
                        city="Chennai",
                        dish="Biryani",
                        amount=Decimal("250.00"),
                        ordered_at=datetime(2026, 7, 2, 20, 10, tzinfo=UTC),
                    ),
                ]
            )
            db.commit()
            print("Seeded 3 customers and 4 orders.")

        except Exception:
            db.rollback()
            raise


if __name__ == "__main__":
    seed()
