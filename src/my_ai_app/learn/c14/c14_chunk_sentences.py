import re

sop = (
    "Paneer must be stored in the fridge below 4 degrees. "
    "Use it within three days of delivery. "
    "If it smells sour or feels slimy, throw it away and log it as wastage. "
    "Never refreeze paneer after it has been thawed."
)


def chunk_sentences(text, max_words=20):
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    current = []
    count = 0
    for sentence in sentences:
        n = len(sentence.split())
        if current and count + n > max_words:
            chunks.append(" ".join(current))
            current = []
            count = 0
        current.append(sentence)
        count += n
    if current:
        chunks.append(" ".join(current))
    return chunks


for i, chunk in enumerate(chunk_sentences(sop)):
    print(f"[{i}] ({len(chunk.split())} words) {chunk}")