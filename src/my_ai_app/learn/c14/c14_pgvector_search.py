import psycopg
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer

DB_URL = "postgresql://postgres:learn@localhost:5456/postgres"

model = SentenceTransformer("all-MiniLM-L6-v2")
conn = psycopg.connect(DB_URL)
register_vector(conn)


def search(question, k=2):
    q_vector = model.encode(question, normalize_embeddings=True)
    return conn.execute(
        """
        SELECT heading, content, 1 - (embedding <=> %s) AS score
        FROM sop_chunks
        ORDER BY embedding <=> %s
        LIMIT %s
        """,
        (q_vector, q_vector, k),
    ).fetchall()


for question in ["how to keep cottage cheese fresh", "delivery boy has not come yet", "I can smell gas"]:
    print("Q:", question)
    for heading, content, score in search(question):
        print(f"   {score:.2f}  [{heading}] {content[:45]}...")

conn.close()