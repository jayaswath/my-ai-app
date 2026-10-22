"""
c12_attention.py  —  scaled dot-product attention, by hand.
Chapter 12, item 5.
"""
import numpy as np

np.set_printoptions(precision=3, suppress=True)

WORDS = ["the", "biryani", "the", "customer", "ordered", "was", "cold"]

# 4 made-up dimensions, so we can read the vectors:
#   dim 0 = is a concrete thing
#   dim 1 = is a person
#   dim 2 = is a property / adjective
#   dim 3 = is a verb or function word
E = np.array([
    [0.0, 0.0, 0.0, 2.0],   # the
    [2.0, 0.0, 0.2, 0.0],   # biryani
    [0.0, 0.0, 0.0, 2.0],   # the
    [0.2, 2.0, 0.0, 0.0],   # customer
    [0.0, 0.2, 0.0, 2.0],   # ordered
    [0.0, 0.0, 0.2, 2.0],   # was
    [0.0, 0.0, 2.0, 0.2],   # cold
])

print(f"{len(WORDS)} words, each a vector of {E.shape[1]} numbers")
print("shape:", E.shape)
for w, v in zip(WORDS, E):
    print(f"  {w:<9} {v}")


# ══════════════════════════════════════════════════
#  SEGMENT 2  —  attention using the raw embeddings
# ══════════════════════════════════════════════════

def softmax(x):
    e = np.exp(x - x.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)

d = E.shape[1]

scores_raw  = E @ E.T / np.sqrt(d)
weights_raw = softmax(scores_raw)

print("\n--- NO PROJECTION: Q = K = the raw embedding ---")
print("what 'cold' pays attention to:")
for w, a in zip(WORDS, weights_raw[6]):
    print(f"  {w:<9} {a:.3f}")
print(f"  {'TOTAL':<9} {weights_raw[6].sum():.3f}")

# ══════════════════════════════════════════════════
#  SEGMENT 3  —  give each word a QUESTION to ask
# ══════════════════════════════════════════════════

#        what the question points at:
#        thing person property verb
W_Q = np.array([
    [0.0,  0.0,  0.0,  1.0],   # if I'm a THING    -> look for verbs
    [0.0,  0.0,  0.0,  1.0],   # if I'm a PERSON   -> look for verbs
    [1.0,  0.0,  0.0,  0.0],   # if I'm a PROPERTY -> look for things
    [0.3,  0.0,  0.0,  0.0],   # if I'm a VERB     -> weakly, subjects
])

Q = E @ W_Q      # what each word is LOOKING FOR
K = E            # what each word ADVERTISES  (kept simple)
V = E            # what each word HANDS OVER  (kept simple)

print("\n'cold' meaning  :", E[6])
print("'cold' question :", Q[6])

scores  = Q @ K.T / np.sqrt(d)
weights = softmax(scores)

print("\n--- WITH W_Q: what 'cold' pays attention to ---")
for w, s, a in zip(WORDS, scores[6], weights[6]):
    print(f"  {w:<9}  score {s:6.3f}   weight {a:.3f}")
print(f"  {'TOTAL':<9}  {'':12}   weight {weights[6].sum():.3f}")

# ══════════════════════════════════════════════════
#  SEGMENT 4  —  the blend
# ══════════════════════════════════════════════════

output = weights @ V

def cos(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))

print("\n--- THE BLEND ---")
print("cold BEFORE attention :", E[6])
print("cold AFTER  attention :", output[6])
print("biryani               :", E[1])
print()
print(f"cos(cold BEFORE, biryani) : {cos(E[6], E[1]):.4f}")
print(f"cos(cold AFTER,  biryani) : {cos(output[6], E[1]):.4f}")

# ══════════════════════════════════════════════════
#  SEGMENT 5  —  causal mask: no peeking at the future
# ══════════════════════════════════════════════════

n = len(WORDS)
mask = np.triu(np.ones((n, n)), k=1)      # 1 = future (hidden)

print("\nthe mask (1 = future, hidden):")
print(mask.astype(int))

masked_scores  = np.where(mask == 1, -np.inf, scores)
masked_weights = softmax(masked_scores)

print("\nwho each word may look at (rows = the word looking):")
print("           " + "  ".join(f"{w[:4]:>5}" for w in WORDS))
for w, row in zip(WORDS, masked_weights):
    print(f"  {w:<9}" + "  ".join(f"{x:5.2f}" for x in row))


# ══════════════════════════════════════════════════
#  SEGMENT 6  —  attention cannot see order
# ══════════════════════════════════════════════════

rev   = E[::-1]                                         # same words, reversed
out_r = softmax((rev @ W_Q) @ rev.T / np.sqrt(d)) @ rev

print("\ncold, normal order  :", output[6])
print("cold, reversed order:", out_r[0])                # cold is now first


# ══════════════════════════════════════════════════
#  SEGMENT 7  —  add position stamps, then reverse again
# ══════════════════════════════════════════════════

def positional_encoding(n_positions, d):
    P = np.zeros((n_positions, d))
    for pos in range(n_positions):
        for i in range(0, d, 2):
            angle = pos / (10000 ** (i / d))
            P[pos, i]     = np.sin(angle)
            P[pos, i + 1] = np.cos(angle)
    return P

def attend(X):
    return softmax((X @ W_Q) @ X.T / np.sqrt(d)) @ X

P = positional_encoding(len(WORDS), d)

out_normal = attend(E + P)          # words in order, stamps 0..6
out_rev    = attend(E[::-1] + P)    # words reversed, stamps STILL 0..6

print("\nWITH position stamps:")
print("cold, normal order  :", out_normal[6])
print("cold, reversed order:", out_rev[0])