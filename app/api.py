from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import cache_key, get_cached, redis_client, set_cached
from app.config import get_settings
from app.db import get_session
from app.files import extract_text
from app.schemas import ChatRequest, ChatResponse, IngestResponse
from app.security import require_api_key
from app.service import chat, ingest_document

router = APIRouter()
settings = get_settings()


@router.get("/health")
async def health(session: AsyncSession = Depends(get_session)):
    await session.execute(text("SELECT 1"))
    redis_ok = True
    try:
        await redis_client.ping()
    except RedisError:
        redis_ok = False
    return {"status": "ok", "database": "ok", "redis": "ok" if redis_ok else "degraded"}


@router.post("/v1/documents", response_model=IngestResponse, dependencies=[Depends(require_api_key)])
async def ingest(file: UploadFile = File(...), session: AsyncSession = Depends(get_session)):
    data = await file.read(settings.max_file_bytes + 1)
    if len(data) > settings.max_file_bytes:
        raise HTTPException(status_code=413, detail="File is too large")
    try:
        text_content = extract_text(
            file.filename or "upload",
            file.content_type or "application/octet-stream",
            data,
        )
        document, count = await ingest_document(
            session,
            file.filename or "upload",
            file.content_type or "application/octet-stream",
            text_content,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return IngestResponse(document_id=document.id, filename=document.filename, chunks_created=count)


@router.post("/v1/chat", response_model=ChatResponse, dependencies=[Depends(require_api_key)])
async def ask(payload: ChatRequest, session: AsyncSession = Depends(get_session)):
    top_k = payload.top_k or settings.top_k
    key = cache_key(payload.question, top_k)
    cached = await get_cached(key)
    if cached:
        cached["cached"] = True
        return ChatResponse(**cached)
    try:
        answer, sources = await chat(session, payload.question, top_k)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    result = {"answer": answer, "sources": sources, "cached": False}
    await set_cached(key, result)
    return ChatResponse(**result)
