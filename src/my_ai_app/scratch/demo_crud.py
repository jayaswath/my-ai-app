from my_ai_app import crud
from my_ai_app.database import SessionLocal


def main() -> None:
    """Exercise the CRUD functions."""
    with SessionLocal() as db:
        print("--- Chennai orders ---")
        for order in crud.get_orders_by_city(db, "Chennai"):
            print(f"  {order.dish:10} {order.amount}")

        print("\n--- Revenue by city ---")
        for city, revenue in crud.revenue_by_city(db):
            print(f"  {city:12} {revenue}")

        print("\n--- Orders with customers ---")
        for order in crud.get_orders_with_customers(db):
            print(f"  {order.customer.name:8} {order.dish}")


if __name__ == "__main__":
    main()
