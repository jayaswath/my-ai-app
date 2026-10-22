import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from groq import Groq

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise SystemExit("GROQ_API_KEY missing - put it in .env")
client = Groq(api_key=api_key)

app = FastAPI()


def groq_words(question):
    stream = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": question}],
        reasoning_effort="low",
        max_tokens=500,
        stream=True,
    )
    for chunk in stream:
        piece = chunk.choices[0].delta.content
        if piece:
            yield piece


@app.get("/chat")
def chat(q: str):
    return StreamingResponse(groq_words(q), media_type="text/plain")