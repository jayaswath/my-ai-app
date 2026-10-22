import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise SystemExit("GROQ_API_KEY missing - put it in .env")

client = Groq(api_key=api_key)

resp = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {"role": "system", "content": "You are a cloud-kitchen assistant. Answer in one short sentence."},
        {"role": "user", "content": "Suggest one add-on to sell with Chicken Biryani."},
    ],
    temperature=0.2,
    max_tokens=1000,
)

print(resp.choices[0].message.content)
print(resp.choices[0].finish_reason)
print(resp.usage.prompt_tokens, resp.usage.completion_tokens, resp.usage.total_tokens)
print(resp.model)
