import numpy as np

biryani = np.array([9, 1])        # [spicy, sweet]
pulao = np.array([6, 1])
gulab_jamun = np.array([0, 9])
big_biryani = np.array([18, 2])   # same taste, double portion


def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


print("biryani vs pulao:      ", round(cosine(biryani, pulao), 3))
print("biryani vs gulab jamun:", round(cosine(biryani, gulab_jamun), 3))
print("biryani vs big biryani:", round(cosine(biryani, big_biryani), 3))