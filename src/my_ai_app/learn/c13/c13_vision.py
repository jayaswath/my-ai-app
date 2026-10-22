import base64
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise SystemExit("GEMINI_API_KEY missing - put it in .env")
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

image_path = Path("data") / "sample_bill.jpg"
image_bytes = image_path.read_bytes()
image_b64 = base64.b64encode(image_bytes).decode("utf-8")

resp = client.chat.completions.create(
    model="gemini-3.8-flash",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Read this supplier bill. List every item with qty, unit, rate and amount. Plain text."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
            ],
        }
    ],
)
print(resp.choices[0].message.content)
print("tokens in:", resp.usage.prompt_tokens, "| out:", resp.usage.completion_tokens)