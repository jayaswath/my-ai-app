from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

docs = [
    "If the rider is late, call the rider and inform the customer.",
    "Store paneer in the fridge below 4 degrees.",
    "Clean the tandoor every night after closing.",
    "Refund the customer if the order is missing items.",
]

vec = TfidfVectorizer()
doc_vectors = vec.fit_transform(docs)

questions = [
    "what to do when the rider is late",
    "how to keep cottage cheese fresh",
]
for question in questions:
    q_vector = vec.transform([question])
    scores = cosine_similarity(q_vector, doc_vectors)[0]
    print("Q:", question)
    for score, doc in sorted(zip(scores, docs), reverse=True):
        print(f"   {score:.2f}  {doc}")