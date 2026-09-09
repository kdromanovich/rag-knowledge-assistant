def chunk_text(text: str, size_words: int = 260, overlap_words: int = 50) -> list[str]:
    words = text.split()
    if not words:
        return []
    if size_words <= 0:
        raise ValueError("size_words must be positive")
    if overlap_words < 0 or overlap_words >= size_words:
        raise ValueError("overlap_words must be >= 0 and < size_words")

    chunks: list[str] = []
    step = size_words - overlap_words
    for start in range(0, len(words), step):
        part = words[start : start + size_words]
        if part:
            chunks.append(" ".join(part))
        if start + size_words >= len(words):
            break
    return chunks
