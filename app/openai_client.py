from openai import AsyncOpenAI

from app.config import get_settings

settings = get_settings()
client = AsyncOpenAI(api_key=settings.openai_api_key or "missing-key")


async def embed_texts(texts: list[str]) -> list[list[float]]:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required for live embeddings")
    result = await client.embeddings.create(
        model=settings.openai_embedding_model,
        input=texts,
    )
    return [item.embedding for item in result.data]


async def answer_with_context(question: str, context: str) -> str:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required for live generation")
    response = await client.responses.create(
        model=settings.openai_chat_model,
        store=False,
        instructions=(
            "Answer only from the supplied context. Cite supporting chunks inline as "
            "[S1], [S2], etc. If the context does not support the answer, say that the "
            "knowledge base does not contain enough information."
        ),
        input=f"Question:\n{question}\n\nContext:\n{context}",
    )
    return response.output_text
