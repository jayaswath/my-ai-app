import json

#lists
orders = ["Chai", "Biryani", "Chai", "Dosa"]
print(orders[0])
print(orders[-1])
print(len(orders))

#Dictionaries
menu = {"Chai": 20, "Biryani": 180, "Dosa": 60}
print(menu["Biryani"])
print(menu.get("Coffee"))
print(menu.get("Coffee", 0))

#dict inside list
response = {
    "choices": [
        {"message": {"role": "assistant", "content": "2 x Chai"}}
    ],
    "usage": {"total_tokens": 42},
}
print(response["choices"])
print(response["choices"][0])
print(response["choices"][0]["message"]["content"])
print(response["usage"]["total_tokens"])

def order_total(items: list[str], prices: dict[str, int]) -> int:
    total = 0
    for item in items:
        total = total + prices.get(item, 0)
    return total

def add_gst(amount: int, rate: float = 0.05) -> float:
    return round(amount * (1 + rate), 2)

bill = order_total(orders, menu)
print(bill)
print(add_gst(bill))
print(add_gst(bill, rate=0.18))

#tuple unpacking
line = ("Chai", 2, 20)
name, qty, price = line
print(name, qty * price)

def cheapest_and_dearest(prices: list[int]) -> tuple[int, int]:
    return min(prices), max(prices)

low, high = cheapest_and_dearest([20, 180, 60])
print(low, high)
_, high = cheapest_and_dearest([20, 180, 60])
print(high)

text = "ORDER 12: 2 x Chai"
print(text[0:5])
print(text[6:8])
print(text[-4:])
print(orders[1:3])

#.item(), .join() 
with_gst = [add_gst(p) for p in menu.values()]
print(with_gst)
cheap = [d for d, p in menu.items() if p < 100]
print(cheap)
menu_text = "\n".join(f"{d}: Rs {p}" for d, p in menu.items())
print(menu_text)
print(f"{'Biryani':<10}|{180:>6}|{add_gst(180):.2f}")

#classes and objects

class Docket:
    def __init__(self, order_id: int, items: list[str]):
        self.order_id = order_id
        self.items = items

    def total(self, prices: dict[str, int]) -> int:
        return sum(prices.get(i, 0) for i in self.items)

d1 = Docket(101, ["Chai", "Dosa"])
d2 = Docket(102, ["Biryani"])
print(d1.order_id, d1.items)
print(d1.total(menu))
print(d2.total(menu))
d2.items.append("Chai")
print(d2.items, d2.total(menu))

#try, except, raise

def price_of(dish: str) -> int:
    if dish not in menu:
        raise ValueError(f"{dish} is not on the menu")
    return menu[dish]

for dish in ["Chai", "Pizza", "Dosa"]:
    try:
        print(dish, price_of(dish))
    except ValueError as e:
        print("REJECTED:", e)

#json

text = json.dumps(menu)
print(type(text), text)

back = json.loads('{"item_id": 7, "qty": 2}')
print(type(back), back["qty"])

with open("data/c13_menu.json", "w") as f:
    json.dump(menu, f, indent=2)

with open("data/c13_menu.json") as f:
    loaded = json.load(f)
print(loaded == menu)


#*args , **kwargs

def print_everything(*args, **kwargs):
    print("Positional args (tuple):", args)
    print("Keyword args (dict):", kwargs)

print_everything("Apple", "Banana", price=1.99, store="Groceries")

#@ decorators

# 1. Define the decorator function
def my_logger(original_function):
    def wrapper():
        print(f"LOG: Running '{original_function.__name__}' function...")
        original_function() # Run the actual function
        print("LOG: Function execution finished.")
    return wrapper

# 2. Apply it using the @ symbol
@my_logger
def greet():
    print("Hello, world!")

# 3. Call the function
greet()

