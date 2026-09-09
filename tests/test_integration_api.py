from fastapi.testclient import TestClient

import app.service as rag_service
from app.main import app


def _vector(seed: int = 0) -> list[float]:
    vector = [0.0] * 1536
    vector[seed % 1536] = 1.0
    return vector


async def fake_embed_texts(texts: list[str]) -> list[list[float]]:
    return [_vector(0) for _ in texts]


async def fake_answer_with_context(question: str, context: str) -> str:
    assert question
    assert "S1" in context
    return "The answer is grounded in the indexed document [S1]."


def test_rag_api_round_trip_with_postgres_pgvector_and_redis(monkeypatch):
    monkeypatch.setattr(rag_service, "embed_texts", fake_embed_texts)
    monkeypatch.setattr(rag_service, "answer_with_context", fake_answer_with_context)

    headers = {"x-api-key": "test-key"}
    document_text = (
        "The launch plan starts with a controlled pilot. "
        "The pilot validates demand, operations, and support before scaling."
    )

    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["database"] == "ok"
        assert health.json()["redis"] == "ok"

        unauthorized = client.post(
            "/v1/chat",
            json={"question": "What is the launch plan?"},
        )
        assert unauthorized.status_code in {401, 403}

        ingest = client.post(
            "/v1/documents",
            headers=headers,
            files={"file": ("launch-plan.txt", document_text.encode(), "text/plain")},
        )
        assert ingest.status_code == 200, ingest.text
        ingest_body = ingest.json()
        assert ingest_body["filename"] == "launch-plan.txt"
        assert ingest_body["chunks_created"] >= 1

        first = client.post(
            "/v1/chat",
            headers=headers,
            json={"question": "What is the launch plan?", "top_k": 3},
        )
        assert first.status_code == 200, first.text
        first_body = first.json()
        assert first_body["cached"] is False
        assert first_body["sources"]
        assert first_body["sources"][0]["filename"] == "launch-plan.txt"
        assert "[S1]" in first_body["answer"]

        second = client.post(
            "/v1/chat",
            headers=headers,
            json={"question": "What is the launch plan?", "top_k": 3},
        )
        assert second.status_code == 200
        assert second.json()["cached"] is True
