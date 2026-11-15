# c21_dataset.py  -  ch.21 item 5: build and check a small fine-tuning dataset. Offline, no AI.
# Task we will teach the model: customer review -> one fixed ticket line.
# Run from my-ai-app:  uv run python src/my_ai_app/learn/c21/c21_dataset.py
import json
import random
import re
from pathlib import Path

random.seed(7)                                   # same "random" data every run
HERE = Path(__file__).parent

SYSTEM = "Turn the customer review into one ticket line."

DISHES = ["Chicken Biryani", "Paneer Butter Masala", "Masala Dosa", "Veg Pulao", "Butter Naan", "Gulab Jamun"]
ISSUES = {                                       # issue label -> ways customers say it
    "late":    ["came {m} minutes late", "was very late", "took forever to arrive"],
    "cold":    ["was cold", "arrived cold", "was not hot at all"],
    "spicy":   ["was way too spicy", "had too much chilli"],
    "missing": ["was missing from my order", "never came in the bag"],
    "small":   ["portion was too small", "quantity was very less"],
}
ASK_REFUND = ["I want my money back.", "Please refund me.", "Refund please."]
NO_REFUND = ["", "Fix this next time.", "Still ordering again."]
HAPPY = ["Loved the {dish}!", "The {dish} was amazing.", "Great {dish}, thank you."]


def make_example():
    dish = random.choice(DISHES)
    if random.random() < 0.2:                    # 1 in 5: a happy review
        review = random.choice(HAPPY).format(dish=dish)
        label = f"ISSUE: none | DISH: {dish} | REFUND: no"
    else:
        issue = random.choice(list(ISSUES))
        wants = random.random() < 0.5
        phrase = random.choice(ISSUES[issue]).format(m=random.choice([30, 40, 50, 90]))
        extra = random.choice(ASK_REFUND if wants else NO_REFUND)
        review = f"The {dish} {phrase}. {extra}".strip()
        label = f"ISSUE: {issue} | DISH: {dish} | REFUND: {'yes' if wants else 'no'}"
    return {"messages": [{"role": "system", "content": SYSTEM},
                         {"role": "user", "content": review},
                         {"role": "assistant", "content": label}]}


# 1. make examples, keep only unique reviews (duplicates teach nothing and leak into the test set)
examples, seen = [], set()
while len(examples) < 120:
    ex = make_example()
    review = ex["messages"][1]["content"]
    if review not in seen:
        seen.add(review)
        examples.append(ex)

# 2. split: the model trains on 100, we test on 20 it has NEVER seen
random.shuffle(examples)
train, test = examples[:100], examples[100:]

# 3. checks before training - a bad file wastes GPU time
LABEL = re.compile(r"^ISSUE: (none|late|cold|spicy|missing|small) \| DISH: .+ \| REFUND: (yes|no)$")
bad = [ex for ex in examples if not LABEL.match(ex["messages"][2]["content"])]
overlap = {e["messages"][1]["content"] for e in train} & {e["messages"][1]["content"] for e in test}
print("examples:", len(examples), "| train:", len(train), "| test:", len(test))
print("bad labels:", len(bad), "| train/test overlap:", len(overlap))

# 4. save as JSONL: one JSON object per line (the format training libraries expect)
for name, rows in [("c21_train.jsonl", train), ("c21_test.jsonl", test)]:
    (HERE / name).write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
print("saved: c21_train.jsonl, c21_test.jsonl")
print("example:", json.dumps(train[0]["messages"][1:], ensure_ascii=False))