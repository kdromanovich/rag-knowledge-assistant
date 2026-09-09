import hashlib
import json
from redis.asyncio import Redis
from app.config import get_settings

settings = get_settings()
redis_client = Redis.from_url(settings.redis_url, decode_responses=True)


def cache_key(question: str, top_k: int) -> str:
    raw = json.dumps({"q": question.strip(), "k": top_k}, sort_keys=True).encode()
    return "rag:answer:" + hashlib.sha256(raw).hexdigest()


async def get_cached(key: str) -> dict | None:
    try:
        value = await redis_client.get(key)
        return json.loads(value) if value else None
    except Exception:
        return None


async def set_cached(key: str, payload: dict) -> None:
    try:
        await redis_client.set(key, json.dumps(payload), ex=settings.cache_ttl_seconds)
    except Exception:
        pass
