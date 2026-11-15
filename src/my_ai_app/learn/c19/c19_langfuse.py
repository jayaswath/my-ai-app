import os

from dotenv import load_dotenv

load_dotenv()                                      # BEFORE the langfuse imports, so they find the keys

from langfuse import get_client, observe
from langfuse.openai import OpenAI                 # an OpenAI client that reports every call to Langfuse

for name in ("GROQ_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_BASE_URL"):
    if not os.environ.get(name):
        raise SystemExit(f"{name} is not set — put it in .env")

client = OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1")
MODEL = "openai/gpt-oss-120b"

STOCK = {"paneer": "0 kg, ran out at 2:10 pm", "chicken": "6 kg"}


@observe()                                         # a span: Langfuse records input, output, time
def get_stock(item):
    return f"{item}: {STOCK.get(item, 'not in the inventory')}"


@observe()                                         # the trace: everything inside is nested under it
def morning_check():
    facts = get_stock("paneer") + "; " + get_stock("chicken")
    response = client.chat.completions.create(     # a generation: model, tokens, time
        model=MODEL,
        messages=[{"role": "system", "content": "Write ONE short line for a restaurant owner. Use only the facts."},
                  {"role": "user", "content": facts}],
    )
    return response.choices[0].message.content


print(morning_check())
get_client().flush()                               # send everything before the program ends
print("done: open Langfuse -> Tracing")