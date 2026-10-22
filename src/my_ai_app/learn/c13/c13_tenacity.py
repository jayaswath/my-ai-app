import random

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


class RateLimited(Exception):
    pass


@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=0.5),
    retry=retry_if_exception_type(RateLimited),
    reraise=True,
)
def flaky_call(n: int) -> str:
    if random.random() < 0.6:
        print(f"  digest #{n}: busy")
        raise RateLimited("429 Too Many Requests")
    return f"digest #{n} ready"


random.seed(12)
for n in range(1, 4):
    try:
        print(flaky_call(n))
    except RateLimited:
        print(f"digest #{n} FAILED after all retries - send later")