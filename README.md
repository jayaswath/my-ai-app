# my-ai-app: Hands-on Generative AI Engineering

![CI](https://github.com/jayaswath/my-ai-app/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11-blue)

Runnable Generative AI builds covering **RAG, AI agents, MCP, LLM evaluation, guardrails and a GPT built from scratch**, on top of a production Python base (FastAPI, PostgreSQL, Docker, CI).

All the examples use one real domain: a **cloud kitchen**. The data is orders, stock, bills, customer reviews and a staff handbook. This is the same domain as [KitchenOS](https://www.kitchenos.online), a live SaaS product I build and run, where these skills ship as AI features.

**Author:** Vijay Kumar A, Generative AI Engineer  ·  [KitchenOS showcase](https://github.com/jayaswath/kitchenos-showcase)

---

## Featured builds

Start here if you have 2 minutes.

| Build | What it does | Code |
|---|---|---|
| **Mini-GPT from scratch** | A character-level transformer (attention, embeddings, training loop) written in PyTorch and trained on 1,500 generated kitchen order tickets | [`c12_minigpt.py`](src/my_ai_app/learn/c12/c12_minigpt.py), [`c12_train.py`](src/my_ai_app/learn/c12/c12_train.py), [`c12_generate.py`](src/my_ai_app/learn/c12/c12_generate.py) |
| **RAG on PostgreSQL + pgvector** | Chunks a restaurant staff-handbook PDF, embeds it with sentence-transformers, stores it in pgvector and answers questions with an LLM. Includes a retrieval evaluation set | [`c14_ingest_pdf.py`](src/my_ai_app/learn/c14/c14_ingest_pdf.py), [`c14_rag_answer.py`](src/my_ai_app/learn/c14/c14_rag_answer.py), [`c14_eval_retrieval.py`](src/my_ai_app/learn/c14/c14_eval_retrieval.py) |
| **Agentic RAG with LangGraph** | An agent that decides when to search the vector store and when it has enough to answer | [`c16_lg_agentic_rag.py`](src/my_ai_app/learn/c16/c16_lg_agentic_rag.py) |
| **Human-in-the-loop agent** | A LangGraph agent that drafts a stock order, pauses for the owner's approval, saves its state to SQLite and resumes later | [`c16_lg_approval.py`](src/my_ai_app/learn/c16/c16_lg_approval.py), [`c16_lg_resume.py`](src/my_ai_app/learn/c16/c16_lg_resume.py) |
| **MCP server** | A "kitchen" MCP server that exposes stock and sales tools, used by Claude Desktop, a LangGraph agent and the OpenAI Agents SDK | [`c17_kitchen_server.py`](src/my_ai_app/learn/c17/c17_kitchen_server.py), [`c17_langgraph_mcp.py`](src/my_ai_app/learn/c17/c17_langgraph_mcp.py) |
| **LLM evaluation and regression gate** | An LLM-as-judge grades an agent's daily digest against a rubric. A regression check compares each run with a saved baseline and blocks the release if any test breaks. Traced with Langfuse | [`c19_judge.py`](src/my_ai_app/learn/c19/c19_judge.py), [`c19_regression.py`](src/my_ai_app/learn/c19/c19_regression.py), [`c19_langfuse.py`](src/my_ai_app/learn/c19/c19_langfuse.py) |
| **Guardrails** | Direct and indirect prompt-injection attacks on a review reader, then three defences: Prompt Guard classification, strict output schemas with Pydantic, and PII masking (phone, email, UPI, PAN, Aadhaar) | [`c20_injection.py`](src/my_ai_app/learn/c20/c20_injection.py), [`c20_defence.py`](src/my_ai_app/learn/c20/c20_defence.py), [`c20_pii.py`](src/my_ai_app/learn/c20/c20_pii.py) |
| **Vision: bill reader** | Reads a supplier bill photo with a vision LLM into validated structured data | [`c13_vision_bill.py`](src/my_ai_app/learn/c13/c13_vision_bill.py) |
| **Fine-tuning dataset** | Builds and checks a train/test JSONL dataset for fine-tuning a review-to-ticket model | [`c21_dataset.py`](src/my_ai_app/learn/c21/c21_dataset.py) |

---

## Full coverage

| Stage | Topics |
|---|---|
| **Production Python** | uv, Git, type hints (mypy strict), pytest, async, FastAPI, Docker, GitHub Actions CI |
| **Data layer** | PostgreSQL, SQLAlchemy, Alembic migrations, pandas, Polars, APScheduler, ETL pipeline |
| **Statistics** | Distributions, probability, hypothesis testing, A/B testing, regression |
| **Machine learning** | scikit-learn Pipelines, classification metrics, cross-validation, data leakage, GridSearchCV, decision trees, random forest, XGBoost, experiment tracking, model save/load and serving |
| **Deep learning** | PyTorch tensors, autograd, training loops, `nn.Linear`, CNNs, transfer learning |
| **LLM internals** | Tokens, embeddings, attention, the transformer, sampling temperature |
| **LLM APIs** | Chat, streaming, structured JSON output, validation and re-asking, retries (tenacity), async and rate limiting, caching, token cost tracking, vision, multiple providers |
| **RAG** | Chunking strategies, embeddings, cosine similarity, TF-IDF vs dense search, pgvector, LangChain and LlamaIndex RAG, retrieval evaluation |
| **Tools and function calling** | Tool schemas, the tool loop, parallel calls, error handling, idempotent and safe tools |
| **AI agents** | Agent loop, short- and long-term memory, scheduling, stop conditions, human approval gates, LangGraph state/edges/checkpoints, Microsoft Agent Framework |
| **MCP** | Servers, tools and resources over stdio and HTTP, clients, and use from LangGraph and the OpenAI Agents SDK |
| **Evaluation and observability** | Rule-based evals, LLM-as-judge, agent evals, cost and latency tracking, regression testing, structured logging, tracing with Langfuse |
| **Safety** | Prompt injection, guard models, output validation, PII redaction |
| **Fine-tuning** | Dataset design, generation and validation |

---

## Tech stack

| Area | Tools |
|---|---|
| **Language and tooling** | Python 3.11, uv, pytest, ruff, mypy, Git, GitHub Actions |
| **Backend** | FastAPI, Uvicorn, SQLAlchemy, Alembic, Pydantic |
| **Data** | PostgreSQL, pgvector, pandas, Polars |
| **ML and DL** | scikit-learn, XGBoost, PyTorch, sentence-transformers |
| **LLMs** | OpenAI-compatible APIs, Groq, Gemini |
| **GenAI frameworks** | LangChain, LangGraph, LlamaIndex, Microsoft Agent Framework, OpenAI Agents SDK, Model Context Protocol |
| **Evaluation** | Langfuse |
| **Infrastructure** | Docker |

---

## Repository structure

```
my-ai-app/
├── src/my_ai_app/
│   ├── api.py, models.py, crud.py …   # FastAPI app + SQLAlchemy data layer
│   ├── pipeline.py, scheduler.py …    # ETL pipeline on a schedule
│   └── learn/
│       ├── w2 … w7/                   # Data, statistics, ML, model serving
│       ├── c9, c10/                   # PyTorch, CNNs
│       ├── c12/                       # Mini-GPT from scratch
│       ├── c13/                       # LLM APIs, structured output, vision
│       ├── c14/                       # RAG + pgvector
│       ├── c15, c16/                  # Tools, agents, LangGraph
│       ├── c17/                       # MCP
│       ├── c19/                       # Evals + observability
│       ├── c20/                       # Guardrails
│       └── c21/                       # Fine-tuning data
├── alembic/                           # Database migrations
├── tests/
├── Dockerfile
└── .github/workflows/ci.yml
```

---

## Running locally

**Requirements:** Python 3.11, [uv](https://github.com/astral-sh/uv), Docker

```bash
# 1. Install dependencies
uv sync

# 2. Start PostgreSQL (and pgvector for the RAG builds) in Docker

# 3. Run the API
uv run uvicorn my_ai_app.api:app --port 8001 --reload

# 4. Run the tests
uv run pytest

# Run any build, e.g. the PII masker (offline, no API key)
uv run python src/my_ai_app/learn/c20/c20_pii.py
```

API keys (`GROQ_API_KEY`, `GEMINI_API_KEY`, …) go in a local `.env` file, which is never committed.

---

## Contact

**Vijay Kumar A**, Generative AI Engineer
📧 vijaykumar07kolar@gmail.com  ·  🌐 [kitchenos.online](https://www.kitchenos.online)
