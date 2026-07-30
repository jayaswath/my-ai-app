from my_ai_app import crud
from my_ai_app.database import SessionLocal


def main() -> None:
    """Insert suppliers and query them back."""
    with SessionLocal() as db:
        if not crud.get_suppliers_by_city(db, "Chennai"):
            crud.create_supplier(db, "Anna Vegetables", "Chennai", "9840055555")
            crud.create_supplier(db, "Marina Meats", "Chennai", "9840066666")
            crud.create_supplier(db, "Cauvery Spices", "Bengaluru", "9840077777")
            print("Created 3 suppliers.")

        print("\n--- Chennai suppliers ---")
        for s in crud.get_suppliers_by_city(db, "Chennai"):
            print(f"  {s.name:20} {s.contact}")

        print("\n--- Orders per dish ---")
        for dish, count in crud.count_orders_per_dish(db):
            print(f"  {dish:10} {count}")


if __name__ == "__main__":
    main()
