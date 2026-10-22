import psycopg
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer

from c14_chunk_headings import chunk_by_heading, text

DB_URL = "postgresql://postgres:learn@localhost:5456/postgres"

model = SentenceTransformer("all-MiniLM-L6-v2")
chunks = chunk_by_heading(text, "kitchen_sop.md")

conn = psycopg.connect(DB_URL, autocommit=True)
conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
register_vector(conn)

conn.execute("DROP TABLE IF EXISTS sop_chunks")
conn.execute("""
    CREATE TABLE sop_chunks (
        id        bigserial PRIMARY KEY,
        source    text,
        heading   text,
        content   text,
        embedding vector(384)
    )
""")

for c in chunks:
    vector = model.encode(f"{c['heading']}: {c['text']}", normalize_embeddings=True)
    conn.execute(
        "INSERT INTO sop_chunks (source, heading, content, embedding) VALUES (%s, %s, %s, %s)",
        (c["source"], c["heading"], c["text"], vector),
    )

count = conn.execute("SELECT count(*) FROM sop_chunks").fetchone()[0]
print("rows stored:", count)
conn.close()