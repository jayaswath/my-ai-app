from pathlib import Path

PROMPTS = Path("data") / "prompts"
VERSION = "v1"


def load_prompt(name: str, version: str = VERSION) -> str:
    return (PROMPTS / f"{name}_{version}.txt").read_text(encoding="utf-8")


def render(template: str, **values) -> str:
    return template.format(**values)


data = "orders: 312 (+8.7%)\nalert: Paneer Tikka -41.9%"

messages = [
    {"role": "system", "content": render(load_prompt("digest_system"), kitchen_name="Biryani Bros")},
    {"role": "user", "content": render(load_prompt("digest_user"), data=data)},
]

print(f"prompt version: {VERSION}\n")
for m in messages:
    print(f"[{m['role']}]\n{m['content']}")