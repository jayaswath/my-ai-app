import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

PROVIDERS = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "key_env": "GROQ_API_KEY",
        "model": "openai/gpt-oss-120b",
    },
}


def ask(provider: str, question: str) -> str:
    cfg = PROVIDERS[provider]
    api_key = os.environ.get(cfg["key_env"])
    if not api_key:
        raise SystemExit(f"{cfg['key_env']} missing - put it in .env")
    client = OpenAI(api_key=api_key, base_url=cfg["base_url"])
    resp = client.chat.completions.create(
        model=cfg["model"],
        messages=[{"role": "user", "content": question}],
    )
    return resp.choices[0].message.content


if __name__ == "__main__":
    print(ask("groq", "Name one South Indian breakfast dish. One word."))