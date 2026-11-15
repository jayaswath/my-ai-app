# c20_pii.py  -  ch.20 item 5: hide personal data BEFORE text goes to an AI model or into logs.
# Plain code, no AI, runs offline.
# Run from my-ai-app:  uv run python src/my_ai_app/learn/c20/c20_pii.py
import re

PATTERNS = [                                                   # order matters: email before UPI
    ("EMAIL",   r"[\w.+-]+@[\w-]+\.[\w.]+"),                   # ravi.k@gmail.com
    ("UPI",     r"\b[\w.-]+@[a-z]+\b"),                        # ravi@okaxis (no dot after @)
    ("PHONE",   r"(?:\+91[\s-]?)?\b[6-9]\d{4}\s?\d{5}\b"),      # +91 98450 12345 / 9845012345
    ("AADHAAR", r"\b\d{4}\s?\d{4}\s?\d{4}\b"),                 # 2345 6789 0123
    ("PAN",     r"\b[A-Z]{5}\d{4}[A-Z]\b"),                    # ABCDE1234F
]


def mask(text: str) -> str:
    for label, pattern in PATTERNS:
        text = re.sub(pattern, f"[{label}]", text)
    return text


note = ("Order 2041: 2 chicken biryani, total Rs 450. Customer Ravi, call +91 98450 12345 "
        "or 9845012345, mail ravi.k@gmail.com, paid by UPI ravi@okaxis. "
        "PAN ABCDE1234F, Aadhaar 2345 6789 0123.")

print("BEFORE:", note)
print("AFTER: ", mask(note))