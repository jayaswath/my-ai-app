MENU = {"Chai": 20, "Biryani": 180, "Dosa": 60}

def price_of(dish: str) -> int:
    return MENU[dish]

print("kitchen_tools loaded, __name__ =", __name__)

if __name__ == "__main__":
    print("self-test:", price_of("Chai"))