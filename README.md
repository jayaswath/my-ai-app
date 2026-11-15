# my-ai-app — Hands-on Generative AI Engineering

A hands-on learning repository covering the full path to production Generative AI engineering: production Python, data pipelines, machine learning, deep learning, transformers from scratch, RAG, AI agents, multi-agent systems, Model Context Protocol (MCP) and LLM evaluation.

Every topic is built as small, runnable code: first from scratch to understand how it works, then with the framework used in industry.

**Author:** Vijay Kumar A, Generative AI Engineer  ·  **Real-world application:** [KitchenOS showcase](https://github.com/jayaswath/kitchenos-showcase), where these skills ship as AI agents in a live SaaS product

---

## What's inside

| Stage | Topics | Highlights |
|---|---|---|
| **Production Python** | uv, Git, type hints, pytest, async, FastAPI, Docker, CI | A small FastAPI app with tests and a CI pipeline |
| **Data layer** | PostgreSQL, SQLAlchemy, pandas, Polars, APScheduler | An ETL pipeline that runs on a schedule |
| **Statistics** | Distributions, Bayes, A/B testing, regression | The maths behind model evaluation |
| **Machine learning** | scikit-learn Pipelines, classification metrics, cross-validation, GridSearchCV, decision trees, random forest, XGBoost | Experiment tracking, model save/load, feature engineering |
| **Model serving** | FastAPI | An ML model served as a local API |
| **Deep learning** | PyTorch tensors, autograd, training loops, `nn.Linear`, CNNs, transfer learning | A computer-vision model trained end to end |
| **LLM internals** | Tokens, embeddings, attention, the transformer | **A mini-GPT built from scratch in PyTorch** |
| **Generative AI breadth** | Diffusion, GANs, CLIP, speech-to-text, text-to-speech, multimodal models | Concepts and where each is used |
| **LLM APIs** | Calling hosted LLMs, prompts, structured output | Working API clients in Python |
| **RAG** | Chunking, embeddings, vector search, pgvector, agentic RAG | A retrieval pipeline on PostgreSQL + pgvector |
| **Tools & function calling** | Tool schemas, letting an LLM call Python functions | An LLM that uses tools to answer questions |
| **AI agents** | Agent loop, memory, scheduling, human approval gates, LangGraph, multi-agent systems, Microsoft Agent Framework | Agents that plan, act and wait for approval before risky steps |
| **Model Context Protocol (MCP)** | MCP servers, tools and resources | An MCP server connected to Claude Desktop |
| **Evaluation & observability** | LLM evals, tracing, Langfuse | Tracing and scoring LLM responses with Langfuse |

---

## Tech stack

| Area | Tools |
|---|---|
| **Language & tooling** | Python 3.11, uv, pytest, Git, GitHub Actions |
| **Backend** | FastAPI, Uvicorn, SQLAlchemy |
| **Data** | PostgreSQL, pgvector, pandas, Polars |
| **ML & DL** | scikit-learn, XGBoost, PyTorch |
| **GenAI & agents** | LLM APIs, LangGraph, Microsoft Agent Framework, Model Context Protocol |
| **Evaluation** | Langfuse |
| **Infrastructure** | Docker |

---

## Repository structure

```
my-ai-app/
├── src/my_ai_app/
│   ├── ...              # FastAPI app and data-layer code
│   └── learn/
│       ├── w2 … w7/     # Weeks 2–7: data, statistics, ML, model serving
│       └── c9, c10 …/   # Chapters 9 onward: PyTorch, CNNs, transformers, RAG, agents, MCP, evals
├── tests/
└── pyproject.toml
```

---

## Running locally

**Requirements:** Python 3.11, [uv](https://github.com/astral-sh/uv), Docker

```bash
# 1. Install dependencies
uv sync

# 2. Start PostgreSQL (and pgvector for the RAG chapters) in Docker

# 3. Run the API
uv run uvicorn my_ai_app.main:app --port 8001 --reload

# 4. Run the tests
uv run pytest
```

API keys go in a local `.env` file, which is never committed.

---

## Contact

**Vijay Kumar A**, Generative AI Engineer
📧 vijaykumar07kolar@gmail.com  ·  🌐 [kitchenos.online](https://www.kitchenos.online)
