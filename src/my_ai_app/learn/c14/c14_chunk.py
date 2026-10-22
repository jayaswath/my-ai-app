sop = (
    "Paneer must be stored in the fridge below 4 degrees. "
    "Use it within three days of delivery. "
    "If it smells sour or feels slimy, throw it away and log it as wastage. "
    "Never refreeze paneer after it has been thawed."
)


def chunk_words(text, size=12, overlap=3):
    words = text.split()
    chunks = []
    step = size - overlap
    for start in range(0, len(words), step):
        piece = words[start:start + size]
        chunks.append(" ".join(piece))
        if start + size >= len(words):
            break
    return chunks


print("total words:", len(sop.split()))
for i, chunk in enumerate(chunk_words(sop)):
    print(f"[{i}] {chunk}")