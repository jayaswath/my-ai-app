import os

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise SystemExit("GROQ_API_KEY missing - put it in .env")

# 1. load: one Document per page
reader = PdfReader("data/staff_handbook.pdf")
pages = [
    Document(page_content=page.extract_text(), metadata={"source": "staff_handbook.pdf", "page": number})
    for number, page in enumerate(reader.pages, start=1)
]

# 2. split into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
chunks = splitter.split_documents(pages)

# 3. embed + store in pgvector
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
store = PGVector(
    embeddings=embeddings,
    collection_name="handbook_langchain",
    connection="postgresql+psycopg://postgres:learn@localhost:5456/postgres",
    pre_delete_collection=True,
)
store.add_documents(chunks)
retriever = store.as_retriever(search_kwargs={"k": 3})
print(f"{len(pages)} pages -> {len(chunks)} chunks stored")

# 4. prompt + model
prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer ONLY from the extracts. If they do not contain the answer, reply exactly: "
               "I don't know - this is not in the handbook. Cite like [staff_handbook.pdf p.2]. "
               "Keep it to 2-3 short sentences, plain text."),
    ("user", "<extracts>\n{context}\n</extracts>\n\nQuestion: {question}"),
])
llm = ChatOpenAI(
    model="openai/gpt-oss-120b",
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1",
    temperature=0.2,
    reasoning_effort="low",
    max_tokens=400,
)


def format_docs(docs):
    return "\n\n".join(f"[{d.metadata['source']} p.{d.metadata['page']}]\n{d.page_content}" for d in docs)


# 5. the chain: question -> retrieve -> prompt -> LLM -> text
chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

for question in ["How many leave days do I get?", "What do I do if oil catches fire?", "Who is the CEO of Swiggy?"]:
    print("Q:", question)
    print("A:", chain.invoke(question))
    print()