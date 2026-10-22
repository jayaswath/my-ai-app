from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

docs = [
    "If the rider is late, call the rider and inform the customer.",
    "Store paneer in the fridge below 4 degrees.",
    "Clean the tandoor every night after closing.",
    "Refund the customer if the order is missing items.",
]

doc_vectors = model.encode(docs)
print("doc_vectors shape:", doc_vectors.shape)
print("first 5 numbers of doc 2:", doc_vectors[1][:5])

question = "how to keep cottage cheese fresh"
q_vector = model.encode(question)
print("question shape:", q_vector.shape)

scores = model.similarity(q_vector, doc_vectors)[0]
for score, doc in sorted(zip(scores.tolist(), docs), reverse=True):
    print(f"   {score:.2f}  {doc}")