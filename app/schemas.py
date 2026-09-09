from pydantic import BaseModel, Field


class IngestResponse(BaseModel):
    document_id: str
    filename: str
    chunks_created: int


class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)
    top_k: int | None = Field(default=None, ge=1, le=20)


class Source(BaseModel):
    source_id: str
    document_id: str
    filename: str
    chunk_ordinal: int
    excerpt: str
    distance: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    cached: bool = False
