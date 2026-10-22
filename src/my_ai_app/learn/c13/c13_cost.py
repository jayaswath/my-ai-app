PRICE_IN = 12.67     # Rs per 1M input tokens   (Groq pricing page, 19 Oct 2026)
PRICE_OUT = 50.70    # Rs per 1M output tokens

def cost_rs(tokens_in: int, tokens_out: int) -> float:
    return tokens_in / 1_000_000 * PRICE_IN + tokens_out / 1_000_000 * PRICE_OUT

print(f"your item-5 call:      Rs {cost_rs(100, 119):.4f}")

digest_in, digest_out = 3_000, 600
per_digest = cost_rs(digest_in, digest_out)
print(f"one digest:            Rs {per_digest:.4f}")
print(f"100 kitchens, 30 days: Rs {per_digest * 30 * 100:.2f} per month")

kannada = cost_rs(digest_in, int(digest_out * 1.8))
print(f"same, in Kannada:      Rs {kannada * 30 * 100:.2f} per month")