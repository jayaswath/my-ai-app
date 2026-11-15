from pathlib import Path

import psycopg
from pgvector.psycopg import register_vector
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

from c14_chunk_sentences import chunk_sentences

DB_URL = "postgresql://postgres:learn@localhost:5456/postgres"
pdf_path = Path("data") / "staff_handbook.pdf"

model = SentenceTransformer("all-MiniLM-L6-v2")
conn = psycopg.connect(DB_URL, autocommit=True)
conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
register_vector(conn)

conn.execute("""
    CREATE TABLE IF NOT EXISTS doc_chunks (
        id        bigserial PRIMARY KEY,
        source    text,
        page      int,
        content   text,
        embedding vector(384)
    )
""")
conn.execute("DELETE FROM doc_chunks WHERE source = %s", (pdf_path.name,))

reader = PdfReader(pdf_path)
count = 0
for page_number, page in enumerate(reader.pages, start=1):
    page_text = page.extract_text().replace("\n", " ")
    for chunk in chunk_sentences(page_text, max_words=60):
        vector = model.encode(chunk, normalize_embeddings=True)
        conn.execute(
            "INSERT INTO doc_chunks (source, page, content, embedding) VALUES (%s, %s, %s, %s)",
            (pdf_path.name, page_number, chunk, vector),
        )
        count += 1

print(f"{pdf_path.name}: {len(reader.pages)} pages -> {count} chunks stored")
conn.close()