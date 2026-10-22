import random
import time


class RateLimited(Exception):
    pass


def flaky_call(n: int) -> str:
    if random.random() < 0.6:
        raise RateLimited("429 Too Many Requests")
    return f"digest #{n} ready"


def call_with_retry(n: int, max_tries: int = 4) -> str:
    for attempt in range(1, max_tries + 1):
        try:
            return flaky_call(n)
        except RateLimited as e:
            if attempt == max_tries:
                raise
            wait = 0.5 * 2 ** (attempt - 1)
            print(f"  attempt {attempt} failed ({e}), waiting {wait}s")
            time.sleep(wait)


random.seed(12)
for n in range(1, 4):
    try:
        print(call_with_retry(n))
    except RateLimited:
        print(f"digest #{n} FAILED after all retries - send later")