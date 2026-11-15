from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

inventory = [
    "Onions (Red)",
    "Tomatoes",
    "Paneer (Fresh)",
    "Full Cream Milk",
    "Coriander Leaves",
    "Green Chillies",
    "Basmati Rice",
    "Refined Oil",
]
bill_items = ["Onion Big", "Tomato", "Paneer", "Milk", "Coriander", "Green Chilli", "Cumin Seeds"]

THRESHOLD = 0.5

inventory_vectors = model.encode(inventory, normalize_embeddings=True)

for name in bill_items:
    q_vector = model.encode(name, normalize_embeddings=True)
    scores = inventory_vectors @ q_vector
    best = scores.argmax()
    score = scores[best]
    if score >= THRESHOLD:
        print(f"{name} -> {inventory[best]} ({score:.2f})")
    else:
        print(f"{name} -> NO MATCH, ask the owner (closest: {inventory[best]} {score:.2f})")