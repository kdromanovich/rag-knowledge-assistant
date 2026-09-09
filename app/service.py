from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.chunking import chunk_text
from app.config import get_settings
from app.models import Chunk, Document
from app.openai_client import answer_with_context, embed_texts

settings = get_settings()


async def ingest_document(
    session: AsyncSession,
    filename: str,
    content_type: str,
    text: str,
) -> tuple[Document, int]:
    chunks = chunk_text(text, settings.chunk_size_words, settings.chunk_overlap_words)
    if not chunks:
        raise ValueError("Document does not contain extractable text")

    vectors = await embed_texts(chunks)
    document = Document(filename=filename, content_type=content_type)
    session.add(document)
    await session.flush()

    for ordinal, (content, embedding) in enumerate(zip(chunks, vectors, strict=True)):
        session.add(
            Chunk(
                document_id=document.id,
                ordinal=ordinal,
                content=content,
                embedding=embedding,
            )
        )
    await session.commit()
    return document, len(chunks)


async def retrieve(session: AsyncSession, question: str, top_k: int):
    vector = (await embed_texts([question]))[0]
    distance = Chunk.embedding.cosine_distance(vector).label("distance")
    stmt = (
        select(Chunk, Document, distance)
        .join(Document, Document.id == Chunk.document_id)
        .order_by(distance)
        .limit(top_k)
    )
    return (await session.execute(stmt)).all()


async def chat(
    session: AsyncSession,
    question: str,
    top_k: int,
) -> tuple[str, list[dict]]:
    rows = await retrieve(session, question, top_k)
    sources: list[dict] = []
    context_parts: list[str] = []
    for idx, (chunk, document, distance) in enumerate(rows, start=1):
        sid = f"S{idx}"
        context_parts.append(f"[{sid}] {chunk.content}")
        sources.append(
            {
                "source_id": sid,
                "document_id": document.id,
                "filename": document.filename,
                "chunk_ordinal": chunk.ordinal,
                "excerpt": chunk.content[:260],
                "distance": float(distance),
            }
        )
    answer = await answer_with_context(question, "\n\n".join(context_parts))
    return answer, sources
