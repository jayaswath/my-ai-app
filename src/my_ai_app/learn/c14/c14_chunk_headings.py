from pathlib import Path

text = (Path("data") / "kitchen_sop.md").read_text(encoding="utf-8")


def chunk_by_heading(text, source):
    chunks = []
    heading = "Intro"
    lines = []
    for line in text.splitlines():
        if line.startswith("#"):
            if lines:
                chunks.append({"source": source, "heading": heading, "text": " ".join(lines)})
            heading = line.lstrip("#").strip()
            lines = []
        elif line.strip():
            lines.append(line.strip())
    if lines:
        chunks.append({"source": source, "heading": heading, "text": " ".join(lines)})
    return chunks


if __name__ == "__main__":
    chunks = chunk_by_heading(text, "kitchen_sop.md")
    print("chunks:", len(chunks))
    for c in chunks:
        print(f"- [{c['heading']}] {c['text'][:55]}...")
    print()
    print(chunks[0])