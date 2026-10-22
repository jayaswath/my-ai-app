import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

docs = [
    "If the rider is late, call the rider and inform the customer.",
    "Store paneer in the fridge below 4 degrees.",
    "Clean the tandoor every night after closing.",
    "Refund the customer if the order is missing items.",
    "Keep raw chicken on the bottom shelf of the cold room.",
    "Check the gas cylinder level every morning before cooking.",
]
doc_vectors = model.encode(docs)


def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def search(question, k=2):
    q_vector = model.encode(question)
    scored = []
    for doc, vec in zip(docs, doc_vectors):
        scored.append((cosine(q_vector, vec), doc))
    scored.sort(reverse=True)
    return scored[:k]


for question in ["how to keep cottage cheese fresh", "delivery boy has not come yet"]:
    print("Q:", question)
    for score, doc in search(question):
        print(f"   {score:.2f}  {doc}")