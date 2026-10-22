import os
import time

from dotenv import load_dotenv
from groq import (APIConnectionError, APITimeoutError, BadRequestError, Groq,
                  InternalServerError, RateLimitError)

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise SystemExit("GROQ_API_KEY missing - put it in .env")

client = Groq(api_key=api_key, timeout=20.0, max_retries=0)

RETRYABLE = (RateLimitError, APITimeoutError, APIConnectionError, InternalServerError)


def ask(messages: list[dict], max_tries: int = 4) -> str:
    for attempt in range(1, max_tries + 1):
        try:
            resp = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=messages,
                max_tokens=1000,
            )
            choice = resp.choices[0]
            if choice.finish_reason == "length":
                raise ValueError("reply cut off - raise max_tokens or shorten the prompt")
            return choice.message.content
        except RETRYABLE as e:
            if attempt == max_tries:
                raise
            wait = 0.5 * 2 ** (attempt - 1)
            if isinstance(e, RateLimitError):
                retry_after = e.response.headers.get("retry-after")
                if retry_after:
                    wait = float(retry_after)
            print(f"  attempt {attempt}: {type(e).__name__}, waiting {wait}s")
            time.sleep(wait)


if __name__ == "__main__":
    try:
        print(ask([{"role": "user", "content": "One tip to reduce food waste in a cloud kitchen, in one sentence."}]))
    except BadRequestError as e:
        print("bad request - fix the code, don't retry:", e.status_code)
    except RETRYABLE as e:
        print("gave up after retries:", type(e).__name__)