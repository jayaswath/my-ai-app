import psycopg
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer

DB_URL = "postgresql://postgres:learn@localhost:5456/postgres"
model = SentenceTransformer("all-MiniLM-L6-v2")
conn = psycopg.connect(DB_URL)
register_vector(conn)

tests = [
    ("how many paid leave days per year", 2),
    ("what to do with an oil fire", 2),
    ("cash float at opening", 1),
    ("can I use my phone while cooking", 1),
    ("customer found a hair in the food", 2),
    ("what to do before leaving at night", 3),
]


def search_pages(question, k=3):
    q_vector = model.encode(question, normalize_embeddings=True)
    rows = conn.execute(
        "SELECT page FROM doc_chunks ORDER BY embedding <=> %s LIMIT %s",
        (q_vector, k),
    ).fetchall()
    return [row[0] for row in rows]


hits_at_1 = 0
hits_at_3 = 0
reciprocal_ranks = 0
for question, expected_page in tests:
    pages = search_pages(question)
    if pages[0] == expected_page:
        hits_at_1 += 1
    if expected_page in pages:
        hits_at_3 += 1
        reciprocal_ranks += 1 / (pages.index(expected_page) + 1)
    print(f"expected p.{expected_page}  got {pages}  {question}")

n = len(tests)
print(f"\nhit@1: {hits_at_1}/{n}   hit@3: {hits_at_3}/{n}   MRR: {reciprocal_ranks / n:.2f}")
conn.close()