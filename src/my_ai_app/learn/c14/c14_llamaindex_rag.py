import os

from dotenv import load_dotenv
from groq import Groq
from llama_index.core import Document, Settings, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from pypdf import PdfReader

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise SystemExit("GROQ_API_KEY missing - put it in .env")
client = Groq(api_key=api_key, timeout=20.0, max_retries=2)

# settings: which embedding model, how to chunk
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
Settings.node_parser = SentenceSplitter(chunk_size=128, chunk_overlap=20)

# 1. load: one Document per page
reader = PdfReader("data/staff_handbook.pdf")
documents = [
    Document(text=page.extract_text(), metadata={"source": "staff_handbook.pdf", "page": number})
    for number, page in enumerate(reader.pages, start=1)
]

# 2. chunk + embed + store, in one line (in memory)
index = VectorStoreIndex.from_documents(documents)
retriever = index.as_retriever(similarity_top_k=3)

SYSTEM = """Answer ONLY from the extracts. If they do not contain the answer, reply exactly:
I don't know - this is not in the handbook. (No citation on that reply.)
Otherwise cite like [staff_handbook.pdf p.2]. Keep it to 2-3 short sentences, plain text."""


def answer(question):
    nodes = retriever.retrieve(question)
    context = "\n\n".join(f"[{n.metadata['source']} p.{n.metadata['page']}]\n{n.text}" for n in nodes)
    resp = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"<extracts>\n{context}\n</extracts>\n\nQuestion: {question}"},
        ],
        reasoning_effort="low",
        max_tokens=400,
        temperature=0.2,
    )
    return resp.choices[0].message.content


for question in ["How many leave days do I get?", "What do I do if oil catches fire?", "Who is the CEO of Swiggy?"]:
    print("Q:", question)
    print("A:", answer(question))
    print()