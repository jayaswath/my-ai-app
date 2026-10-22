import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise SystemExit("GROQ_API_KEY missing - put it in .env")
client = Groq(api_key=api_key)

MODEL = "openai/gpt-oss-120b"

def prompt_tokens(text: str) -> int:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": text}],
        max_tokens=50,
    )
    return resp.usage.prompt_tokens

SENTENCES = {
    "English": "Yesterday you sold 142 chicken biryanis, 18% fewer than last Friday.",
    "Hindi": "कल आपने 142 चिकन बिरयानी बेचीं, जो पिछले शुक्रवार से 18% कम है।",
    "Kannada": "ನಿನ್ನೆ ನೀವು 142 ಚಿಕನ್ ಬಿರಿಯಾನಿ ಮಾರಾಟ ಮಾಡಿದ್ದೀರಿ, ಇದು ಕಳೆದ ಶುಕ್ರವಾರಕ್ಕಿಂತ 18% ಕಡಿಮೆ.",
}

baseline = prompt_tokens(".")
print(f"wrapping only: {baseline} tokens\n")

counts = {lang: prompt_tokens(text) - baseline for lang, text in SENTENCES.items()}
for lang, n in counts.items():
    print(f"{lang:8} {n:3} tokens   x{n / counts['English']:.1f} vs English")