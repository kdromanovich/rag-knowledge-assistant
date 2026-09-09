# RAG Knowledge Assistant

[Русская версия](README_RU.md)

A production-style Retrieval-Augmented Generation API built with **Python, FastAPI, PostgreSQL, pgvector, Redis and OpenAI**. It ingests documents, creates embeddings, retrieves semantically relevant chunks and generates grounded answers with explicit source references.

## Why this project exists

This repository demonstrates an AI backend beyond low-code workflow orchestration: async API development, relational persistence, vector search, document ingestion, caching, authentication, containerization, testing and CI.

## Architecture

```mermaid
flowchart LR
    U[Client] --> API[FastAPI]
    API --> ING[Document ingestion]
    ING --> CH[Chunking]
    CH --> EMB[OpenAI embeddings]
    EMB --> PG[(PostgreSQL + pgvector)]
    U --> Q[Question]
    Q --> API
    API --> R[(Redis cache)]
    API --> RET[Vector retrieval]
    RET --> PG
    RET --> LLM[OpenAI Responses API]
    LLM --> A[Grounded answer + S1/S2 citations]
```

## Features

- `POST /v1/documents` for PDF, TXT and Markdown ingestion;
- configurable overlapping chunking;
- OpenAI embeddings;
- cosine similarity retrieval in pgvector;
- grounded generation with `[S1]`, `[S2]` source markers;
- PostgreSQL persistence with SQLAlchemy 2 async ORM;
- Redis response cache;
- API-key authentication;
- file-size validation and explicit format handling;
- Docker Compose environment;
- pytest, Ruff and GitHub Actions CI.

## Quick start

```bash
cp .env.example .env
# Put OPENAI_API_KEY into .env
docker compose up --build
```

Open `http://localhost:8000/docs`.

### Ingest a document

```bash
curl -X POST http://localhost:8000/v1/documents \
  -H 'x-api-key: change-me' \
  -F 'file=@./example.pdf'
```

### Ask a question

```bash
curl -X POST http://localhost:8000/v1/chat \
  -H 'content-type: application/json' \
  -H 'x-api-key: change-me' \
  -d '{"question":"What does the document say about the launch plan?"}'
```

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Database/Redis health |
| POST | `/v1/documents` | Ingest and embed a document |
| POST | `/v1/chat` | Retrieve context and answer with sources |

## Repository structure

```text
app/                  FastAPI application and RAG services
tests/                unit tests
.github/workflows/    CI
Dockerfile             application image
docker-compose.yml     API + PostgreSQL/pgvector + Redis
```

## Production notes

This is a portfolio-grade reference implementation. For a public production deployment, add migrations (Alembic), object storage, tenant isolation, document ACL filtering, background ingestion for large files, request tracing and an API gateway/WAF.

## License

MIT
